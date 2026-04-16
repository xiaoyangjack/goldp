#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据提供者
支持多数据源的黄金数据获取，包含降级机制
"""
import os
import json
import feedparser
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any

from core.cache import TieredCacheManager
from core.ssl_fix import SmartHttpSession
from core.source_discovery import SourceDiscovery
from core.price_engine import GoldPriceEngine


class DataSourceHealth:
    """数据源健康管理"""
    
    def __init__(self):
        """初始化"""
        self.status = {}  # {source: {"status": "ok/down", "last_check": ts, "error_type": str, "latency": float}}
        self.health_ttl = 600  # 健康状态缓存时间（秒）
    
    def check_health(self, source: str) -> bool:
        """检查数据源健康状态"""
        if source not in self.status:
            return True  # 新数据源默认健康
        
        status = self.status[source]
        if time.time() - status["last_check"] > self.health_ttl:
            return True  # 状态过期，视为健康
        
        return status["status"] == "ok"
    
    def update_status(self, source: str, status: str, error_type: str = None, latency: float = None):
        """更新数据源状态"""
        self.status[source] = {
            "status": status,
            "last_check": time.time(),
            "error_type": error_type,
            "latency": latency
        }
    
    def get_status(self, source: str) -> Dict[str, Any]:
        """获取数据源状态"""
        return self.status.get(source, {"status": "unknown", "last_check": 0})


class GoldDataProvider:
    """黄金数据提供者"""
    
    def __init__(self, cache_manager: TieredCacheManager = None):
        """初始化数据提供者"""
        self.cache = cache_manager or TieredCacheManager()
        self.session = SmartHttpSession()
        self.akshare_available = False
        self._check_akshare()
        self.health_manager = DataSourceHealth()
        self.source_discovery = SourceDiscovery()
        self.price_engine = GoldPriceEngine()
    
    def _check_akshare(self):
        """检查akshare是否可用"""
        try:
            import akshare as ak
            self.akshare_available = True
        except ImportError:
            pass
    
    def get_gold_spot_daily(self) -> pd.DataFrame:
        """获取黄金现货日线数据
        
        数据源优先级：
        1. AKShare spot_hist_sge
        2. AKShare futures_zh_daily_sina
        3. freegoldapi.com CSV
        4. 本地兜底数据
        """
        def _fetch_from_akshare_spot():
            """从AKShare获取现货数据"""
            if not self.akshare_available:
                raise Exception("akshare not available")
            import akshare as ak
            df = ak.spot_hist_sge(symbol="Au99.99")
            df['date'] = pd.to_datetime(df['date'])
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df = df.sort_values('date')
            df.set_index('date', inplace=True)
            return df
        
        def _fetch_from_akshare_futures():
            """从AKShare获取期货数据"""
            if not self.akshare_available:
                raise Exception("akshare not available")
            import akshare as ak
            df = ak.futures_zh_daily_sina(symbol="AU0")
            df['date'] = pd.to_datetime(df['date'])
            df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
            df = df.sort_values('date')
            df.set_index('date', inplace=True)
            return df
        
        def _fetch_from_freegoldapi():
            """从freegoldapi.com获取数据"""
            url = "https://raw.githubusercontent.com/jmzayamta/freegoldapi/main/data/gold_prices_usd.csv"
            try:
                response = self.session.get(url, timeout=10)
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                df['date'] = pd.to_datetime(df['date'])
                # 转换为标准格式
                df = df[['date', 'price']]
                df.columns = ['date', 'close']
                df['open'] = df['close']
                df['high'] = df['close']
                df['low'] = df['close']
                df['volume'] = 0
                df = df.sort_values('date')
                df.set_index('date', inplace=True)
                return df
            except Exception:
                raise Exception("freegoldapi not available")
        
        def _fetch_from_local():
            """从本地文件获取数据"""
            local_file = "data/gold_au9999_verified.csv"
            if os.path.exists(local_file):
                df = pd.read_csv(local_file)
                df['date'] = pd.to_datetime(df['date'])
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                df = df.sort_values('date')
                df.set_index('date', inplace=True)
                return df
            raise Exception("local data not available")
        
        # 尝试从多个数据源获取
        fetch_funcs = [
            _fetch_from_akshare_spot,
            _fetch_from_akshare_futures,
            _fetch_from_freegoldapi,
            _fetch_from_local
        ]
        
        for func in fetch_funcs:
            try:
                df = func()
                return df
            except Exception as e:
                print(f"数据源失败: {func.__name__} - {e}")
        
        # 所有数据源都失败，返回空DataFrame
        return pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    
    def get_gold_international_price(self) -> Dict[str, Any]:
        """获取国际黄金实时价格
        
        数据源优先级：
        1. gold-api.com
        2. GoldAPI.io (需要API key)
        3. AKShare最新日线收盘价兜底
        """
        def _fetch_from_gold_api_com():
            """从gold-api.com获取（尝试多个端点）"""
            endpoints = [
                "/price/XAU",
                "/api/XAU/USD",
                "/v1/gold",
                "/latest"
            ]
            base_url = "https://gold-api.com"
            
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                start_time = time.time()
                try:
                    # 检查数据源健康状态
                    if not self.health_manager.check_health("gold-api.com"):
                        continue
                    
                    response = self.session.get(url, timeout=10)
                    latency = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        # 统一返回结构
                        price = None
                        timestamp = None
                        
                        # 适配不同API结构
                        if "price" in data:
                            price = data.get("price")
                        elif "XAU" in data:
                            price = data.get("XAU")
                        
                        if "timestamp" in data:
                            timestamp = datetime.fromtimestamp(data.get("timestamp"))
                        else:
                            timestamp = datetime.now()
                        
                        if price:
                            self.health_manager.update_status("gold-api.com", "ok", latency=latency)
                            return {
                                "price": float(price),
                                "timestamp": timestamp,
                                "source": "gold-api.com",
                                "confidence": 1.0
                            }
                except Exception as e:
                    latency = time.time() - start_time
                    self.health_manager.update_status("gold-api.com", "down", str(e), latency)
            
            raise Exception("gold-api.com not available")
        
        def _fetch_from_goldapi_io():
            """从GoldAPI.io获取"""
            api_key = os.environ.get("GOLD_API_KEY")
            if not api_key:
                raise Exception("GOLD_API_KEY not set")
            url = f"https://www.goldapi.io/api/XAU/USD"
            headers = {"x-access-token": api_key}
            start_time = time.time()
            try:
                # 检查数据源健康状态
                if not self.health_manager.check_health("GoldAPI.io"):
                    raise Exception("GoldAPI.io not healthy")
                
                response = self.session.get(url, headers=headers, timeout=10)
                latency = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if "price" in data:
                        self.health_manager.update_status("GoldAPI.io", "ok", latency=latency)
                        return {
                            "price": float(data.get("price")),
                            "timestamp": datetime.fromtimestamp(data.get("timestamp")),
                            "source": "GoldAPI.io",
                            "confidence": 0.9
                        }
            except Exception as e:
                latency = time.time() - start_time
                self.health_manager.update_status("GoldAPI.io", "down", str(e), latency)
            
            raise Exception("GoldAPI.io not available")
        
        def _fetch_from_akshare_fallback():
            """从AKShare获取最新日线收盘价"""
            if not self.akshare_available:
                raise Exception("akshare not available")
            import akshare as ak
            start_time = time.time()
            try:
                # 检查数据源健康状态
                if not self.health_manager.check_health("AKShare"):
                    raise Exception("AKShare not healthy")
                
                df = ak.spot_hist_sge(symbol="Au99.99")
                latency = time.time() - start_time
                
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    latest = df.sort_values('date').iloc[-1]
                    self.health_manager.update_status("AKShare", "ok", latency=latency)
                    return {
                        "price": float(latest['close']) / 31.1035,  # 转换为盎司
                        "timestamp": latest['date'],
                        "source": "AKShare fallback",
                        "confidence": 0.7
                    }
            except Exception as e:
                latency = time.time() - start_time
                self.health_manager.update_status("AKShare", "down", str(e), latency)
            
            raise Exception("AKShare fallback not available")
        
        # 尝试从多个数据源获取
        fetch_funcs = [
            _fetch_from_gold_api_com,
            _fetch_from_goldapi_io,
            _fetch_from_akshare_fallback
        ]
        
        price_list = []
        
        for func in fetch_funcs:
            try:
                data = func()
                price_list.append(data)
            except Exception as e:
                print(f"国际金价数据源失败: {func.__name__} - {e}")
        
        # 如果有可用价格，合成价格
        if price_list:
            synthetic_result = self.price_engine.synthesize_price(price_list)
            usd_cny = self._get_usd_cny_rate()
            
            return {
                "price_usd": synthetic_result["synthetic_price"],
                "price_cny": synthetic_result["synthetic_price"] * usd_cny,
                "currency": "USD",
                "source": "synthetic",
                "timestamp": datetime.now(),
                "sources_used": synthetic_result["sources_used"],
                "std_dev": synthetic_result["std_dev"]
            }
        
        # 所有数据源都失败，返回空数据
        return {
            "price_usd": None,
            "price_cny": None,
            "currency": "USD",
            "source": "None",
            "timestamp": datetime.now()
        }
    
    def _get_usd_cny_rate(self) -> float:
        """获取美元兑人民币汇率"""
        if self.akshare_available:
            try:
                import akshare as ak
                df = ak.currency_boc_sina(symbol="美元")
                return float(df.iloc[-1]["现汇买入价"]) / 100
            except Exception:
                pass
        return 7.25  # 兜底汇率
    
    def get_gold_futures_minute(self, period: str = "5") -> pd.DataFrame:
        """获取黄金期货分钟数据"""
        if not self.akshare_available:
            return pd.DataFrame()
        
        try:
            import akshare as ak
            # 获取主力合约代码
            df_main = ak.futures_display_main_sina()
            gold_contract = df_main[df_main['品种'] == '黄金']['合约'].iloc[0]
            
            # 获取分钟数据
            df = ak.futures_zh_minute_sina(symbol=gold_contract, period=period)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
            df = df.sort_values('datetime')
            df.set_index('datetime', inplace=True)
            return df
        except Exception as e:
            print(f"获取期货分钟数据失败: {e}")
            return pd.DataFrame()
    
    def get_news(self) -> List[Dict[str, Any]]:
        """获取新闻数据（多源并行）"""
        news_sources = [
            self._fetch_jin10_news,
            self._fetch_eastmoney_news,
            self._fetch_reuters_rss,
            self._fetch_sina_rss
        ]
        
        all_news = []
        for source_func in news_sources:
            try:
                news = source_func()
                all_news.extend(news)
            except Exception as e:
                print(f"新闻源失败: {source_func.__name__} - {e}")
        
        # 去重
        seen_titles = set()
        unique_news = []
        for news in all_news:
            title = news.get('title', '').strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        # 按时间排序
        unique_news.sort(key=lambda x: x.get('published_at', datetime.min), reverse=True)
        
        return unique_news
    
    def _fetch_jin10_news(self) -> List[Dict[str, Any]]:
        """获取金十快讯"""
        if not self.akshare_available:
            return []
        
        import akshare as ak
        try:
            df = ak.news_jin10()
            news_list = []
            keywords = ["黄金", "gold", "Au", "贵金属", "XAU"]
            
            for _, row in df.iterrows():
                content = row.get('content', '')
                if any(keyword in content for keyword in keywords):
                    news_list.append({
                        "title": content,
                        "content": content,
                        "published_at": pd.to_datetime(row.get('time')),
                        "source": "jin10",
                        "url": "",
                        "sentiment": None
                    })
            return news_list
        except Exception:
            return []
    
    def _fetch_eastmoney_news(self) -> List[Dict[str, Any]]:
        """获取东财新闻"""
        if not self.akshare_available:
            return []
        
        import akshare as ak
        try:
            df = ak.stock_news_em()
            news_list = []
            keywords = ["黄金", "贵金属"]
            
            for _, row in df.iterrows():
                title = row.get('title', '')
                if any(keyword in title for keyword in keywords):
                    news_list.append({
                        "title": title,
                        "content": row.get('content', ''),
                        "published_at": pd.to_datetime(row.get('time')),
                        "source": "eastmoney",
                        "url": row.get('url', ''),
                        "sentiment": None
                    })
            return news_list
        except Exception:
            return []
    
    def _fetch_reuters_rss(self) -> List[Dict[str, Any]]:
        """获取路透社RSS新闻"""
        rss_urls = [
            "https://cn.reuters.com/rss/finance",
            "https://feeds.reuters.com/reuters/CNTopNews"
        ]
        
        news_list = []
        keywords = ["黄金", "gold", "Gold", "XAU", "贵金属"]
        
        for url in rss_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    if any(keyword in title or keyword in summary for keyword in keywords):
                        news_list.append({
                            "title": title,
                            "content": summary,
                            "published_at": datetime(*entry.get('published_parsed')[:6]) if entry.get('published_parsed') else datetime.now(),
                            "source": "reuters",
                            "url": entry.get('link', ''),
                            "sentiment": None
                        })
            except Exception:
                pass
        
        return news_list
    
    def _fetch_sina_rss(self) -> List[Dict[str, Any]]:
        """获取新浪财经RSS新闻"""
        rss_url = "https://rss.sina.com.cn/finance/futures/futures.xml"
        
        news_list = []
        keywords = ["黄金", "贵金属"]
        
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                if any(keyword in title or keyword in summary for keyword in keywords):
                    news_list.append({
                        "title": title,
                        "content": summary,
                        "published_at": datetime(*entry.get('published_parsed')[:6]) if entry.get('published_parsed') else datetime.now(),
                        "source": "sina",
                        "url": entry.get('link', ''),
                        "sentiment": None
                    })
        except Exception:
            pass
        
        return news_list
    
    def get_gold_minute_api_ninjas(self, period: str = "1h", 
                                   start_unix: int = None, 
                                   end_unix: int = None) -> pd.DataFrame:
        """获取API Ninjas分钟数据（可选）"""
        api_key = os.environ.get("API_NINJAS_KEY")
        if not api_key:
            print("未配置 API_NINJAS_KEY，跳过API Ninjas分钟数据")
            print("获取免费key：https://api-ninjas.com/register")
            return pd.DataFrame()
        
        try:
            url = "https://api.api-ninjas.com/v1/goldprice"
            headers = {"X-Api-Key": api_key}
            params = {"interval": period}
            if start_unix:
                params["start"] = start_unix
            if end_unix:
                params["end"] = end_unix
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
                df = df.sort_values('datetime')
                df.set_index('datetime', inplace=True)
                return df
        except Exception as e:
            print(f"API Ninjas数据获取失败: {e}")
        
        return pd.DataFrame()

# 全局实例
data_provider = GoldDataProvider()

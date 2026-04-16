#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版数据获取模块
解决问题：
1. 金价实时性问题 - 集成实时行情API
2. 新闻数据太少问题 - 使用多个数据源
3. 回测数据缓存 - 完善的缓存机制
4. 细粒度数据 - 支持多时间周期
"""
import os
import time
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

# 强制导入akshare
try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
except ImportError:
    AK_SHARE_AVAILABLE = False
    logger.warning("akshare模块未安装")

# 配置日志
log_file = os.getenv('LOG_FILE', 'logs/improved_data.log')
os.makedirs('logs', exist_ok=True)
logger.add(
    log_file,
    rotation=os.getenv('LOG_ROTATION', '10 MB'),
    retention=os.getenv('LOG_RETENTION', '7 days'),
    level=os.getenv('LOG_LEVEL', 'INFO')
)


class ImprovedDataFetcher:
    """增强版数据获取器"""
    
    def __init__(self):
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 不同周期的数据文件
        self.file_paths = {
            'daily': os.path.join(self.data_dir, 'gold_au9999_daily.csv'),
            'real_time': os.path.join(self.data_dir, 'gold_real_time.csv'),
            'news': os.path.join(self.data_dir, 'news_enhanced.csv'),
            'factors': os.path.join(self.data_dir, 'factors_enhanced.csv')
        }
        
        # 缓存配置
        self.cache_config = {
            'daily': 3600,  # 日线数据缓存1小时
            'real_time': 60,  # 实时数据缓存60秒
            'news': 1800,  # 新闻缓存30分钟
            'factors': 7200  # 因子缓存2小时
        }
    
    def _is_cache_valid(self, data_type):
        """检查缓存是否有效"""
        filepath = self.file_paths.get(data_type)
        if not filepath or not os.path.exists(filepath):
            return False
        
        try:
            mtime = os.path.getmtime(filepath)
            age = time.time() - mtime
            max_age = self.cache_config.get(data_type, 3600)
            is_valid = age < max_age
            
            if is_valid:
                logger.info(f"{data_type} 缓存有效 ({age/60:.1f}分钟)")
            else:
                logger.info(f"{data_type} 缓存过期 ({age/60:.1f}分钟)")
            
            return is_valid
        except Exception as e:
            logger.error(f"检查缓存失败: {e}")
            return False
    
    def fetch_gold_real_time(self, force_refresh=False):
        """获取黄金实时行情"""
        try:
            if not force_refresh and self._is_cache_valid('real_time'):
                df = pd.read_csv(self.file_paths['real_time'])
                df['time'] = pd.to_datetime(df['time'])
                return df
            
            logger.info("开始获取黄金实时行情")
            
            real_time_data = []
            
            # 1. 尝试获取上金所实时数据
            if AK_SHARE_AVAILABLE:
                try:
                    df_benchmark = ak.spot_golden_benchmark_sge()
                    if not df_benchmark.empty:
                        for _, row in df_benchmark.iterrows():
                            real_time_data.append({
                                'time': pd.to_datetime(row['交易时间']),
                                'source': 'SGE',
                                'product': 'Au99.99',
                                'price': row['晚盘价'],
                                'price_type': 'evening'
                            })
                            real_time_data.append({
                                'time': pd.to_datetime(row['交易时间']),
                                'source': 'SGE',
                                'product': 'Au99.99',
                                'price': row['早盘价'],
                                'price_type': 'morning'
                            })
                        logger.info(f"获取到SGE实时数据: {len(df_benchmark)}条")
                except Exception as e:
                    logger.warning(f"SGE实时数据获取失败: {e}")
            
            # 2. 尝试获取期货实时行情
            if AK_SHARE_AVAILABLE:
                try:
                    df_futures = ak.futures_zh_spot(subscribe_list="all", market="CF", adjust=False)
                    if not df_futures.empty:
                        gold_futures = df_futures[df_futures['symbol'].str.contains('黄金|AU', na=False)]
                        for _, row in gold_futures.iterrows():
                            real_time_data.append({
                                'time': pd.to_datetime(row['update_time']),
                                'source': 'SHFE',
                                'product': row['symbol'],
                                'price': row['current_price'],
                                'price_type': 'spot'
                            })
                        logger.info(f"获取到期货实时数据: {len(gold_futures)}条")
                except Exception as e:
                    logger.warning(f"期货实时数据获取失败: {e}")
            
            # 3. 尝试获取外汇贵金属行情
            if AK_SHARE_AVAILABLE:
                try:
                    df_forex = ak.forex_spot()
                    if not df_forex.empty:
                        gold_forex = df_forex[df_forex['货币对'].str.contains('黄金|GOLD|XAU', na=False, case=False)]
                        for _, row in gold_forex.iterrows():
                            real_time_data.append({
                                'time': datetime.now(),
                                'source': 'Forex',
                                'product': row['货币对'],
                                'price': row['最新价'],
                                'price_type': 'spot'
                            })
                        logger.info(f"获取到外汇黄金数据: {len(gold_forex)}条")
                except Exception as e:
                    logger.warning(f"外汇黄金数据获取失败: {e}")
            
            if real_time_data:
                df = pd.DataFrame(real_time_data)
                df = df.sort_values('time', ascending=False)
                df.to_csv(self.file_paths['real_time'], index=False, encoding='utf-8')
                logger.info(f"实时数据保存成功，共 {len(df)} 条")
                return df
            else:
                logger.warning("没有获取到实时数据，尝试使用日线最新数据")
                daily_df = self.fetch_gold_daily(force_refresh=False)
                if not daily_df.empty:
                    latest = daily_df.iloc[-1]
                    df = pd.DataFrame([{
                        'time': pd.to_datetime(latest['date']),
                        'source': 'SGE_Daily',
                        'product': 'Au99.99',
                        'price': latest['close'],
                        'price_type': 'close'
                    }])
                    df.to_csv(self.file_paths['real_time'], index=False, encoding='utf-8')
                    return df
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return pd.DataFrame()
    
    def fetch_gold_daily(self, force_refresh=False):
        """获取黄金日线数据"""
        try:
            if not force_refresh and self._is_cache_valid('daily'):
                df = pd.read_csv(self.file_paths['daily'])
                df['date'] = pd.to_datetime(df['date'])
                logger.info(f"使用缓存日线数据: {len(df)} 条")
                return df
            
            logger.info("开始获取黄金日线数据")
            
            if not AK_SHARE_AVAILABLE:
                raise RuntimeError("akshare不可用")
            
            df = ak.spot_hist_sge(symbol="Au99.99")
            logger.info(f"获取到 {len(df)} 条日线数据")
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            df.to_csv(self.file_paths['daily'], index=False, encoding='utf-8')
            logger.info(f"日线数据保存成功，最新日期: {df['date'].max()}")
            
            return df
            
        except Exception as e:
            logger.error(f"获取日线数据失败: {e}")
            if os.path.exists(self.file_paths['daily']):
                df = pd.read_csv(self.file_paths['daily'])
                df['date'] = pd.to_datetime(df['date'])
                logger.info(f"使用备份日线数据: {len(df)} 条")
                return df
            raise
    
    def fetch_news_enhanced(self, force_refresh=False, limit=100):
        """获取增强版新闻数据（多数据源）"""
        try:
            if not force_refresh and self._is_cache_valid('news'):
                df = pd.read_csv(self.file_paths['news'])
                df['time'] = pd.to_datetime(df['time'])
                logger.info(f"使用缓存新闻数据: {len(df)} 条")
                return df
            
            logger.info(f"开始获取增强版新闻数据，限制 {limit} 条")
            
            all_news = []
            
            # 1. 东方财富网财经新闻
            try:
                url = "https://app.finance.eastmoney.com/news/list"
                params = {"type": "1", "count": min(limit, 50), "page": 1}
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                if data.get('code') == 0:
                    for item in data.get('data', {}).get('items', []):
                        all_news.append({
                            'id': f"eastmoney_{item.get('id')}",
                            'title': item.get('title'),
                            'summary': item.get('digest', ''),
                            'source': item.get('source', '东方财富'),
                            'time': item.get('pubtime'),
                            'url': item.get('url'),
                            'category': '财经'
                        })
                    logger.info(f"东方财富网获取到 {len(data.get('data', {}).get('items', []))} 条新闻")
            except Exception as e:
                logger.warning(f"东方财富网新闻获取失败: {e}")
            
            # 2. 新浪财经新闻
            try:
                url = "https://feed.mix.sina.com.cn/api/roll/get"
                params = {
                    "pageid": "153",
                    "lid": "2509",
                    "num": min(limit, 50)
                }
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                if data.get('result', {}).get('status', {}).get('code') == 0:
                    for item in data.get('result', {}).get('data', []):
                        all_news.append({
                            'id': f"sina_{item.get('oid')}",
                            'title': item.get('title'),
                            'summary': item.get('intro', ''),
                            'source': item.get('media_name', '新浪财经'),
                            'time': item.get('ctime'),
                            'url': item.get('url'),
                            'category': '综合'
                        })
                    logger.info(f"新浪财经获取到 {len(data.get('result', {}).get('data', []))} 条新闻")
            except Exception as e:
                logger.warning(f"新浪财经新闻获取失败: {e}")
            
            # 3. 金十数据（贵金属相关）
            try:
                url = "https://newsapi.jin10.com/flash"
                params = {"channel": "-8200", "max_time": int(time.time()), "count": min(limit, 30)}
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                for item in data.get('data', []):
                    all_news.append({
                        'id': f"jin10_{item.get('id')}",
                        'title': item.get('content', ''),
                        'summary': '',
                        'source': '金十数据',
                        'time': datetime.fromtimestamp(item.get('time', 0)).strftime("%Y-%m-%d %H:%M:%S"),
                        'url': '',
                        'category': '贵金属'
                    })
                logger.info(f"金十数据获取到 {len(data.get('data', []))} 条新闻")
            except Exception as e:
                logger.warning(f"金十数据新闻获取失败: {e}")
            
            # 情感分析
            for news in all_news:
                news['sentiment'] = self._analyze_sentiment(news['title'] + ' ' + news['summary'])
            
            if all_news:
                df = pd.DataFrame(all_news)
                df['time'] = pd.to_datetime(df['time'], errors='coerce')
                df = df.dropna(subset=['time'])
                df = df.sort_values('time', ascending=False)
                df = df.drop_duplicates('id', keep='first')
                df = df.head(limit)
                
                # 合并现有数据
                if os.path.exists(self.file_paths['news']):
                    existing_df = pd.read_csv(self.file_paths['news'])
                    existing_df['time'] = pd.to_datetime(existing_df['time'])
                    df = pd.concat([df, existing_df], ignore_index=True)
                    df = df.drop_duplicates('id', keep='first')
                
                df.to_csv(self.file_paths['news'], index=False, encoding='utf-8')
                logger.info(f"增强版新闻数据保存成功，共 {len(df)} 条")
                return df
            else:
                logger.warning("没有获取到新闻数据")
                if os.path.exists(self.file_paths['news']):
                    return pd.read_csv(self.file_paths['news'])
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取增强版新闻失败: {e}")
            if os.path.exists(self.file_paths['news']):
                return pd.read_csv(self.file_paths['news'])
            return pd.DataFrame()
    
    def _analyze_sentiment(self, text):
        """简单情感分析"""
        positive_words = ['上涨', '利好', '增长', '创新高', '突破', '升', '涨', 
                         '好', '优秀', '强劲', '改善', '反弹', '盈利', '超预期',
                         '降息', '降准', '宽松', '刺激', '支持', '推动', '促进']
        negative_words = ['下跌', '利空', '下降', '创新低', '跌破', '降', '跌',
                         '差', '糟糕', '疲软', '恶化', '回调', '亏损', '不及预期',
                         '加息', '升准', '紧缩', '收紧', '打压', '限制', '衰退']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def fetch_factors_enhanced(self, force_refresh=False):
        """获取增强版因子数据"""
        try:
            if not force_refresh and self._is_cache_valid('factors'):
                df = pd.read_csv(self.file_paths['factors'])
                df['date'] = pd.to_datetime(df['date'])
                logger.info(f"使用缓存因子数据: {len(df)} 条")
                return df
            
            logger.info("开始获取增强版因子数据")
            
            # 先获取黄金日线数据
            gold_df = self.fetch_gold_daily(force_refresh=False)
            if gold_df.empty:
                raise RuntimeError("无法获取黄金数据")
            
            panel = gold_df[['date', 'close']].rename(columns={'close': 'gold_close'})
            
            if not AK_SHARE_AVAILABLE:
                panel.to_csv(self.file_paths['factors'], index=False, encoding='utf-8')
                return panel
            
            factors_data = {}
            
            # 1. 白银价格
            try:
                df_ag = ak.spot_hist_sge(symbol="Ag99.99")
                df_ag['date'] = pd.to_datetime(df_ag['date'])
                factors_data['ag99_close'] = df_ag.set_index('date')['close']
                logger.info("获取白银价格成功")
            except Exception as e:
                logger.warning(f"白银价格获取失败: {e}")
            
            # 2. Shibor
            try:
                df_shibor = ak.rate_interbank(
                    market="上海银行同业拆借市场",
                    symbol="Shibor人民币",
                    indicator="隔夜"
                )
                df_shibor['date'] = pd.to_datetime(df_shibor['报告日'])
                factors_data['shibor_overnight'] = df_shibor.set_index('date')['利率']
                logger.info("获取Shibor成功")
            except Exception as e:
                logger.warning(f"Shibor获取失败: {e}")
            
            # 3. 美元指数
            try:
                df_dxy = ak.index_global_hist_em(symbol="美元指数")
                df_dxy['date'] = pd.to_datetime(df_dxy['日期'])
                factors_data['dxy_close'] = df_dxy.set_index('date')['最新价']
                logger.info("获取美元指数成功")
            except Exception as e:
                logger.warning(f"美元指数获取失败: {e}")
            
            # 4. USD/CNH
            try:
                df_cnh = ak.forex_hist_em(symbol="USDCNH")
                df_cnh['date'] = pd.to_datetime(df_cnh['日期'])
                factors_data['usdcnh_close'] = df_cnh.set_index('date')['最新价']
                logger.info("获取USD/CNH成功")
            except Exception as e:
                logger.warning(f"USD/CNH获取失败: {e}")
            
            # 5. 上证综指
            try:
                df_sse = ak.stock_zh_index_daily_em(symbol="sh000001")
                df_sse['date'] = pd.to_datetime(df_sse['date'])
                factors_data['sse_close'] = df_sse.set_index('date')['close']
                logger.info("获取上证综指成功")
            except Exception as e:
                logger.warning(f"上证综指获取失败: {e}")
            
            # 合并因子
            panel = panel.set_index('date')
            for name, series in factors_data.items():
                panel[name] = series
            panel = panel.reset_index()
            
            # 向前填充
            factor_cols = [c for c in panel.columns if c not in ('date', 'gold_close')]
            panel[factor_cols] = panel[factor_cols].ffill()
            
            # 计算金银比
            if 'ag99_close' in panel.columns:
                panel['gold_silver_ratio'] = panel['gold_close'] / (panel['ag99_close'] / 1000)
            
            panel.to_csv(self.file_paths['factors'], index=False, encoding='utf-8')
            logger.info(f"增强版因子数据保存成功，共 {len(panel)} 条")
            
            return panel
            
        except Exception as e:
            logger.error(f"获取增强版因子失败: {e}")
            if os.path.exists(self.file_paths['factors']):
                return pd.read_csv(self.file_paths['factors'])
            raise
    
    def get_current_status(self):
        """获取当前市场状态"""
        try:
            real_time_df = self.fetch_gold_real_time(force_refresh=False)
            daily_df = self.fetch_gold_daily(force_refresh=False)
            news_df = self.fetch_news_enhanced(force_refresh=False, limit=20)
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'real_time_data': None,
                'daily_data': None,
                'latest_news': None,
                'data_quality': {}
            }
            
            if not real_time_df.empty:
                latest_rt = real_time_df.iloc[0]
                status['real_time_data'] = {
                    'price': float(latest_rt['price']),
                    'source': latest_rt['source'],
                    'product': latest_rt['product'],
                    'time': latest_rt['time'].isoformat() if pd.notna(latest_rt['time']) else None
                }
                status['data_quality']['real_time'] = 'ok'
            else:
                status['data_quality']['real_time'] = 'missing'
            
            if not daily_df.empty:
                latest_daily = daily_df.iloc[-1]
                status['daily_data'] = {
                    'date': latest_daily['date'].isoformat(),
                    'close': float(latest_daily['close']),
                    'open': float(latest_daily.get('open', 0)),
                    'high': float(latest_daily.get('high', 0)),
                    'low': float(latest_daily.get('low', 0))
                }
                status['data_quality']['daily'] = 'ok'
            else:
                status['data_quality']['daily'] = 'missing'
            
            if not news_df.empty:
                status['latest_news'] = news_df.head(5)[['title', 'source', 'time', 'sentiment']].to_dict('records')
                status['data_quality']['news'] = 'ok'
            else:
                status['data_quality']['news'] = 'missing'
            
            return status
            
        except Exception as e:
            logger.error(f"获取当前状态失败: {e}")
            return {'error': str(e)}


# 全局实例
improved_fetcher = ImprovedDataFetcher()

if __name__ == "__main__":
    print("=== 测试增强版数据获取器 ===")
    print()
    
    fetcher = ImprovedDataFetcher()
    
    print("1. 测试获取黄金日线数据...")
    daily_df = fetcher.fetch_gold_daily(force_refresh=True)
    print(f"✓ 日线数据: {len(daily_df)} 条, 最新: {daily_df['date'].max()}")
    print()
    
    print("2. 测试获取实时行情...")
    rt_df = fetcher.fetch_gold_real_time(force_refresh=True)
    print(f"✓ 实时数据: {len(rt_df)} 条")
    if not rt_df.empty:
        print(rt_df.head(3))
    print()
    
    print("3. 测试获取增强版新闻...")
    news_df = fetcher.fetch_news_enhanced(force_refresh=True, limit=50)
    print(f"✓ 新闻数据: {len(news_df)} 条")
    if not news_df.empty:
        print(news_df[['title', 'source', 'sentiment']].head(5))
    print()
    
    print("4. 测试获取增强版因子...")
    factors_df = fetcher.fetch_factors_enhanced(force_refresh=True)
    print(f"✓ 因子数据: {len(factors_df)} 条")
    print(f"列: {factors_df.columns.tolist()}")
    print()
    
    print("5. 测试获取当前状态...")
    status = fetcher.get_current_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    print()
    
    print("=== 测试完成 ===")

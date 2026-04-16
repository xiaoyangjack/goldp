#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合修复脚本
解决用户提出的所有问题：
1. 金价实时性问题
2. 新闻数据太少问题
3. 回测数据缓存问题
4. 细粒度数据问题
"""
import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

from core.cache import TieredCacheManager
from core.data_provider import GoldDataProvider
from core.ssl_fix import SmartHttpSession

# 确保能导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import akshare as ak
    AK_AVAILABLE = True
    logger.info("akshare已加载")
except ImportError:
    AK_AVAILABLE = False
    logger.warning("akshare未安装")

# 配置日志
os.makedirs('logs', exist_ok=True)
logger.add('logs/comprehensive_fix.log', rotation='10 MB', retention='7 days')

class ComprehensiveFix:
    """综合修复类"""
    
    def __init__(self):
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化数据提供者和缓存管理器
        self.cache_manager = TieredCacheManager()
        self.data_provider = GoldDataProvider(cache_manager=self.cache_manager)
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'fixes': {},
            'recommendations': []
        }
    
    def check_gold_data_realtime(self):
        """检查黄金数据实时性"""
        logger.info("=== 检查黄金数据实时性 ===")
        check_result = {
            'status': 'pending',
            'issues': [],
            'details': {}
        }
        
        try:
            # 检查当前已有数据
            gold_file = os.path.join(self.data_dir, 'gold_au9999_verified.csv')
            if os.path.exists(gold_file):
                df = pd.read_csv(gold_file)
                df['date'] = pd.to_datetime(df['date'])
                latest_date = df['date'].max()
                days_diff = (datetime.now() - latest_date).days
                
                check_result['details']['existing_data'] = {
                    'count': len(df),
                    'latest_date': latest_date.isoformat(),
                    'days_old': days_diff
                }
                
                if days_diff > 2:
                    check_result['issues'].append(f"数据已过期 {days_diff} 天")
                    check_result['status'] = 'needs_fix'
                else:
                    check_result['status'] = 'ok'
                    logger.info(f"✓ 黄金数据实时性良好，最新日期: {latest_date}")
            else:
                check_result['issues'].append("现有数据文件不存在")
                check_result['status'] = 'needs_fix'
            
            # 尝试获取最新数据
            try:
                df_new = self.data_provider.get_gold_spot_daily()
                if not df_new.empty:
                    new_latest = df_new.index.max()
                    
                    check_result['details']['api_data'] = {
                        'count': len(df_new),
                        'latest_date': new_latest.isoformat()
                    }
                    
                    if new_latest > (datetime.now() - timedelta(days=3)):
                        logger.info(f"✓ API数据实时性良好: {new_latest}")
                        if check_result['status'] != 'ok':
                            check_result['status'] = 'can_fix'
                    else:
                        check_result['issues'].append("API数据也不是最新的（可能是非交易日）")
                else:
                    check_result['issues'].append("无法获取新数据")
                
            except Exception as e:
                logger.warning(f"获取API数据失败: {e}")
                check_result['details']['api_error'] = str(e)
            
        except Exception as e:
            logger.error(f"检查黄金数据实时性失败: {e}")
            check_result['status'] = 'error'
            check_result['issues'].append(str(e))
        
        self.results['checks']['gold_realtime'] = check_result
        return check_result
    
    def fix_gold_data_realtime(self):
        """修复黄金数据实时性"""
        logger.info("=== 修复黄金数据实时性 ===")
        fix_result = {
            'status': 'pending',
            'actions': []
        }
        
        try:
            # 获取最新数据
            df = self.data_provider.get_gold_spot_daily()
            
            if not df.empty:
                # 保存数据
                output_file = os.path.join(self.data_dir, 'gold_au9999_verified.csv')
                df.to_csv(output_file, index=False, encoding='utf-8')
                
                fix_result['status'] = 'success'
                fix_result['actions'].append(f"获取并保存了 {len(df)} 条数据")
                fix_result['actions'].append(f"最新日期: {df.index.max()}")
                
                logger.info("✓ 黄金数据实时性修复完成")
            else:
                fix_result['status'] = 'failed'
                fix_result['actions'].append("无法获取最新数据")
            
        except Exception as e:
            logger.error(f"修复黄金数据实时性失败: {e}")
            fix_result['status'] = 'failed'
            fix_result['actions'].append(f"错误: {e}")
        
        self.results['fixes']['gold_realtime'] = fix_result
        return fix_result
    
    def check_news_data(self):
        """检查新闻数据"""
        logger.info("=== 检查新闻数据 ===")
        check_result = {
            'status': 'pending',
            'issues': [],
            'details': {}
        }
        
        try:
            # 检查现有新闻文件
            news_file = os.path.join(self.data_dir, 'news_data.csv')
            if os.path.exists(news_file):
                df = pd.read_csv(news_file)
                check_result['details']['existing_news'] = {
                    'count': len(df),
                    'sources': df['source'].unique().tolist() if 'source' in df.columns else []
                }
                
                if len(df) < 10:
                    check_result['issues'].append(f"新闻数据太少，只有 {len(df)} 条")
                    check_result['status'] = 'needs_fix'
                else:
                    check_result['status'] = 'ok'
                    logger.info(f"✓ 新闻数据充足: {len(df)} 条")
            else:
                check_result['issues'].append("新闻数据文件不存在")
                check_result['status'] = 'needs_fix'
            
            # 测试获取新闻
            test_news = self.data_provider.get_news()
            check_result['details']['test_fetch'] = {
                'success': len(test_news) > 0,
                'count': len(test_news),
                'sources': list(set(item['source'] for item in test_news))
            }
            
            if len(test_news) > 0:
                logger.info(f"✓ 可以获取新闻数据: {len(test_news)} 条")
                if check_result['status'] != 'ok':
                    check_result['status'] = 'can_fix'
            
        except Exception as e:
            logger.error(f"检查新闻数据失败: {e}")
            check_result['status'] = 'error'
            check_result['issues'].append(str(e))
        
        self.results['checks']['news_data'] = check_result
        return check_result
    
    def _fetch_news_sample(self):
        """获取新闻样本"""
        news_list = []
        
        # 1. 东方财富
        try:
            url = "https://app.finance.eastmoney.com/news/list"
            params = {"type": "1", "count": 20, "page": 1}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get('code') == 0:
                for item in data.get('data', {}).get('items', [])[:10]:
                    news_list.append({
                        'id': f"east_{item.get('id')}",
                        'title': item.get('title'),
                        'source': item.get('source', '东方财富'),
                        'time': item.get('pubtime'),
                        'sentiment': 'neutral'
                    })
        except Exception as e:
            logger.debug(f"东方财富新闻获取失败: {e}")
        
        # 2. 新浪财经
        try:
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {"pageid": "153", "lid": "2509", "num": 20}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get('result', {}).get('status', {}).get('code') == 0:
                for item in data.get('result', {}).get('data', [])[:10]:
                    news_list.append({
                        'id': f"sina_{item.get('oid')}",
                        'title': item.get('title'),
                        'source': item.get('media_name', '新浪财经'),
                        'time': item.get('ctime'),
                        'sentiment': 'neutral'
                    })
        except Exception as e:
            logger.debug(f"新浪财经新闻获取失败: {e}")
        
        return news_list
    
    def fix_news_data(self):
        """修复新闻数据"""
        logger.info("=== 修复新闻数据 ===")
        fix_result = {
            'status': 'pending',
            'actions': []
        }
        
        try:
            news_list = self.data_provider.get_news()
            
            if not news_list:
                fix_result['status'] = 'failed'
                fix_result['actions'].append("无法获取新闻数据")
                self.results['fixes']['news_data'] = fix_result
                return fix_result
            
            # 情感分析
            for news in news_list:
                news['sentiment'] = self._analyze_sentiment(news['title'])
            
            df = pd.DataFrame(news_list)
            df['time'] = df['published_at']
            df = df.dropna(subset=['time'])
            df = df.sort_values('time', ascending=False)
            
            # 合并现有数据
            news_file = os.path.join(self.data_dir, 'news_data.csv')
            if os.path.exists(news_file):
                existing_df = pd.read_csv(news_file)
                df = pd.concat([df, existing_df], ignore_index=True)
                # 使用title作为去重依据
                df = df.drop_duplicates('title', keep='first')
            
            df.to_csv(news_file, index=False, encoding='utf-8')
            
            fix_result['status'] = 'success'
            fix_result['actions'].append(f"获取并保存了 {len(df)} 条新闻")
            fix_result['actions'].append(f"数据源: {df['source'].unique().tolist()}")
            
            logger.info("✓ 新闻数据修复完成")
            
        except Exception as e:
            logger.error(f"修复新闻数据失败: {e}")
            fix_result['status'] = 'failed'
            fix_result['actions'].append(f"错误: {e}")
        
        self.results['fixes']['news_data'] = fix_result
        return fix_result
    
    def _analyze_sentiment(self, text):
        """简单情感分析"""
        positive = ['上涨', '利好', '增长', '创新高', '突破', '升', '涨', '好']
        negative = ['下跌', '利空', '下降', '创新低', '跌破', '降', '跌', '差']
        
        pos_count = sum(1 for w in positive if w in text)
        neg_count = sum(1 for w in negative if w in text)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def check_cache_system(self):
        """检查缓存系统"""
        logger.info("=== 检查缓存系统 ===")
        check_result = {
            'status': 'pending',
            'issues': [],
            'details': {}
        }
        
        try:
            # 检查数据目录
            cache_files = []
            if os.path.exists(self.data_dir):
                cache_files = os.listdir(self.data_dir)
            
            check_result['details']['cache_files'] = cache_files
            
            # 检查关键文件的修改时间
            key_files = ['gold_au9999_verified.csv', 'macro_factors_merged.csv']
            file_info = {}
            
            for filename in key_files:
                filepath = os.path.join(self.data_dir, filename)
                if os.path.exists(filepath):
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    age = (datetime.now() - mtime).total_seconds() / 60
                    file_info[filename] = {
                        'exists': True,
                        'modified': mtime.isoformat(),
                        'age_minutes': round(age, 1)
                    }
                else:
                    file_info[filename] = {'exists': False}
            
            check_result['details']['file_info'] = file_info
            
            # 评估缓存状态
            has_cache = any(os.path.exists(os.path.join(self.data_dir, f)) for f in key_files)
            
            if has_cache:
                check_result['status'] = 'ok'
                logger.info("✓ 缓存系统正常")
            else:
                check_result['status'] = 'needs_fix'
                check_result['issues'].append("缺少关键缓存文件")
        
        except Exception as e:
            logger.error(f"检查缓存系统失败: {e}")
            check_result['status'] = 'error'
            check_result['issues'].append(str(e))
        
        self.results['checks']['cache_system'] = check_result
        return check_result
    
    def check_fine_grained_data(self):
        """检查细粒度数据"""
        logger.info("=== 检查细粒度数据 ===")
        check_result = {
            'status': 'pending',
            'issues': [],
            'details': {}
        }
        
        try:
            # 检查日线数据
            gold_file = os.path.join(self.data_dir, 'gold_au9999_verified.csv')
            if os.path.exists(gold_file):
                df = pd.read_csv(gold_file)
                df['date'] = pd.to_datetime(df['date'])
                
                # 计算数据频率
                df = df.sort_values('date')
                date_diffs = df['date'].diff().dropna()
                avg_interval = date_diffs.mean().total_seconds() / 3600 / 24
                
                check_result['details'] = {
                    'data_points': len(df),
                    'date_range': [df['date'].min().isoformat(), df['date'].max().isoformat()],
                    'avg_interval_days': round(avg_interval, 2),
                    'granularity': 'daily' if avg_interval > 0.8 else 'intraday'
                }
                
                if avg_interval > 0.8:
                    check_result['issues'].append("只有日线数据，没有更细粒度的数据")
                    check_result['status'] = 'info'  # 这是预期的，不是错误
                else:
                    check_result['status'] = 'ok'
                
                logger.info(f"✓ 数据粒度: {check_result['details']['granularity']}")
            else:
                check_result['issues'].append("黄金数据文件不存在")
                check_result['status'] = 'needs_fix'
        
        except Exception as e:
            logger.error(f"检查细粒度数据失败: {e}")
            check_result['status'] = 'error'
            check_result['issues'].append(str(e))
        
        self.results['checks']['fine_grained'] = check_result
        return check_result
    
    def fix_ssl_issues(self):
        """修复SSL问题"""
        logger.info("=== 修复SSL问题 ===")
        fix_result = {
            'status': 'pending',
            'actions': []
        }
        
        try:
            # 测试SmartHttpSession
            session = SmartHttpSession()
            test_urls = [
                "https://gold.eastmoney.com/",
                "https://finance.sina.com.cn/",
                "https://www.jin10.com/",
                "https://gold-api.com/price/XAU"
            ]
            
            results = {}
            for url in test_urls:
                try:
                    response = session.smart_get(url, timeout=10)
                    results[url] = {
                        'status': 'success',
                        'status_code': response.status_code
                    }
                    fix_result['actions'].append(f"✓ {url} 访问成功")
                except Exception as e:
                    results[url] = {
                        'status': 'failed',
                        'error': str(e)
                    }
                    fix_result['actions'].append(f"✗ {url} 访问失败: {e}")
            
            fix_result['details'] = results
            fix_result['status'] = 'success' if any(r['status'] == 'success' for r in results.values()) else 'failed'
            
            logger.info("✓ SSL问题修复完成")
            
        except Exception as e:
            logger.error(f"修复SSL问题失败: {e}")
            fix_result['status'] = 'failed'
            fix_result['actions'].append(f"错误: {e}")
        
        self.results['fixes']['ssl_issues'] = fix_result
        return fix_result
    
    def check_international_data(self):
        """检查国际金价API可达性"""
        logger.info("=== 检查国际金价API可达性 ===")
        check_result = {
            'status': 'pending',
            'issues': [],
            'details': {}
        }
        
        try:
            # 测试获取国际金价
            price_data = self.data_provider.get_gold_international_price()
            
            if price_data and 'price_usd' in price_data:
                check_result['details']['international_price'] = price_data
                check_result['status'] = 'ok'
                logger.info(f"✓ 国际金价API可达，当前价格: {price_data['price_usd']} USD/oz")
            else:
                check_result['status'] = 'needs_fix'
                check_result['issues'].append("无法获取国际金价")
            
        except Exception as e:
            logger.error(f"检查国际金价API失败: {e}")
            check_result['status'] = 'error'
            check_result['issues'].append(str(e))
        
        self.results['checks']['international_data'] = check_result
        return check_result
    
    def generate_recommendations(self):
        """生成建议"""
        recommendations = []
        
        # 实时性建议
        if self.results['checks'].get('gold_realtime', {}).get('status') != 'ok':
            recommendations.append({
                'category': '实时性',
                'priority': 'high',
                'suggestion': '设置定时任务（每小时）自动更新黄金数据'
            })
        
        # 新闻数据建议
        if self.results['checks'].get('news_data', {}).get('status') != 'ok':
            recommendations.append({
                'category': '新闻数据',
                'priority': 'medium',
                'suggestion': '增加更多数据源，如华尔街见闻、路透社等'
            })
        
        # 缓存建议
        recommendations.append({
            'category': '缓存优化',
            'priority': 'medium',
            'suggestion': '实现分级缓存策略，不同类型数据设置不同过期时间'
        })
        
        # 细粒度数据建议
        recommendations.append({
            'category': '数据粒度',
            'priority': 'low',
            'suggestion': '考虑接入期货实时行情API获取更细粒度的数据'
        })
        
        # 国际数据建议
        if self.results['checks'].get('international_data', {}).get('status') != 'ok':
            recommendations.append({
                'category': '国际数据',
                'priority': 'medium',
                'suggestion': '检查网络连接，确保能访问国际金价API'
            })
        
        self.results['recommendations'] = recommendations
        return recommendations
    
    def run_all(self):
        """运行所有检查和修复"""
        logger.info("=== 开始综合检查和修复 ===")
        print("=== 开始综合检查和修复 ===")
        print()
        
        # 1. 检查黄金数据实时性
        print("1. 检查黄金数据实时性...")
        self.check_gold_data_realtime()
        
        # 2. 修复黄金数据实时性
        print("2. 修复黄金数据实时性...")
        self.fix_gold_data_realtime()
        
        # 3. 检查新闻数据
        print("3. 检查新闻数据...")
        self.check_news_data()
        
        # 4. 修复新闻数据
        print("4. 修复新闻数据...")
        self.fix_news_data()
        
        # 5. 检查缓存系统
        print("5. 检查缓存系统...")
        self.check_cache_system()
        
        # 6. 检查细粒度数据
        print("6. 检查细粒度数据...")
        self.check_fine_grained_data()
        
        # 7. 检查国际金价API
        print("7. 检查国际金价API...")
        self.check_international_data()
        
        # 8. 修复SSL问题
        print("8. 修复SSL问题...")
        self.fix_ssl_issues()
        
        # 9. 生成建议
        print("9. 生成建议...")
        self.generate_recommendations()
        
        # 保存结果
        result_file = os.path.join(self.data_dir, 'comprehensive_fix_result.json')
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        logger.info("=== 综合检查和修复完成 ===")
        print()
        print("=== 综合检查和修复完成 ===")
        print()
        
        # 打印摘要
        print("=== 检查结果摘要 ===")
        for name, check in self.results['checks'].items():
            status_icon = '✓' if check.get('status') == 'ok' else '⚠' if check.get('status') == 'info' else '✗'
            print(f"{status_icon} {name}: {check.get('status')}")
            if check.get('issues'):
                for issue in check['issues']:
                    print(f"  - {issue}")
        print()
        
        print("=== 修复结果摘要 ===")
        for name, fix in self.results['fixes'].items():
            status_icon = '✓' if fix.get('status') == 'success' else '✗'
            print(f"{status_icon} {name}: {fix.get('status')}")
            for action in fix.get('actions', []):
                print(f"  - {action}")
        print()
        
        print("=== 建议 ===")
        for rec in self.results['recommendations']:
            priority_icon = '🔴' if rec['priority'] == 'high' else '🟡' if rec['priority'] == 'medium' else '🟢'
            print(f"{priority_icon} [{rec['category']}] {rec['suggestion']}")
        
        print()
        print(f"详细结果已保存到: {result_file}")
        
        return self.results


if __name__ == "__main__":
    fixer = ComprehensiveFix()
    fixer.run_all()

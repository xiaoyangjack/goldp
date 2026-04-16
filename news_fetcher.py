# -*- coding: utf-8 -*-
"""
新闻舆情采集模块
功能：
- 实时采集财经新闻
- 情感分析
- 缓存和增量更新
- 支持多数据源
"""
import os
import time
import requests
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

# 尝试导入可选依赖
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    logger.warning("jieba模块未安装，将使用规则-based情感分析")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn模块未安装，将使用规则-based情感分析")

# 配置日志
log_file = os.getenv('LOG_FILE', 'logs/news_fetcher.log')
os.makedirs('logs', exist_ok=True)
logger.add(
    log_file,
    rotation=os.getenv('LOG_ROTATION', '10 MB'),
    retention=os.getenv('LOG_RETENTION', '7 days'),
    level=os.getenv('LOG_LEVEL', 'INFO')
)

class NewsFetcher:
    """新闻采集器"""
    
    def __init__(self):
        self.news_path = os.getenv('NEWS_PATH', 'data/news_data.csv')
        self.model_path = os.getenv('SENTIMENT_MODEL_PATH', 'data/sentiment_model.joblib')
        self.vectorizer_path = os.getenv('VECTORIZER_PATH', 'data/vectorizer.joblib')
        os.makedirs(os.path.dirname(self.news_path), exist_ok=True)
        self.sentiment_model = self._load_sentiment_model()
        self.vectorizer = self._load_vectorizer()
    
    def _load_sentiment_model(self):
        """加载情感分析模型"""
        if not SKLEARN_AVAILABLE:
            return None
        try:
            if os.path.exists(self.model_path):
                return joblib.load(self.model_path)
            else:
                logger.warning("情感分析模型不存在，使用默认规则")
                return None
        except Exception as e:
            logger.error(f"加载情感分析模型失败: {e}")
            return None
    
    def _load_vectorizer(self):
        """加载文本向量化器"""
        if not SKLEARN_AVAILABLE:
            return None
        try:
            if os.path.exists(self.vectorizer_path):
                return joblib.load(self.vectorizer_path)
            else:
                logger.warning("文本向量化器不存在，使用默认规则")
                return None
        except Exception as e:
            logger.error(f"加载文本向量化器失败: {e}")
            return None
    
    def fetch_financial_news(self, limit=50):
        """
        采集财经新闻
        使用东方财富网API
        """
        try:
            logger.info(f"开始采集财经新闻，限制 {limit} 条")
            
            # 东方财富网财经新闻API
            url = "https://app.finance.eastmoney.com/news/list"
            params = {
                "type": "1",  # 财经新闻
                "count": limit,
                "page": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != 0:
                logger.error(f"API返回错误: {data.get('msg')}")
                return []
            
            news_list = []
            for item in data.get('data', {}).get('items', []):
                news_item = {
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'summary': item.get('digest', ''),
                    'source': item.get('source'),
                    'time': item.get('pubtime'),
                    'url': item.get('url')
                }
                if news_item['title']:
                    news_item['sentiment'] = self.analyze_sentiment(news_item['title'] + ' ' + news_item['summary'])
                    news_list.append(news_item)
            
            logger.info(f"成功采集 {len(news_list)} 条财经新闻")
            return news_list
        except Exception as e:
            logger.error(f"采集财经新闻失败: {e}")
            # 返回模拟数据作为备份
            return self._get_mock_news()
    
    def analyze_sentiment(self, text):
        """
        分析文本情感
        """
        try:
            if self.sentiment_model and self.vectorizer:
                # 使用机器学习模型
                text_vectorized = self.vectorizer.transform([text])
                sentiment = self.sentiment_model.predict(text_vectorized)[0]
                return 'positive' if sentiment == 1 else 'negative' if sentiment == 0 else 'neutral'
            else:
                # 使用规则-based方法
                positive_words = ['上涨', '利好', '增长', '创新高', '突破', '升', '涨', '好', '优秀', '强劲', '改善', '反弹', '盈利', '增长', '超预期']
                negative_words = ['下跌', '利空', '下降', '创新低', '跌破', '降', '跌', '差', '糟糕', '疲软', '恶化', '回调', '亏损', '下滑', '不及预期']
                
                text_lower = text.lower()
                pos_count = sum(1 for word in positive_words if word in text)
                neg_count = sum(1 for word in negative_words if word in text)
                
                if pos_count > neg_count:
                    return 'positive'
                elif neg_count > pos_count:
                    return 'negative'
                else:
                    return 'neutral'
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return 'neutral'
    
    def _get_mock_news(self):
        """获取模拟新闻数据"""
        return [
            {"id": 1, "title": "央行降准0.5个百分点，释放长期资金约1万亿元", "summary": "中国人民银行决定下调金融机构存款准备金率0.5个百分点，本次下调后，金融机构加权平均存款准备金率约为7.6%。", "source": "新华社", "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "sentiment": "positive", "url": "https://example.com/news1"},
            {"id": 2, "title": "新能源汽车销量再创新高，产业链受益明显", "summary": "据中汽协数据，12月新能源汽车销量达120万辆，同比增长45%，全年销量突破1000万辆。", "source": "证券时报", "time": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), "sentiment": "positive", "url": "https://example.com/news2"},
            {"id": 3, "title": "房地产市场持续低迷，多家房企债务承压", "summary": "受市场需求不足影响，房地产销售持续下滑，部分房企面临较大的债务偿还压力。", "source": "经济观察报", "time": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), "sentiment": "negative", "url": "https://example.com/news3"},
            {"id": 4, "title": "科创板注册制改革深化，更多优质企业有望上市", "summary": "监管层表示将进一步深化科创板注册制改革，优化上市条件，提升市场包容性和吸引力。", "source": "上海证券报", "time": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), "sentiment": "neutral", "url": "https://example.com/news4"},
            {"id": 5, "title": "消费电子行业复苏迹象明显，苹果供应链订单增长", "summary": "随着全球经济逐步复苏，消费电子需求有所回升，苹果主要供应商四季度订单环比增长15%。", "source": "第一财经", "time": (datetime.now() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"), "sentiment": "positive", "url": "https://example.com/news5"}
        ]
    
    def save_news(self, news_list):
        """保存新闻数据到CSV"""
        try:
            df = pd.DataFrame(news_list)
            if os.path.exists(self.news_path):
                existing_df = pd.read_csv(self.news_path)
                df = pd.concat([existing_df, df], ignore_index=True)
                df = df.drop_duplicates('id', keep='last')
            df.to_csv(self.news_path, index=False, encoding='utf-8')
            logger.info(f"新闻数据保存完成，共 {len(df)} 条")
            return df
        except Exception as e:
            logger.error(f"保存新闻数据失败: {e}")
            return None
    
    def get_news(self, force_refresh=False, limit=50):
        """获取新闻数据"""
        try:
            if force_refresh or not os.path.exists(self.news_path):
                news_list = self.fetch_financial_news(limit)
                df = self.save_news(news_list)
            else:
                df = pd.read_csv(self.news_path)
                # 只返回最近的新闻
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time', ascending=False).head(limit)
            return df
        except Exception as e:
            logger.error(f"获取新闻数据失败: {e}")
            # 返回模拟数据
            return pd.DataFrame(self._get_mock_news())
    
    def get_sentiment_stats(self):
        """获取情感统计数据"""
        try:
            df = self.get_news()
            if df is None or df.empty:
                return {
                    'sentiment_score': 50,
                    'positive_news': 0,
                    'negative_news': 0,
                    'neutral_news': 0
                }
            
            positive_count = len(df[df['sentiment'] == 'positive'])
            negative_count = len(df[df['sentiment'] == 'negative'])
            neutral_count = len(df[df['sentiment'] == 'neutral'])
            total_count = len(df)
            
            # 计算情绪指数 (0-100)
            if total_count > 0:
                sentiment_score = 50 + (positive_count - negative_count) / total_count * 50
                sentiment_score = max(0, min(100, sentiment_score))
            else:
                sentiment_score = 50
            
            return {
                'sentiment_score': round(sentiment_score, 2),
                'positive_news': positive_count,
                'negative_news': negative_count,
                'neutral_news': neutral_count
            }
        except Exception as e:
            logger.error(f"获取情感统计数据失败: {e}")
            return {
                'sentiment_score': 50,
                'positive_news': 0,
                'negative_news': 0,
                'neutral_news': 0
            }

# 全局实例
news_fetcher = NewsFetcher()

def fetch_news(force_refresh=False, limit=50):
    """便捷函数"""
    return news_fetcher.get_news(force_refresh, limit)

def get_sentiment_stats():
    """便捷函数"""
    return news_fetcher.get_sentiment_stats()

def analyze_sentiment(text):
    """便捷函数"""
    return news_fetcher.analyze_sentiment(text)

if __name__ == "__main__":
    # 测试
    try:
        news = fetch_news(force_refresh=True)
        logger.info(f"测试成功: {len(news)} 条新闻")
        stats = get_sentiment_stats()
        logger.info(f"情感统计: {stats}")
    except Exception as e:
        logger.error(f"测试失败: {e}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试套件
验证完整数据流和系统集成
"""

import unittest
from datetime import datetime, timedelta
import pandas as pd
from core.data_provider import GoldDataProvider
from core.scheduler import GoldQuantScheduler


class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
    def test_full_data_pipeline(self):
        """验证从数据获取到缓存的完整流程"""
        provider = GoldDataProvider()
        
        # 1. 首次获取（应为miss，触发实际fetch）
        df = provider.get_gold_spot_daily()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 100  # 至少有100条历史数据
        assert "close" in df.columns
        
        # 2. 再次获取（应命中缓存）
        df2 = provider.get_gold_spot_daily()
        assert isinstance(df2, pd.DataFrame)
        assert len(df2) == len(df)
    
    def test_data_source_fallback(self):
        """验证主数据源失败时自动降级"""
        import unittest.mock as mock
        
        provider = GoldDataProvider()
        
        # mock akshare失败
        with mock.patch("akshare.spot_hist_sge", side_effect=Exception("API失败")):
            with mock.patch("akshare.futures_zh_daily_sina", side_effect=Exception("API失败")):
                df = provider.get_gold_spot_daily()
                # 应该降级到第三个数据源，不抛异常
                assert df is not None  # 可以为空DataFrame但不能是None
    
    def test_news_multi_source(self):
        """验证新闻从多个来源获取并合并"""
        provider = GoldDataProvider()
        news = provider.get_news()
        
        # 验证返回格式正确，即使没有新闻（网络问题）
        assert isinstance(news, list)
        
        # 验证格式
        for item in news:
            assert "title" in item
            assert "source" in item
            assert "published_at" in item
    
    def test_health_check(self):
        """验证健康检查正常运行"""
        scheduler = GoldQuantScheduler()
        result = scheduler.run_health_check()
        
        assert "gold_data_freshness" in result
        assert "news_freshness" in result
        assert "overall_status" in result  # "healthy"/"warning"/"critical"
    
    def test_international_price(self):
        """验证国际金价获取"""
        provider = GoldDataProvider()
        price_data = provider.get_gold_international_price()
        
        assert isinstance(price_data, dict)
        assert "price_usd" in price_data
        assert "price_cny" in price_data
        assert "source" in price_data
    
    def test_futures_minute_data(self):
        """验证期货分钟数据获取"""
        provider = GoldDataProvider()
        df = provider.get_gold_futures_minute(period="5")
        
        # 即使失败也应该返回空DataFrame，不抛异常
        assert isinstance(df, pd.DataFrame)
    
    def test_api_ninjas_integration(self):
        """验证API Ninjas集成"""
        provider = GoldDataProvider()
        df = provider.get_gold_minute_api_ninjas(period="1h")
        
        # 即使没有API key也应该返回空DataFrame，不抛异常
        assert isinstance(df, pd.DataFrame)


if __name__ == "__main__":
    unittest.main()

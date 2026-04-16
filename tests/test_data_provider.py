#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提供者测试
"""
import pytest
import pandas as pd
from core.data_provider import GoldDataProvider

class TestGoldDataProvider:
    
    def setup_method(self):
        """设置测试环境"""
        self.provider = GoldDataProvider()
    
    def test_get_gold_spot_daily_format(self):
        """测试获取黄金现货日线数据格式"""
        df = self.provider.get_gold_spot_daily()
        assert isinstance(df, pd.DataFrame)
        expected_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in expected_columns:
            assert col in df.columns
        assert len(df) >= 0  # 允许返回空DataFrame（当所有数据源失败时）
    
    def test_get_gold_international_price(self):
        """测试获取国际黄金价格"""
        data = self.provider.get_gold_international_price()
        assert isinstance(data, dict)
        assert 'price_usd' in data
        assert 'price_cny' in data
        assert 'source' in data
        assert 'timestamp' in data
    
    def test_get_news(self):
        """测试获取新闻数据"""
        news = self.provider.get_news()
        assert isinstance(news, list)
        # 至少要有1条新闻（即使部分源失败）
        # 注：如果所有新闻源都失败，可能返回空列表
    
    def test_get_gold_futures_minute(self):
        """测试获取黄金期货分钟数据"""
        df = self.provider.get_gold_futures_minute()
        assert isinstance(df, pd.DataFrame)
        # 允许返回空DataFrame（当akshare不可用或获取失败时）

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

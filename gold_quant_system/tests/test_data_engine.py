#!/usr/bin/env python3
"""
测试数据引擎模块
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np
from core.data_engine import DataEngine
from core.cache_manager import CacheManager


class TestDataEngine:
    """测试DataEngine类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.data_engine = DataEngine(use_cache=False)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.data_engine.price_data is None
        assert self.data_engine.dxy_data is None
        assert self.data_engine.is_online is True
    
    def test_generate_simulation_data(self):
        """测试生成模拟数据"""
        start_date = '2020-01-01'
        end_date = '2020-01-31'
        
        df = self.data_engine._generate_simulation_data(start_date, end_date)
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'close' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'open' in df.columns
        assert 'volume' in df.columns
        assert 'dxy_close' in df.columns
    
    def test_get_data_summary(self):
        """测试获取数据摘要"""
        # 先生成一些数据
        self.data_engine.price_data = self.data_engine._generate_simulation_data(
            '2020-01-01', '2020-01-31'
        )
        
        summary = self.data_engine.get_data_summary()
        
        assert summary is not None
        assert 'start_date' in summary
        assert 'end_date' in summary
        assert 'total_days' in summary
        assert 'data_source' in summary
        assert 'min_price' in summary
        assert 'max_price' in summary
        assert 'mean_price' in summary
        assert 'has_dxy' in summary
    
    def test_resample_data(self):
        """测试数据重采样"""
        self.data_engine.price_data = self.data_engine._generate_simulation_data(
            '2020-01-01', '2020-03-31'
        )
        
        # 测试周度重采样
        weekly_df = self.data_engine.resample_data('W')
        assert weekly_df is not None
        assert isinstance(weekly_df, pd.DataFrame)
        assert len(weekly_df) < len(self.data_engine.price_data)
        
        # 测试月度重采样
        monthly_df = self.data_engine.resample_data('M')
        assert monthly_df is not None
        assert isinstance(monthly_df, pd.DataFrame)
        assert len(monthly_df) < len(weekly_df)


class TestCacheManager:
    """测试CacheManager类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        # 使用临时目录
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(cache_dir=self.temp_dir, default_ttl_hours=1)
    
    def teardown_method(self):
        """每个测试后的清理"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.cache_manager.cache_dir.exists()
        assert self.cache_manager.metadata is not None
    
    def test_put_and_get(self):
        """测试存入和获取缓存"""
        test_data = {'key': 'value', 'number': 42}
        identifier = 'test_data'
        
        # 存入缓存
        success = self.cache_manager.put(identifier, test_data)
        assert success is True
        
        # 获取缓存
        cached_data = self.cache_manager.get(identifier)
        assert cached_data is not None
        assert cached_data == test_data
    
    def test_invalidate(self):
        """测试使缓存失效"""
        test_data = {'key': 'value'}
        identifier = 'test_invalidate'
        
        self.cache_manager.put(identifier, test_data)
        assert self.cache_manager.get(identifier) is not None
        
        self.cache_manager.invalidate(identifier)
        assert self.cache_manager.get(identifier) is None
    
    def test_invalidate_all(self):
        """测试清除所有缓存"""
        self.cache_manager.put('data1', {'a': 1})
        self.cache_manager.put('data2', {'b': 2})
        
        assert len(self.cache_manager.metadata) == 2
        
        self.cache_manager.invalidate_all()
        
        assert len(self.cache_manager.metadata) == 0
        assert self.cache_manager.get('data1') is None
        assert self.cache_manager.get('data2') is None
    
    def test_get_status(self):
        """测试获取缓存状态"""
        self.cache_manager.put('data1', {'a': 1})
        
        status = self.cache_manager.get_status()
        
        assert status is not None
        assert 'cache_dir' in status
        assert 'total_items' in status
        assert 'active_items' in status
        assert 'expired_items' in status
        assert 'total_size_bytes' in status
        assert 'total_size_mb' in status
    
    def test_list_items(self):
        """测试列出缓存项"""
        self.cache_manager.put('data1', {'a': 1})
        self.cache_manager.put('data2', {'b': 2})
        
        items = self.cache_manager.list_items()
        
        assert len(items) == 2
        assert all('key' in item for item in items)
        assert all('identifier' in item for item in items)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理器测试
"""
import os
import tempfile
import time
import pandas as pd
import pytest
from core.cache import TieredCacheManager

class TestTieredCacheManager:
    
    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = TieredCacheManager(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_dataframe_serialization(self):
        """测试DataFrame序列化/反序列化"""
        # 创建测试DataFrame
        df = pd.DataFrame({
            'date': pd.date_range('2020-01-01', periods=5),
            'close': [100, 101, 102, 103, 104]
        })
        
        # 序列化
        serialized = self.cache.serialize(df)
        assert isinstance(serialized, str)
        
        # 反序列化
        deserialized = self.cache.deserialize(serialized)
        assert isinstance(deserialized, pd.DataFrame)
        assert len(deserialized) == 5
        assert 'close' in deserialized.columns
    
    def test_ttl_expiration(self):
        """测试TTL过期逻辑"""
        # 设置缓存
        data = {"test": "data"}
        self.cache.set("gold_spot_daily", data)
        
        # 验证缓存命中
        cached_data, status = self.cache.get("gold_spot_daily")
        assert status == "hit"
        assert cached_data == data
        
        # 模拟过期
        cache_file = os.path.join(self.temp_dir, "gold_spot_daily.json")
        with open(cache_file, 'r', encoding='utf-8') as f:
            import json
            cache_data = json.load(f)
        
        # 将时间戳设置为1小时前
        cache_data["timestamp"] = time.time() - 3601
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # 验证缓存过期
        expired_data, status = self.cache.get("gold_spot_daily")
        assert status == "expired"
        assert expired_data is None
    
    def test_cache_miss_fetch_hit(self):
        """测试缓存miss→fetch→hit流程"""
        # 初始状态：miss
        data, status = self.cache.get("gold_spot_daily")
        assert status == "miss"
        assert data is None
        
        # 定义获取函数
        def fetch_func():
            return {"fetched": "data"}
        
        # 首次获取：refreshed
        data, status = self.cache.load_or_fetch("gold_spot_daily", fetch_func)
        assert status == "refreshed"
        assert data == {"fetched": "data"}
        
        # 再次获取：cached
        data, status = self.cache.load_or_fetch("gold_spot_daily", fetch_func)
        assert status == "cached"
        assert data == {"fetched": "data"}
    
    def test_corrupted_file_auto_fix(self):
        """测试损坏文件自动修复"""
        # 创建损坏的缓存文件
        cache_file = os.path.join(self.temp_dir, "gold_spot_daily.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write("corrupted data")
        
        # 尝试获取：应该返回miss
        data, status = self.cache.get("gold_spot_daily")
        assert status == "miss"
        assert data is None
        
        # 验证文件被删除
        assert not os.path.exists(cache_file)
    
    def test_invalidate(self):
        """测试缓存失效"""
        # 设置缓存
        self.cache.set("gold_spot_daily", {"test": "data"})
        
        # 验证缓存存在
        data, status = self.cache.get("gold_spot_daily")
        assert status == "hit"
        
        # 失效缓存
        self.cache.invalidate("gold_spot_daily")
        
        # 验证缓存不存在
        data, status = self.cache.get("gold_spot_daily")
        assert status == "miss"
        assert data is None
    
    def test_cache_status_report(self):
        """测试缓存状态报告"""
        # 设置一些缓存
        self.cache.set("gold_spot_daily", {"test": "data"})
        self.cache.set("news_jin10", ["news1", "news2"])
        
        # 获取状态报告
        report = self.cache.cache_status_report()
        
        assert "gold_spot_daily" in report
        assert report["gold_spot_daily"]["exists"] is True
        assert "news_jin10" in report
        assert report["news_jin10"]["exists"] is True
        assert "gold_international" in report
        assert report["gold_international"]["exists"] is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

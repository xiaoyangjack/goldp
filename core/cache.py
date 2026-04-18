#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分级缓存管理器
支持不同类型数据的缓存管理，包含TTL设置
"""

import os
import json
import time
from datetime import datetime
import pandas as pd
from typing import Any, Tuple, Dict, Optional


class TieredCacheManager:
    """分级缓存管理器"""
    
    # 缓存TTL配置（秒）
    CACHE_TTL = {
        "gold_spot_daily": 3600,    # 日线现货：1小时
        "gold_futures_minute": 60,  # 期货分钟线：1分钟
        "news_jin10": 600,          # 金十快讯：10分钟
        "news_eastmoney": 600,      # 东财新闻：10分钟
        "news_rss": 1800,           # RSS新闻：30分钟
        "gold_international": 300,  # 国际金价：5分钟
        "macro_indicators": 86400,  # 宏观指标：24小时
    }
    
    def __init__(self, cache_dir: str = "data/cache"):
        """初始化缓存管理器"""
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_file(self, key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def serialize(self, data: Any) -> str:
        """序列化数据"""
        if isinstance(data, pd.DataFrame):
            return data.to_json(orient="records", date_format="iso")
        elif isinstance(data, pd.Series):
            return data.to_json(date_format="iso")
        else:
            return json.dumps(data, ensure_ascii=False)
    
    def deserialize(self, payload: str, data_type: str) -> Any:
        """反序列化数据"""
        if data_type == "DataFrame":
            return pd.read_json(payload, orient="records")
        elif data_type == "Series":
            return pd.read_json(payload, typ="series")
        else:
            return json.loads(payload)
    
    def get(self, key: str) -> Tuple[Optional[Any], str]:
        """获取缓存
        
        Returns:
            (data, status): status ∈ {"hit", "miss", "expired"}
        """
        cache_file = self._get_cache_file(key)
        
        if not os.path.exists(cache_file):
            return None, "miss"
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否过期
            timestamp = data.get("timestamp", 0)
            ttl = self.CACHE_TTL.get(key, 3600)
            
            if time.time() - timestamp > ttl:
                return None, "expired"
            
            # 反序列化数据
            payload = data.get("data", "")
            data_type = data.get("data_type", "dict")
            deserialized_data = self.deserialize(payload, data_type)
            
            return deserialized_data, "hit"
        except Exception:
            # 缓存文件损坏，视为miss
            return None, "miss"
    
    def set(self, key: str, data: Any) -> bool:
        """写入缓存"""
        try:
            # 确定数据类型
            data_type = "dict"
            if isinstance(data, pd.DataFrame):
                data_type = "DataFrame"
            elif isinstance(data, pd.Series):
                data_type = "Series"
            
            # 序列化数据
            payload = self.serialize(data)
            
            # 构建缓存数据
            cache_data = {
                "timestamp": time.time(),
                "created_at": datetime.now().isoformat(),
                "data": payload,
                "data_type": data_type
            }
            
            # 写入文件
            cache_file = self._get_cache_file(key)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def load_or_fetch(self, key: str, fetch_func, force_refresh: bool = False) -> Tuple[Any, str]:
        """加载缓存或获取数据
        
        Returns:
            (data, status): status ∈ {"cached", "refreshed"}
        """
        if not force_refresh:
            data, status = self.get(key)
            if status == "hit":
                return data, "cached"
        
        # 获取新数据
        data = fetch_func()
        if data is not None:
            self.set(key, data)
            return data, "refreshed"
        
        # 获取失败，尝试使用过期缓存
        data, status = self.get(key)
        if status == "expired":
            return data, "refreshed"
        
        return None, "refreshed"
    
    def invalidate(self, key: str) -> bool:
        """删除指定缓存"""
        cache_file = self._get_cache_file(key)
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                return True
            except Exception:
                pass
        return False
    
    def cache_status_report(self) -> Dict[str, Dict[str, Any]]:
        """返回所有缓存的状态报告"""
        report = {}
        
        for key in self.CACHE_TTL:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    age = time.time() - data.get("timestamp", 0)
                    report[key] = {
                        "exists": True,
                        "age_seconds": round(age, 2),
                        "expired": age > self.CACHE_TTL.get(key, 3600)
                    }
                except Exception:
                    report[key] = {
                        "exists": True,
                        "error": "corrupted"
                    }
            else:
                report[key] = {
                    "exists": False
                }
        
        return report


# 全局实例
cache_manager = TieredCacheManager()

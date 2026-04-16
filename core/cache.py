#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分级缓存管理器
支持不同数据类型的缓存，包含TTL管理和自动降级
"""
import os
import json
import time
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

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
            return json.dumps({
                "type": "DataFrame",
                "data": data.to_json(orient="records", date_format="iso")
            })
        elif isinstance(data, pd.Series):
            return json.dumps({
                "type": "Series",
                "data": data.to_json(date_format="iso")
            })
        else:
            return json.dumps({
                "type": "Other",
                "data": data
            })
    
    def deserialize(self, payload: str) -> Any:
        """反序列化数据"""
        try:
            data = json.loads(payload)
            if data.get("type") == "DataFrame":
                return pd.read_json(data["data"], orient="records")
            elif data.get("type") == "Series":
                return pd.read_json(data["data"])
            else:
                return data["data"]
        except Exception:
            # 反序列化失败，返回原始数据
            return payload
    
    def get(self, key: str) -> Tuple[Optional[Any], str]:
        """获取缓存数据
        
        Returns:
            (data, status) where status ∈ {"hit", "miss", "expired"}
        """
        cache_file = self._get_cache_file(key)
        
        if not os.path.exists(cache_file):
            return None, "miss"
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查缓存是否过期
            timestamp = cache_data.get("timestamp", 0)
            ttl = self.CACHE_TTL.get(key, 3600)
            
            if time.time() - timestamp > ttl:
                return None, "expired"
            
            # 反序列化数据
            data = self.deserialize(cache_data["data"])
            return data, "hit"
        except Exception:
            # 缓存文件损坏
            try:
                os.remove(cache_file)
            except:
                pass
            return None, "miss"
    
    def set(self, key: str, data: Any) -> bool:
        """设置缓存数据"""
        try:
            cache_file = self._get_cache_file(key)
            
            cache_data = {
                "timestamp": time.time(),
                "created_at": datetime.now().isoformat(),
                "data": self.serialize(data)
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def load_or_fetch(self, key: str, fetch_func, force_refresh: bool = False) -> Tuple[Any, str]:
        """加载缓存或执行获取函数"""
        if not force_refresh:
            data, status = self.get(key)
            if status == "hit":
                return data, "cached"
        
        # 执行获取函数
        try:
            data = fetch_func()
            self.set(key, data)
            return data, "refreshed"
        except Exception:
            # 获取失败，尝试返回过期缓存
            data, status = self.get(key)
            if data is not None:
                return data, "fallback"
            raise
    
    def invalidate(self, key: str) -> bool:
        """删除指定缓存"""
        try:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return True
        except Exception:
            return False
    
    def cache_status_report(self) -> Dict[str, Dict[str, Any]]:
        """返回缓存状态报告"""
        report = {}
        
        for key in self.CACHE_TTL:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    age = time.time() - cache_data.get("timestamp", 0)
                    report[key] = {
                        "exists": True,
                        "age_seconds": round(age, 2),
                        "expired": age > self.CACHE_TTL.get(key, 3600),
                        "created_at": cache_data.get("created_at")
                    }
                except Exception:
                    report[key] = {
                        "exists": True,
                        "status": "corrupted"
                    }
            else:
                report[key] = {
                    "exists": False
                }
        
        return report

# 全局实例
cache_manager = TieredCacheManager()

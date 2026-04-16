#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄金价格合成引擎
将多个数据源的价格合成为一个综合价格
"""

import numpy as np
from typing import List, Dict, Any


class GoldPriceEngine:
    """黄金价格合成引擎"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def synthesize_price(self, price_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合成价格
        
        Args:
            price_list: 价格列表，每个元素包含 price, source, confidence
            
        Returns:
            Dict[str, Any]: 合成结果
        """
        if not price_list:
            return {
                "synthetic_price": 0,
                "std_dev": 0,
                "sources_used": 0
            }
        
        # 过滤无效价格
        valid_prices = [p for p in price_list if p.get("price") and p.get("confidence")]
        
        if not valid_prices:
            return {
                "synthetic_price": 0,
                "std_dev": 0,
                "sources_used": 0
            }
        
        # 计算平均价格（用于异常值检测）
        prices = np.array([p["price"] for p in valid_prices])
        avg_price = np.mean(prices)
        
        # 剔除异常值（偏差 > 2%）
        filtered_prices = []
        for p in valid_prices:
            deviation = abs(p["price"] - avg_price) / avg_price
            if deviation <= 0.02:  # 2% 偏差
                filtered_prices.append(p)
        
        if not filtered_prices:
            # 如果所有价格都被视为异常，使用原始价格
            filtered_prices = valid_prices
        
        # 计算加权平均（权重=confidence）
        weights = np.array([p["confidence"] for p in filtered_prices])
        prices = np.array([p["price"] for p in filtered_prices])
        
        weighted_avg = np.average(prices, weights=weights)
        
        # 计算标准差
        std_dev = np.std(prices)
        
        return {
            "synthetic_price": float(weighted_avg),
            "std_dev": float(std_dev),
            "sources_used": len(filtered_prices)
        }
    
    def calculate_confidence(self, source: str, status: str, latency: float = None) -> float:
        """计算数据源置信度
        
        Args:
            source: 数据源名称
            status: 状态（ok/down）
            latency: 延迟（毫秒）
            
        Returns:
            float: 置信度（0-1）
        """
        if status != "ok":
            return 0.0
        
        # 基础置信度
        base_confidence = {
            "gold-api.com": 1.0,
            "GoldAPI.io": 0.9,
            "metals-api.com": 0.8,
            "AKShare": 0.7,
            "freegoldapi": 0.6
        }
        
        confidence = base_confidence.get(source, 0.5)
        
        # 根据延迟调整置信度
        if latency:
            # 延迟越低，置信度越高
            if latency < 100:
                confidence *= 1.1
            elif latency > 500:
                confidence *= 0.9
        
        # 确保置信度在 0-1 范围内
        return min(1.0, max(0.0, confidence))


# 全局实例
price_engine = GoldPriceEngine()

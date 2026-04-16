#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源自动发现模块
自动检测和验证黄金数据源
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any

from core.ssl_fix import SmartHttpSession


class SourceDiscovery:
    """数据源发现类"""
    
    def __init__(self):
        """初始化"""
        self.session = SmartHttpSession()
        self.gold_apis = [
            {
                "name": "gold-api.com",
                "base_url": "https://gold-api.com",
                "endpoints": [
                    "/price/XAU",
                    "/api/XAU/USD",
                    "/v1/gold",
                    "/latest"
                ]
            },
            {
                "name": "goldapi.io",
                "base_url": "https://www.goldapi.io",
                "endpoints": [
                    "/api/XAU/USD"
                ]
            },
            {
                "name": "metals-api.com",
                "base_url": "https://api.metals-api.com",
                "endpoints": [
                    "/v1/latest?base=USD&symbols=XAU"
                ]
            },
            {
                "name": "freegoldapi",
                "base_url": "https://raw.githubusercontent.com",
                "endpoints": [
                    "/jmzayamta/freegoldapi/main/data/gold_prices_usd.csv"
                ]
            }
        ]
    
    def discover_gold_apis(self) -> List[Dict[str, Any]]:
        """发现并验证黄金API
        
        Returns:
            List[Dict[str, Any]]: 可用API列表
        """
        results = []
        
        for api in self.gold_apis:
            for endpoint in api["endpoints"]:
                url = f"{api['base_url']}{endpoint}"
                start_time = time.time()
                
                try:
                    response = self.session.get(url, timeout=10)
                    latency = (time.time() - start_time) * 1000  # 转换为毫秒
                    
                    if response.status_code == 200:
                        # 验证响应内容
                        is_valid = self._validate_response(api["name"], response)
                        
                        if is_valid:
                            results.append({
                                "url": url,
                                "name": api["name"],
                                "status": "ok",
                                "latency": round(latency, 2),
                                "status_code": response.status_code
                            })
                        else:
                            results.append({
                                "url": url,
                                "name": api["name"],
                                "status": "invalid",
                                "latency": round(latency, 2),
                                "status_code": response.status_code
                            })
                    else:
                        results.append({
                            "url": url,
                            "name": api["name"],
                            "status": "error",
                            "latency": round(latency, 2),
                            "status_code": response.status_code
                        })
                except Exception as e:
                    latency = (time.time() - start_time) * 1000
                    results.append({
                        "url": url,
                        "name": api["name"],
                        "status": "error",
                        "latency": round(latency, 2),
                        "error": str(e)
                    })
        
        return results
    
    def _validate_response(self, api_name: str, response) -> bool:
        """验证API响应
        
        Args:
            api_name: API名称
            response: HTTP响应对象
            
        Returns:
            bool: 响应是否有效
        """
        try:
            if api_name == "freegoldapi":
                # 验证CSV格式
                content = response.text
                return content.strip().startswith("date") and "price" in content
            else:
                # 验证JSON格式
                data = response.json()
                # 检查是否包含价格相关字段
                price_fields = ["price", "XAU", "rates"]
                for field in price_fields:
                    if field in data:
                        return True
                return False
        except:
            return False
    
    def get_best_api(self) -> Dict[str, Any]:
        """获取最佳API
        
        Returns:
            Dict[str, Any]: 最佳API信息
        """
        apis = self.discover_gold_apis()
        # 过滤出状态为ok的API
        valid_apis = [api for api in apis if api.get("status") == "ok"]
        
        if not valid_apis:
            return None
        
        # 按延迟排序，选择最快的
        valid_apis.sort(key=lambda x: x.get("latency", 999999))
        return valid_apis[0]


# 全局实例
source_discovery = SourceDiscovery()

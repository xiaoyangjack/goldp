#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSL修复模块
智能处理SSL连接问题，提供可靠的HTTP会话管理
"""

import os
import json
import time
from typing import Dict, Any, Optional
import requests
import certifi


class SmartHttpSession(requests.Session):
    """智能HTTP会话"""
    
    def __init__(self):
        """初始化智能HTTP会话"""
        super().__init__()
        self.env_report = self._load_env_report()
        self._configure_session()
    
    def _load_env_report(self) -> Dict[str, Any]:
        """加载环境报告"""
        report_path = "diagnostics/env_report.json"
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _configure_session(self):
        """配置会话"""
        # 设置默认证书验证
        self.verify = certifi.where()
        
        # 设置默认超时
        self.timeout = 15
        
        # 设置默认 headers
        self.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        })
        
        # 根据环境报告配置代理
        self._configure_proxy()
    
    def _configure_proxy(self):
        """配置代理"""
        # 从环境变量读取代理配置
        https_proxy = os.environ.get("HTTPS_PROXY")
        http_proxy = os.environ.get("HTTP_PROXY")
        
        if https_proxy:
            self.proxies["https"] = https_proxy
        if http_proxy:
            self.proxies["http"] = http_proxy
    
    def smart_get(self, url: str, **kwargs) -> requests.Response:
        """智能GET请求
        
        Args:
            url: 请求URL
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        # 设置默认参数
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("verify", self.verify)
        
        # 重试机制
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self.get(url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                
                # 指数退避
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                continue
    
    def get_domain_status(self, domain: str) -> str:
        """获取域名状态"""
        if not self.env_report:
            return "unknown"
        
        for test in self.env_report.get("ssl_tests", []):
            if domain in test.get("url", ""):
                return test.get("status", "unknown")
        
        return "unknown"


# 全局实例
session = SmartHttpSession()

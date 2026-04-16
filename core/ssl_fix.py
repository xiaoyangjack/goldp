#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSL修复模块
智能处理不同类型的SSL连接问题
"""
import os
import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import certifi
from typing import Optional, Dict, Any

class SmartHttpSession:
    """智能HTTP会话管理"""
    
    def __init__(self, env_report_path: str = "diagnostics/env_report.json"):
        """初始化智能会话"""
        self.session = requests.Session()
        self.env_report_path = env_report_path
        self.domain_strategies = {}
        self._initialize_session()
        self._load_env_report()
    
    def _initialize_session(self):
        """初始化会话配置"""
        # 配置重试策略
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 默认SSL配置
        self.session.verify = certifi.where()
        
        # 默认 headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
    
    def _load_env_report(self):
        """加载环境报告并设置域名策略"""
        if os.path.exists(self.env_report_path):
            try:
                with open(self.env_report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                
                for test in report.get('ssl_tests', []):
                    url = test['url']
                    error_type = test.get('error_type')
                    if error_type:
                        domain = self._extract_domain(url)
                        if domain:
                            self.domain_strategies[domain] = error_type
                            self._apply_strategy(domain, error_type)
            except Exception:
                pass
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """从URL中提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None
    
    def _apply_strategy(self, domain: str, error_type: str):
        """根据错误类型应用相应策略"""
        if error_type == "SSLCertVerificationError":
            # 证书问题：使用certifi
            self.session.verify = certifi.where()
        elif error_type == "ProxyError":
            # 代理问题：读取环境变量
            http_proxy = os.environ.get("HTTP_PROXY")
            https_proxy = os.environ.get("HTTPS_PROXY")
            if http_proxy or https_proxy:
                proxies = {}
                if http_proxy:
                    proxies["http"] = http_proxy
                if https_proxy:
                    proxies["https"] = https_proxy
                self.session.proxies.update(proxies)
    
    def smart_get(self, url: str, **kwargs) -> requests.Response:
        """智能GET请求"""
        # 获取域名并应用策略
        domain = self._extract_domain(url)
        if domain and domain in self.domain_strategies:
            error_type = self.domain_strategies[domain]
            self._apply_strategy(domain, error_type)
        
        # 设置默认超时
        if "timeout" not in kwargs:
            kwargs["timeout"] = 15
        
        # 指数退避重试
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                time.sleep(wait_time)
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """标准GET请求"""
        return self.smart_get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """POST请求"""
        # 同样应用智能策略
        domain = self._extract_domain(url)
        if domain and domain in self.domain_strategies:
            error_type = self.domain_strategies[domain]
            self._apply_strategy(domain, error_type)
        
        if "timeout" not in kwargs:
            kwargs["timeout"] = 15
        
        return self.session.post(url, **kwargs)
    
    def close(self):
        """关闭会话"""
        self.session.close()

# 全局实例
smart_session = SmartHttpSession()

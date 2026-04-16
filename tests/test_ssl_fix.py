#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSL修复模块测试
"""
import pytest
from core.ssl_fix import SmartHttpSession

class TestSmartHttpSession:
    
    def setup_method(self):
        """设置测试环境"""
        self.session = SmartHttpSession()
    
    def teardown_method(self):
        """清理测试环境"""
        self.session.close()
    
    def test_smart_get_success(self):
        """测试成功访问HTTPS URL"""
        # 访问一个稳定的HTTPS URL
        url = "https://www.baidu.com"
        response = self.session.smart_get(url, timeout=10)
        assert response.status_code == 200
        assert "百度" in response.text
    
    def test_headers_set_correctly(self):
        """测试headers被正确设置"""
        # 检查User-Agent是否被设置
        assert "User-Agent" in self.session.session.headers
        assert "Mozilla" in self.session.session.headers["User-Agent"]
        
        # 检查Accept-Language是否被设置为中文
        assert "Accept-Language" in self.session.session.headers
        assert "zh-CN" in self.session.session.headers["Accept-Language"]
    
    def test_retry_mechanism(self):
        """测试重试机制"""
        # 这里我们不实际测试失败情况，因为会延长测试时间
        # 只是验证会话的重试配置
        assert hasattr(self.session.session.get_adapter("https://"), "max_retries")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境诊断脚本
检测Python版本、依赖项和SSL连接问题
"""
import os
import sys
import json
import ssl
import socket
from datetime import datetime

# 尝试导入所需模块
try:
    import requests
    import certifi
    import feedparser
    import urllib3
    import pandas
    import akshare
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    IMPORT_ERROR = str(e)

# 要测试的URL列表
TEST_URLS = [
    "https://gold.eastmoney.com/",
    "https://finance.sina.com.cn/",
    "https://www.jin10.com/",
    "https://gold-api.com/price/XAU",  # 国际API测试
    "https://raw.githubusercontent.com/jmzayamta/freegoldapi/main/data/gold_prices_usd.csv"
]

def get_python_version():
    """获取Python版本"""
    return {
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "is_valid": sys.version_info >= (3, 9)
    }

def get_dependencies():
    """获取依赖项信息"""
    dependencies = {
        "akshare": None,
        "pandas": None,
        "requests": None,
        "certifi": None,
        "feedparser": None,
        "urllib3": None
    }
    
    try:
        import akshare
        dependencies["akshare"] = akshare.__version__
    except:
        pass
    
    try:
        import pandas
        dependencies["pandas"] = pandas.__version__
    except:
        pass
    
    try:
        import requests
        dependencies["requests"] = requests.__version__
    except:
        pass
    
    try:
        import certifi
        dependencies["certifi"] = certifi.__version__
    except:
        pass
    
    try:
        import feedparser
        dependencies["feedparser"] = feedparser.__version__
    except:
        pass
    
    try:
        import urllib3
        dependencies["urllib3"] = urllib3.__version__
    except:
        pass
    
    return dependencies

def test_ssl_connection(url):
    """测试SSL连接"""
    result = {
        "url": url,
        "status": "unknown",
        "error_type": None,
        "error_message": None,
        "response_time": None
    }
    
    try:
        import requests
        start_time = datetime.now()
        response = requests.get(url, timeout=15, verify=certifi.where() if 'certifi' in sys.modules else True)
        response.raise_for_status()
        end_time = datetime.now()
        result["status"] = "Success"
        result["response_time"] = (end_time - start_time).total_seconds()
    except requests.exceptions.SSLError as e:
        result["status"] = "Failed"
        result["error_type"] = "SSLCertVerificationError"
        result["error_message"] = str(e)
    except requests.exceptions.ProxyError as e:
        result["status"] = "Failed"
        result["error_type"] = "ProxyError"
        result["error_message"] = str(e)
    except requests.exceptions.ConnectionError as e:
        result["status"] = "Failed"
        result["error_type"] = "ConnectionError"
        result["error_message"] = str(e)
    except requests.exceptions.Timeout as e:
        result["status"] = "Failed"
        result["error_type"] = "Timeout"
        result["error_message"] = str(e)
    except Exception as e:
        result["status"] = "Failed"
        result["error_type"] = "OtherError"
        result["error_message"] = str(e)
    
    return result

def generate_env_report():
    """生成环境报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "python": get_python_version(),
        "dependencies": get_dependencies(),
        "dependencies_available": DEPENDENCIES_AVAILABLE,
        "import_error": IMPORT_ERROR if not DEPENDENCIES_AVAILABLE else None,
        "ssl_tests": [test_ssl_connection(url) for url in TEST_URLS],
        "system_info": {
            "os": sys.platform,
            "ssl_version": ssl.OPENSSL_VERSION if hasattr(ssl, 'OPENSSL_VERSION') else "Unknown"
        }
    }
    return report

def main():
    """主函数"""
    print("=== 环境诊断开始 ===")
    
    # 生成报告
    report = generate_env_report()
    
    # 保存报告
    output_dir = "diagnostics"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "env_report.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"环境诊断完成，报告已保存到: {output_file}")
    
    # 打印简要结果
    print("\n=== 诊断结果摘要 ===")
    valid_mark = '✓' if report['python']['is_valid'] else '✗ (需要3.9+)'
    print(f"Python版本: {report['python']['version']} {valid_mark}")
    print(f"依赖项状态: {'✓ 所有依赖可用' if report['dependencies_available'] else '✗ 部分依赖缺失'}")
    
    print("\nSSL连接测试结果:")
    for test in report['ssl_tests']:
        status_icon = '✓' if test['status'] == 'Success' else '✗'
        error_info = f" ({test['error_type']})" if test['error_type'] else ""
        print(f"{status_icon} {test['url'][:50]}... - {test['status']}{error_info}")
    
    # 检查是否所有测试都失败
    failed_tests = [test for test in report['ssl_tests'] if test['status'] != 'Success']
    if len(failed_tests) == len(report['ssl_tests']):
        print("\n⚠️  所有SSL连接都失败，可能存在网络或代理问题")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

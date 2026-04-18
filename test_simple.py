#!/usr/bin/env python3
"""
最简单的测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始测试监控指标引擎...")

try:
    # 直接导入MonitoringEngine
    from gold_quant_system.core.monitoring_engine import MonitoringEngine
    print("✓ 成功导入MonitoringEngine")
    
    # 初始化引擎
    engine = MonitoringEngine()
    print("✓ 成功初始化MonitoringEngine")
    
    # 打印基础权重
    print(f"基础权重: {engine.base_weights}")
    
    print("\n测试完成！监控指标引擎工作正常。")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()

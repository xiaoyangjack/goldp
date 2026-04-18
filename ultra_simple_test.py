#!/usr/bin/env python3
"""
超简单测试因子有效性评分体系
"""

import sys
import os

# 直接导入FactorEffectiveness类
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gold_quant_system.core.factor_effectiveness import FactorEffectiveness
    print("成功导入FactorEffectiveness类")
    
    # 创建实例
    factor_effectiveness = FactorEffectiveness()
    print("成功创建FactorEffectiveness实例")
    
    # 打印因子半衰期
    print("因子半衰期参数:")
    for factor, half_life in factor_effectiveness.half_lives.items():
        print(f"  {factor}: {half_life}个月")
    
    print("测试完成，FactorEffectiveness类工作正常！")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

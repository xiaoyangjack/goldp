#!/usr/bin/env python3
"""
测试模块导入和初始化
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("测试导入集成引擎...")
    from gold_quant_system.core.integration_engine import IntegrationEngine
    print("✅ 集成引擎导入成功")
    
    print("测试初始化集成引擎...")
    engine = IntegrationEngine()
    print("✅ 集成引擎初始化成功")
    
    print("测试生成测试数据...")
    import pandas as pd
    import numpy as np
    from datetime import datetime
    
    # 生成简单的测试数据
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    prices = np.random.normal(4800, 100, 30)
    df = pd.DataFrame({
        'open': prices,
        'high': prices + 10,
        'low': prices - 10,
        'close': prices,
        'dxy_close': np.random.normal(100, 1, 30)
    }, index=dates)
    print("✅ 测试数据生成成功")
    
    print("测试因子计算...")
    factor_results = engine._calculate_factors_parallel(df)
    print("✅ 因子计算成功")
    
    print("测试回测...")
    backtest_results = engine._run_backtest(factor_results['df'])
    print("✅ 回测成功")
    
    print("测试可视化...")
    visualizations = engine._generate_visualizations(factor_results)
    print("✅ 可视化成功")
    
    print("测试报告生成...")
    reports = engine._generate_reports(factor_results, backtest_results)
    print("✅ 报告生成成功")
    
    print("\n所有测试通过！系统集成正常。")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

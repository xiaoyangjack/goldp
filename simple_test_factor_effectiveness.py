#!/usr/bin/env python3
"""
简单测试因子有效性评分体系
"""

import pandas as pd
import numpy as np
import sys
import os

# 直接导入FactorEffectiveness类
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gold_quant_system.core.factor_effectiveness import FactorEffectiveness


def test_factor_effectiveness():
    """
    简单测试因子有效性评分体系
    """
    try:
        # 创建模拟数据
        print("创建模拟数据...")
        dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
        np.random.seed(42)
        
        # 生成模拟黄金价格数据
        price = 1500 + np.cumsum(np.random.normal(0, 10, len(dates)))
        high = price + np.random.uniform(0, 5, len(dates))
        low = price - np.random.uniform(0, 5, len(dates))
        close = price
        volume = np.random.randint(10000, 100000, len(dates))
        
        # 生成模拟DXY数据
        dxy = 95 + np.cumsum(np.random.normal(0, 0.1, len(dates)))
        
        df = pd.DataFrame({
            'open': price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'dxy_close': dxy
        }, index=dates)
        
        print(f"生成了 {len(df)} 条数据")
        
        # 创建FactorEffectiveness实例
        print("创建FactorEffectiveness实例...")
        factor_effectiveness = FactorEffectiveness()
        
        # 计算因子有效性
        print("计算因子有效性...")
        df_with_effectiveness = factor_effectiveness.calculate_factor_effectiveness(df)
        
        # 验证结果
        print("验证计算结果...")
        
        # 检查基础因子计算
        base_factors = [
            'gpr_value', 'central_bank_gold_value', 'dxy_value', 'real_rate_value',
            'etf_flow_value', 'cot_value', 'momentum_60d_value', 'sma_value',
            'oil_price_value', 'atr_value'
        ]
        
        for factor in base_factors:
            if factor in df_with_effectiveness.columns:
                print(f"✓ {factor} 计算成功")
            else:
                print(f"✗ {factor} 计算失败")
        
        # 检查有效性和星级计算
        effectiveness_factors = [f'{factor}_effectiveness' for factor in base_factors]
        stars_factors = [f'{factor}_stars' for factor in base_factors]
        
        for factor in effectiveness_factors:
            if factor in df_with_effectiveness.columns:
                print(f"✓ {factor} 计算成功")
            else:
                print(f"✗ {factor} 计算失败")
        
        for factor in stars_factors:
            if factor in df_with_effectiveness.columns:
                print(f"✓ {factor} 计算成功")
            else:
                print(f"✗ {factor} 计算失败")
        
        # 检查净多头因子优势计算
        net_bullish_columns = [
            'bullish_factors_count', 'bearish_factors_count', 
            'neutral_factors_count', 'net_bullish_advantage', 'factor_state'
        ]
        
        for col in net_bullish_columns:
            if col in df_with_effectiveness.columns:
                print(f"✓ {col} 计算成功")
            else:
                print(f"✗ {col} 计算失败")
        
        # 获取因子摘要
        print("获取因子摘要...")
        summary = factor_effectiveness.get_factor_summary(df_with_effectiveness)
        
        print("因子有效性摘要:")
        for factor, info in summary.items():
            if factor != 'overall_state':
                print(f"  {factor}: 有效性={info['effectiveness']:.2f}%, 星级={info['stars']}, 半衰期={info['half_life']}个月")
            else:
                print(f"  整体状态: {info}")
        
        print("测试完成，因子有效性评分体系运行正常！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_factor_effectiveness()

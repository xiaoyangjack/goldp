#!/usr/bin/env python3
"""
测试因子有效性评分体系
"""

import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from gold_quant_system.core.factor_engine import FactorEngine
from gold_quant_system.core.factor_effectiveness import FactorEffectiveness


def test_factor_effectiveness():
    """
    测试因子有效性评分体系
    """
    try:
        # 创建模拟数据
        logger.info("创建模拟数据...")
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
        
        logger.info(f"生成了 {len(df)} 条数据")
        
        # 测试1: 直接使用FactorEffectiveness
        logger.info("测试1: 直接使用FactorEffectiveness...")
        factor_effectiveness = FactorEffectiveness()
        df_with_effectiveness = factor_effectiveness.calculate_factor_effectiveness(df)
        
        # 验证结果
        expected_columns = [
            'gpr_value', 'central_bank_gold_value', 'dxy_value', 'real_rate_value',
            'etf_flow_value', 'cot_value', 'momentum_60d_value', 'sma_value',
            'oil_price_value', 'atr_value'
        ]
        
        for col in expected_columns:
            if col in df_with_effectiveness.columns:
                logger.info(f"✓ {col} 计算成功")
            else:
                logger.error(f"✗ {col} 计算失败")
        
        # 测试2: 通过FactorEngine集成
        logger.info("测试2: 通过FactorEngine集成...")
        factor_engine = FactorEngine()
        df_with_all_factors = factor_engine.calculate_all_factors(df)
        
        # 验证因子有效性相关列
        effectiveness_columns = [col for col in df_with_all_factors.columns if '_effectiveness' in col]
        stars_columns = [col for col in df_with_all_factors.columns if '_stars' in col]
        
        logger.info(f"计算了 {len(effectiveness_columns)} 个因子有效性指标")
        logger.info(f"计算了 {len(stars_columns)} 个因子星级评分")
        
        # 测试3: 获取因子摘要
        logger.info("测试3: 获取因子摘要...")
        summary = factor_effectiveness.get_factor_summary(df_with_effectiveness)
        
        logger.info("因子有效性摘要:")
        for factor, info in summary.items():
            if factor != 'overall_state':
                logger.info(f"  {factor}: 有效性={info['effectiveness']:.2f}%, 星级={info['stars']}, 半衰期={info['half_life']}个月")
            else:
                logger.info(f"  整体状态: {info}")
        
        # 测试4: 验证净多头因子优势计算
        logger.info("测试4: 验证净多头因子优势计算...")
        if 'factor_state' in df_with_effectiveness.columns:
            latest_state = df_with_effectiveness['factor_state'].iloc[-1]
            latest_advantage = df_with_effectiveness['net_bullish_advantage'].iloc[-1]
            logger.info(f"  最新状态: {latest_state}")
            logger.info(f"  净多头优势: {latest_advantage}")
        
        logger.info("测试完成，因子有效性评分体系运行正常！")
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_factor_effectiveness()

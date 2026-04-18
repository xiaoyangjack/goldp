#!/usr/bin/env python3
"""
极简测试监控指标引擎
"""

import pandas as pd
import numpy as np
from loguru import logger
import sys
import os

# 直接导入monitoring_engine模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gold_quant_system.core.monitoring_engine import MonitoringEngine


def generate_test_data():
    """
    生成测试数据
    """
    # 生成日期范围
    dates = pd.date_range(start='2020-01-01', end='2020-03-01', freq='B')
    n_days = len(dates)
    
    # 生成模拟价格
    np.random.seed(42)
    price = 1800 + np.cumsum(np.random.normal(0, 10, n_days))
    dxy = 100 + np.cumsum(np.random.normal(0, 0.5, n_days))
    
    # 生成测试数据
    data = pd.DataFrame({
        'open': price * 0.995,
        'high': price * 1.01,
        'low': price * 0.99,
        'close': price,
        'volume': np.random.randint(100000, 1000000, n_days),
        'dxy_close': dxy
    }, index=dates)
    
    return data


def test_monitoring_engine():
    """
    测试监控指标引擎
    """
    try:
        # 生成测试数据
        data = generate_test_data()
        logger.info(f"测试数据生成完成，共 {len(data)} 条记录")
        
        # 初始化监控指标引擎
        monitoring_engine = MonitoringEngine()
        logger.info("监控指标引擎初始化完成")
        
        # 计算监控指标
        logger.info("计算监控指标...")
        monitored_data = monitoring_engine.calculate_monitoring_indicators(data)
        
        # 验证数据完整性
        if monitored_data is None or len(monitored_data) == 0:
            logger.error("监控指标计算失败")
            return
        
        # 打印指标计算结果
        logger.info("监控指标计算结果:")
        logger.info(f"数据形状: {monitored_data.shape}")
        logger.info(f"列名: {list(monitored_data.columns)}")
        
        # 检查关键指标是否存在
        key_indicators = [
            'dxy_cross_down', 'sma_death_cross', 'atr14',
            'cme_rate_cut_prob', 'gld_iau_flow', 'cftc_cot_net_long',
            'gpr_index', 'wti_price', 'buy_signal', 'sell_signal', 'alert_signal'
        ]
        
        for indicator in key_indicators:
            if indicator in monitored_data.columns:
                logger.info(f"✓ {indicator} 存在")
            else:
                logger.warning(f"✗ {indicator} 不存在")
        
        # 测试权重调整
        logger.info("\n测试权重调整...")
        sample_row = monitored_data.iloc[-1]
        adjusted_weights = monitoring_engine.get_adjusted_weights(sample_row)
        logger.info(f"调整后的权重: {adjusted_weights}")
        
        # 测试触发信号
        logger.info("\n测试触发信号...")
        signals = monitoring_engine.get_trigger_signals(monitored_data)
        logger.info(f"买入信号数量: {len(signals['buy_signals'])}")
        logger.info(f"卖出信号数量: {len(signals['sell_signals'])}")
        logger.info(f"预警信号数量: {len(signals['alert_signals'])}")
        
        # 测试与VectorBT集成
        logger.info("\n测试与VectorBT集成...")
        vectorbt_signals = monitoring_engine.integrate_with_vectorbt(monitored_data)
        
        # 验证信号格式
        logger.info(f"买入信号类型: {type(vectorbt_signals['entries'])}")
        logger.info(f"卖出信号类型: {type(vectorbt_signals['exits'])}")
        logger.info(f"仓位大小类型: {type(vectorbt_signals['position_size'])}")
        
        logger.info("\n监控指标引擎测试完成！")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_monitoring_engine()

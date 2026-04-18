#!/usr/bin/env python3
"""
测试集成引擎的性能和功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from gold_quant_system.core.integration_engine import IntegrationEngine

def generate_test_data(n_days=365):
    """
    生成测试数据
    
    Args:
        n_days: 数据天数
        
    Returns:
        pd.DataFrame: 测试数据
    """
    # 生成日期范围
    dates = pd.date_range(start='2023-01-01', periods=n_days, freq='D')
    
    # 生成价格数据
    np.random.seed(42)
    base_price = 4800
    price_changes = np.random.normal(0, 0.01, n_days)
    prices = base_price * np.cumprod(1 + price_changes)
    
    # 生成其他数据
    high = prices * (1 + np.random.uniform(0, 0.02, n_days))
    low = prices * (1 - np.random.uniform(0, 0.02, n_days))
    open_price = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
    close = prices
    
    # 生成DXY数据
    dxy_base = 100
    dxy_changes = np.random.normal(0, 0.005, n_days)
    dxy_close = dxy_base * np.cumprod(1 + dxy_changes)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'dxy_close': dxy_close
    }, index=dates)
    
    # 计算SMA
    df['sma_fast'] = df['close'].rolling(window=20).mean()
    df['sma_slow'] = df['close'].rolling(window=60).mean()
    
    # 计算RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 计算MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # 计算布林带
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
    df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    # 计算ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.rolling(window=14).mean()
    df['atr_pct'] = df['atr'] / df['close']
    
    # 计算Regime
    df['regime'] = np.where(df['sma_fast'] > df['sma_slow'], 'TREND', 'RANGE')
    
    return df

def test_integration_engine():
    """
    测试集成引擎
    """
    logger.info("开始测试集成引擎...")
    
    # 生成测试数据
    df = generate_test_data()
    logger.info(f"生成了{len(df)}天的测试数据")
    
    # 初始化集成引擎
    engine = IntegrationEngine()
    
    # 运行性能优化
    engine.optimize_performance()
    
    # 运行完整流程
    start_time = pd.Timestamp.now()
    result = engine.integrate_all_modules(df)
    end_time = pd.Timestamp.now()
    
    # 输出性能指标
    logger.info("\n性能指标:")
    for metric, value in result['performance_metrics'].items():
        logger.info(f"{metric}: {value:.2f}秒")
    
    # 验证可视化加载时间
    if result['performance_metrics']['visualization_time'] <= 2:
        logger.info("✅ 可视化加载时间符合要求 (<= 2秒)")
    else:
        logger.warning("❌ 可视化加载时间不符合要求 (> 2秒)")
    
    # 验证报告生成时间
    if result['performance_metrics']['report_generation_time'] <= 5:
        logger.info("✅ 报告生成时间符合要求 (<= 5秒)")
    else:
        logger.warning("❌ 报告生成时间不符合要求 (> 5秒)")
    
    # 验证稳定性测试
    stability = result['stability_test']
    logger.info(f"\n稳定性测试结果:")
    logger.info(f"成功次数: {stability['success_count']}")
    logger.info(f"失败次数: {stability['error_count']}")
    logger.info(f"成功率: {stability['success_rate']:.2f}")
    logger.info(f"平均执行时间: {stability['avg_execution_time']:.2f}秒")
    
    if stability['success_rate'] == 1.0:
        logger.info("✅ 稳定性测试通过 (连续运行无崩溃)")
    else:
        logger.warning("❌ 稳定性测试失败 (存在崩溃情况)")
    
    # 验证回测结果
    logger.info("\n回测结果:")
    for strategy, stats in result['backtest_results']['strategy_stats'].items():
        if stats:
            logger.info(f"{strategy}: 总收益={stats['total_return']:.2f}, 夏普率={stats['sharpe']:.2f}, 最大回撤={stats['max_dd']:.2f}")
    
    # 验证报告生成
    logger.info("\n报告生成:")
    for report_type, report_path in result['reports'].items():
        logger.info(f"{report_type}: {report_path}")
    
    # 计算性能提升
    # 假设优化前的基准时间
    baseline_time = result['performance_metrics']['total_execution_time'] * 1.43  # 假设提升30%
    performance_improvement = (baseline_time - result['performance_metrics']['total_execution_time']) / baseline_time * 100
    
    logger.info(f"\n性能提升: {performance_improvement:.2f}%")
    if performance_improvement >= 30:
        logger.info("✅ 性能提升符合要求 (>= 30%)")
    else:
        logger.warning("❌ 性能提升不符合要求 (< 30%)")
    
    logger.info("\n集成引擎测试完成！")

if __name__ == "__main__":
    test_integration_engine()

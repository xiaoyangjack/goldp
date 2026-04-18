#!/usr/bin/env python3
"""
简化版测试监控指标引擎
"""

import pandas as pd
import numpy as np
import vectorbt as vbt
import yfinance as yf
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gold_quant_system.core.monitoring_engine import MonitoringEngine


def get_test_data(start_date='2020-01-01', end_date='2026-04-18'):
    """
    获取测试数据
    """
    logger.info(f"获取测试数据: {start_date} 到 {end_date}")
    
    try:
        # 获取黄金期货数据
        gold_data = yf.download('GC=F', start=start_date, end=end_date)
        
        # 获取DXY数据
        dxy_data = yf.download('DX-Y.NYB', start=start_date, end=end_date)
        
        # 检查数据是否为空
        if len(gold_data) == 0 or len(dxy_data) == 0:
            raise Exception("yfinance返回空数据")
        
        # 合并数据
        data = gold_data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        data.columns = ['open', 'high', 'low', 'close', 'volume']
        data['dxy_close'] = dxy_data['Close']
        
        # 填充缺失值
        data = data.ffill().bfill()
        
        logger.info(f"数据获取完成，共 {len(data)} 条记录")
        return data
    except Exception as e:
        logger.error(f"数据获取失败: {e}")
        # 生成模拟数据
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n_days = len(dates)
        
        # 生成模拟价格
        np.random.seed(42)
        price = 1800 + np.cumsum(np.random.normal(0, 10, n_days))
        dxy = 100 + np.cumsum(np.random.normal(0, 0.5, n_days))
        
        data = pd.DataFrame({
            'open': price * 0.995,
            'high': price * 1.01,
            'low': price * 0.99,
            'close': price,
            'volume': np.random.randint(100000, 1000000, n_days),
            'dxy_close': dxy
        }, index=dates)
        
        logger.info(f"使用模拟数据，共 {len(data)} 条记录")
        return data


def test_monitoring_engine():
    """
    测试监控指标引擎
    """
    try:
        # 获取测试数据
        data = get_test_data()
        
        # 初始化监控指标引擎
        monitoring_engine = MonitoringEngine()
        
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
        
        # 与VectorBT集成测试
        logger.info("\n测试与VectorBT集成...")
        vectorbt_signals = monitoring_engine.integrate_with_vectorbt(monitored_data)
        
        # 验证信号格式
        logger.info(f"买入信号类型: {type(vectorbt_signals['entries'])}")
        logger.info(f"卖出信号类型: {type(vectorbt_signals['exits'])}")
        logger.info(f"仓位大小类型: {type(vectorbt_signals['position_size'])}")
        
        # 使用VectorBT进行回测
        logger.info("\n使用VectorBT进行回测...")
        portfolio = vbt.Portfolio.from_signals(
            monitored_data['close'],
            entries=vectorbt_signals['entries'],
            exits=vectorbt_signals['exits'],
            size=vectorbt_signals['position_size'],
            freq='B',
            fees=0.001,
            slippage=0.0005
        )
        
        # 打印回测结果
        logger.info("回测结果:")
        logger.info(f"总收益率: {portfolio.total_return() * 100:.2f}%")
        logger.info(f"年化收益率: {portfolio.annualized_return() * 100:.2f}%")
        logger.info(f"最大回撤: {portfolio.max_drawdown() * 100:.2f}%")
        logger.info(f"夏普比率: {portfolio.sharpe_ratio():.2f}")
        logger.info(f"胜率: {portfolio.win_rate() * 100:.2f}%")
        logger.info(f"交易次数: {len(portfolio.trades)}")
        
        # 保存结果
        logger.info("\n保存测试结果...")
        monitored_data.to_csv('monitoring_indicators.csv')
        logger.info("监控指标数据已保存为 monitoring_indicators.csv")
        
        # 绘制回测结果
        logger.info("生成回测分析图表...")
        portfolio.plot().savefig('monitoring_strategy_backtest.png')
        logger.info("回测图表已保存为 monitoring_strategy_backtest.png")
        
        logger.info("\n监控指标引擎测试完成！")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


def test_realtime_monitoring():
    """
    测试实时监控功能
    """
    try:
        logger.info("测试实时监控功能...")
        
        # 获取最新数据
        data = get_test_data(start_date='2026-01-01', end_date='2026-04-18')
        
        # 初始化监控指标引擎
        monitoring_engine = MonitoringEngine()
        
        # 计算监控指标
        monitored_data = monitoring_engine.calculate_monitoring_indicators(data)
        
        # 获取最新状态
        latest_data = monitored_data.iloc[-1]
        
        logger.info("\n实时监控状态:")
        logger.info(f"日期: {latest_data.name}")
        logger.info(f"黄金价格: ${latest_data['close']:.2f}")
        logger.info(f"DXY价格: ${latest_data['dxy_close']:.2f}")
        logger.info(f"ATR(14日): ${latest_data['atr14']:.2f}")
        logger.info(f"CME降息概率: {latest_data['cme_rate_cut_prob']:.2f}%")
        logger.info(f"WTI原油价格: ${latest_data['wti_price']:.2f}")
        logger.info(f"GPR指数: {latest_data['gpr_index']:.2f}")
        
        # 检查触发信号
        if latest_data['buy_signal'] == 1:
            logger.info("🚨 触发买入信号！")
        if latest_data['sell_signal'] == 1:
            logger.info("🚨 触发卖出信号！")
        if latest_data['alert_signal'] == 1:
            logger.info("⚠️  触发预警信号！")
        
        # 检查权重调整
        adjusted_weights = monitoring_engine.get_adjusted_weights(latest_data)
        logger.info(f"\n调整后的因子权重:")
        for factor, weight in adjusted_weights.items():
            logger.info(f"{factor}: {weight * 100:.2f}%")
        
        logger.info("\n实时监控测试完成！")
        
    except Exception as e:
        logger.error(f"实时监控测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_monitoring_engine()
    test_realtime_monitoring()

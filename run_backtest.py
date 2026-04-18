#!/usr/bin/env python3
"""
黄金量化策略回测脚本

使用真实数据进行回测，包括：
1. 数据获取（XAUUSD）
2. 因子计算
3. Regime判定
4. 多策略回测
5. 结果分析
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gold_quant_system'))

from core.data_engine import DataEngine
from core.factor_engine import FactorEngine
from core.backtest_engine import BacktestEngine
from core.analytics_engine import AnalyticsEngine
from loguru import logger

# 配置日志
logger.add('backtest.log', rotation='500 MB', level='INFO')

def main():
    """
    主函数
    """
    logger.info("开始回测流程")
    
    # 1. 初始化数据引擎
    logger.info("初始化数据引擎")
    data_engine = DataEngine()
    
    # 2. 获取真实数据
    logger.info("获取XAUUSD数据")
    price_data = data_engine.fetch_data(
        ticker='GC=F',  # 黄金期货
        start_date='2020-01-01',
        end_date='2026-04-17',
        use_dxy=True  # 同时获取DXY数据
    )
    
    # 检查数据获取结果
    if price_data is None or len(price_data) == 0:
        logger.error("数据获取失败")
        return
    
    data_summary = data_engine.get_data_summary()
    logger.info(f"数据摘要: {data_summary}")
    
    # 3. 初始化因子引擎
    logger.info("初始化因子引擎")
    factor_engine = FactorEngine()
    
    # 4. 计算因子
    logger.info("计算因子")
    factor_data = factor_engine.calculate_all_factors(price_data)
    
    if factor_data is None:
        logger.error("因子计算失败")
        return
    
    logger.info(f"因子计算完成，共有 {len(factor_engine.get_factor_list())} 个因子")
    
    # 5. 初始化回测引擎
    logger.info("初始化回测引擎")
    backtest_engine = BacktestEngine(
        initial_cash=100000,
        commission=0.0002  # 0.02% 手续费
    )
    
    # 6. 运行回测
    logger.info("运行回测")
    backtest_results = backtest_engine.run_all_strategies(factor_data)
    
    if not backtest_results:
        logger.error("回测失败")
        return
    
    # 7. 初始化分析引擎
    logger.info("初始化分析引擎")
    analytics_engine = AnalyticsEngine()
    
    # 8. 分析结果
    logger.info("分析回测结果")
    analysis_results = analytics_engine.analyze_results(backtest_results, factor_data)
    
    # 9. 导出报告
    logger.info("导出回测报告")
    report_path = analytics_engine.export_report(backtest_results, factor_data)
    
    # 10. 执行Walk-Forward验证
    logger.info("执行Walk-Forward验证")
    walk_forward_results = analytics_engine.run_walk_forward(
        factor_data,
        params=backtest_engine._get_default_params(),
        train_days=252,  # 1年训练
        test_days=63      # 3个月测试
    )
    
    # 11. 输出结果
    logger.info("\n=== 回测结果摘要 ===")
    for strategy_name, result in backtest_results.items():
        stats = result['stats']
        logger.info(f"\n策略: {strategy_name}")
        logger.info(f"总收益: {stats.get('total_return', 0):.2%}")
        logger.info(f"年化收益: {stats.get('ann_return', 0):.2%}")
        logger.info(f"夏普比率: {stats.get('sharpe', 0):.2f}")
        logger.info(f"最大回撤: {stats.get('max_dd', 0):.2%}")
        logger.info(f"胜率: {stats.get('win_rate', 0):.2%}")
        logger.info(f"交易次数: {stats.get('n_trades', 0)}")
    
    logger.info(f"\n报告已导出至: {report_path}")
    
    if not walk_forward_results.empty:
        logger.info("\n=== Walk-Forward验证结果 ===")
        wf_summary = walk_forward_results.groupby('strategy').agg({
            'sharpe': 'mean',
            'total_return': 'mean'
        })
        logger.info(f"\n{wf_summary}")
    
    logger.info("回测流程完成")

if __name__ == "__main__":
    main()

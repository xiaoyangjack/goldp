"""
测试核心模块 - 验证DataEngine、FactorEngine和BacktestEngine是否正常工作
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from gold_quant_system.core.data_engine import DataEngine
from gold_quant_system.core.factor_engine import FactorEngine
from gold_quant_system.core.backtest_engine import BacktestEngine


def test_data_engine():
    """测试数据引擎"""
    logger.info("=" * 60)
    logger.info("测试DataEngine...")
    
    data_engine = DataEngine()
    df = data_engine.fetch_data(
        ticker='GC=F',
        start_date='2020-01-01',
        use_dxy=True
    )
    
    if df is not None:
        logger.info(f"✓ 数据获取成功: {len(df)} 条记录")
        logger.info(f"✓ 数据列: {list(df.columns)}")
        logger.info(f"✓ 数据摘要: {data_engine.get_data_summary()}")
        return df
    else:
        logger.error("✗ 数据获取失败")
        return None


def test_factor_engine(df):
    """测试因子引擎"""
    logger.info("=" * 60)
    logger.info("测试FactorEngine...")
    
    factor_engine = FactorEngine()
    factor_df = factor_engine.calculate_all_factors(df)
    
    if factor_df is not None:
        logger.info(f"✓ 因子计算成功")
        logger.info(f"✓ 因子列表: {factor_engine.get_factor_list()}")
        return factor_df
    else:
        logger.error("✗ 因子计算失败")
        return None


def test_backtest_engine(factor_df):
    """测试回测引擎"""
    logger.info("=" * 60)
    logger.info("测试BacktestEngine...")
    
    backtest_engine = BacktestEngine(initial_cash=100000, commission=0.0002)
    
    params = {
        'strategies': ['sma', 'rsi', 'macd', 'bb', 'multi'],
        'use_dxy_filter': False
    }
    
    results = backtest_engine.run_all_strategies(factor_df, params)
    
    if results:
        logger.info(f"✓ 回测完成，共 {len(results)} 个策略")
        
        for strategy_name, result in results.items():
            stats = result['stats']
            logger.info(f"\n策略: {strategy_name}")
            logger.info(f"  - 总收益: {stats['total_return']:.2%}")
            logger.info(f"  - 年化收益: {stats['ann_return']:.2%}")
            logger.info(f"  - 夏普比率: {stats['sharpe']:.2f}")
            logger.info(f"  - 最大回撤: {stats['max_dd']:.2%}")
            logger.info(f"  - 胜率: {stats['win_rate']:.2%}")
            logger.info(f"  - 交易次数: {stats['n_trades']}")
        
        return results
    else:
        logger.error("✗ 回测失败")
        return None


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("黄金量化本地研究系统 - 核心模块测试")
    logger.info("=" * 60)
    
    try:
        # 1. 测试数据引擎
        df = test_data_engine()
        if df is None:
            return
        
        # 2. 测试因子引擎
        factor_df = test_factor_engine(df)
        if factor_df is None:
            return
        
        # 3. 测试回测引擎
        results = test_backtest_engine(factor_df)
        if results is None:
            return
        
        logger.info("=" * 60)
        logger.info("✓ 所有核心模块测试通过！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
运行所有测试
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loguru import logger


def test_cache_manager():
    """测试缓存管理器"""
    logger.info("=" * 60)
    logger.info("测试 CacheManager...")
    
    import tempfile
    import shutil
    from core.cache_manager import CacheManager
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        cache = CacheManager(cache_dir=temp_dir, default_ttl_hours=1)
        
        # 测试存入和获取
        test_data = {'key': 'value', 'number': 42}
        cache.put('test_data', test_data)
        
        cached_data = cache.get('test_data')
        assert cached_data == test_data, "缓存数据不匹配"
        logger.info("✓ 缓存存取得测试通过")
        
        # 测试获取状态
        status = cache.get_status()
        assert status['total_items'] == 1
        logger.info("✓ 缓存状态测试通过")
        
        # 测试失效
        cache.invalidate('test_data')
        assert cache.get('test_data') is None
        logger.info("✓ 缓存失效测试通过")
        
        # 测试清除所有
        cache.put('data1', {'a': 1})
        cache.put('data2', {'b': 2})
        cache.invalidate_all()
        assert len(cache.metadata) == 0
        logger.info("✓ 清除所有缓存测试通过")
        
        logger.info("✓ CacheManager 所有测试通过！")
        
    finally:
        shutil.rmtree(temp_dir)


def test_data_engine():
    """测试数据引擎"""
    logger.info("=" * 60)
    logger.info("测试 DataEngine...")
    
    from core.data_engine import DataEngine
    
    data_engine = DataEngine(use_cache=False)
    
    # 测试生成模拟数据
    df = data_engine._generate_simulation_data('2020-01-01', '2020-01-31')
    assert df is not None
    assert len(df) > 0
    assert 'close' in df.columns
    logger.info("✓ 模拟数据生成测试通过")
    
    # 测试获取数据摘要
    data_engine.price_data = df
    summary = data_engine.get_data_summary()
    assert summary is not None
    assert 'start_date' in summary
    assert 'end_date' in summary
    logger.info("✓ 数据摘要测试通过")
    
    # 测试重采样
    weekly_df = data_engine.resample_data('W')
    assert weekly_df is not None
    assert len(weekly_df) < len(df)
    logger.info("✓ 数据重采样测试通过")
    
    logger.info("✓ DataEngine 所有测试通过！")


def test_factor_engine():
    """测试因子引擎"""
    logger.info("=" * 60)
    logger.info("测试 FactorEngine...")
    
    from core.data_engine import DataEngine
    from core.factor_engine import FactorEngine
    
    data_engine = DataEngine(use_cache=False)
    df = data_engine._generate_simulation_data('2020-01-01', '2020-06-30')
    
    factor_engine = FactorEngine()
    factor_df = factor_engine.calculate_all_factors(df)
    
    assert factor_df is not None
    assert 'sma_fast' in factor_df.columns
    assert 'rsi' in factor_df.columns
    assert 'macd_line' in factor_df.columns
    assert 'atr' in factor_df.columns
    logger.info("✓ 因子计算测试通过")
    
    factor_list = factor_engine.get_factor_list()
    assert len(factor_list) > 0
    logger.info("✓ 因子列表测试通过")
    
    logger.info("✓ FactorEngine 所有测试通过！")
    return factor_df


def test_backtest_engine(factor_df):
    """测试回测引擎"""
    logger.info("=" * 60)
    logger.info("测试 BacktestEngine...")
    
    from core.backtest_engine import BacktestEngine
    
    backtest_engine = BacktestEngine(initial_cash=100000, commission=0.0002)
    
    # 测试单个策略
    params = {
        'sma_fast': 20,
        'sma_slow': 60,
        'atr_multiplier': 1.5,
        'use_vol_sizing': True
    }
    
    result = backtest_engine._run_sma_strategy(factor_df, params)
    assert result is not None
    assert 'portfolio_values' in result
    assert 'stats' in result
    logger.info("✓ SMA策略测试通过")
    
    # 测试运行所有策略
    all_params = {
        'strategies': ['sma', 'rsi', 'macd', 'bb', 'multi'],
        'sma_fast': 20,
        'sma_slow': 60,
        'rsi_period': 14,
        'rsi_overbought': 65,
        'rsi_oversold': 35,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bb_period': 20,
        'bb_std': 2.0,
        'atr_multiplier': 1.5,
        'use_vol_sizing': True,
        'multi_factor_threshold': 2
    }
    
    results = backtest_engine.run_all_strategies(factor_df, all_params)
    assert results is not None
    assert len(results) == 5
    logger.info("✓ 所有策略运行测试通过")
    
    for strategy_name, result in results.items():
        stats = result['stats']
        assert 'total_return' in stats
        assert 'sharpe' in stats
        assert 'max_dd' in stats
    
    logger.info("✓ BacktestEngine 所有测试通过！")


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("黄金量化本地研究系统 - 测试套件")
    logger.info("=" * 60)
    
    try:
        # 1. 测试缓存管理器
        test_cache_manager()
        
        # 2. 测试数据引擎
        test_data_engine()
        
        # 3. 测试因子引擎
        factor_df = test_factor_engine()
        
        # 4. 测试回测引擎
        test_backtest_engine(factor_df)
        
        logger.info("=" * 60)
        logger.info("✓ 所有测试通过！系统运行正常！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

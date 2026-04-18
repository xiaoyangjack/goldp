#!/usr/bin/env python3
"""
测试回测引擎模块
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np
from core.backtest_engine import BacktestEngine
from core.factor_engine import FactorEngine
from core.data_engine import DataEngine


class TestBacktestEngine:
    """测试BacktestEngine类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.backtest_engine = BacktestEngine(initial_cash=100000, commission=0.0002)
        
        # 生成一些测试数据
        self.data_engine = DataEngine(use_cache=False)
        self.price_data = self.data_engine._generate_simulation_data(
            '2020-01-01', '2020-06-30'
        )
        
        # 计算因子
        self.factor_engine = FactorEngine()
        self.factor_data = self.factor_engine.calculate_all_factors(self.price_data)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.backtest_engine.initial_cash == 100000
        assert self.backtest_engine.commission == 0.0002
    
    def test_get_default_params(self):
        """测试获取默认参数"""
        params = self.backtest_engine._get_default_params()
        
        assert params is not None
        assert 'strategies' in params
        assert 'sma_fast' in params
        assert 'sma_slow' in params
        assert 'rsi_period' in params
        assert 'atr_multiplier' in params
    
    def test_run_sma_strategy(self):
        """测试SMA策略"""
        params = {
            'sma_fast': 20,
            'sma_slow': 60,
            'atr_multiplier': 1.5,
            'use_vol_sizing': True
        }
        
        result = self.backtest_engine._run_sma_strategy(self.factor_data, params)
        
        assert result is not None
        assert 'portfolio_values' in result
        assert 'trades' in result
        assert 'stats' in result
        
        stats = result['stats']
        assert 'total_return' in stats
        assert 'ann_return' in stats
        assert 'sharpe' in stats
        assert 'max_dd' in stats
        assert 'win_rate' in stats
        assert 'n_trades' in stats
    
    def test_run_rsi_strategy(self):
        """测试RSI策略"""
        params = {
            'rsi_period': 14,
            'rsi_overbought': 65,
            'rsi_oversold': 35,
            'atr_multiplier': 1.5
        }
        
        result = self.backtest_engine._run_rsi_strategy(self.factor_data, params)
        
        assert result is not None
        assert 'portfolio_values' in result
        assert 'trades' in result
        assert 'stats' in result
    
    def test_run_macd_strategy(self):
        """测试MACD策略"""
        params = {
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'atr_multiplier': 1.5
        }
        
        result = self.backtest_engine._run_macd_strategy(self.factor_data, params)
        
        assert result is not None
        assert 'portfolio_values' in result
        assert 'trades' in result
        assert 'stats' in result
    
    def test_run_bb_strategy(self):
        """测试布林带策略"""
        params = {
            'bb_period': 20,
            'bb_std': 2.0,
            'atr_multiplier': 1.5
        }
        
        result = self.backtest_engine._run_bb_strategy(self.factor_data, params)
        
        assert result is not None
        assert 'portfolio_values' in result
        assert 'trades' in result
        assert 'stats' in result
    
    def test_run_multi_factor_strategy(self):
        """测试多因子策略"""
        params = {
            'multi_factor_threshold': 2,
            'atr_multiplier': 1.5
        }
        
        result = self.backtest_engine._run_multi_factor_strategy(self.factor_data, params)
        
        assert result is not None
        assert 'portfolio_values' in result
        assert 'trades' in result
        assert 'stats' in result
    
    def test_run_all_strategies(self):
        """测试运行所有策略"""
        params = {
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
        
        results = self.backtest_engine.run_all_strategies(self.factor_data, params)
        
        assert results is not None
        assert isinstance(results, dict)
        assert len(results) == 5  # 5个策略
        
        for strategy_name, result in results.items():
            assert 'portfolio_values' in result
            assert 'trades' in result
            assert 'stats' in result
    
    def test_calculate_stats(self):
        """测试计算统计指标"""
        # 生成模拟组合价值
        n_days = 100
        portfolio_values = pd.Series(
            100000 * (1 + np.random.normal(0.001, 0.02, n_days)).cumprod(),
            index=pd.date_range('2020-01-01', periods=n_days, freq='B')
        )
        
        trades = [
            {'type': 'entry', 'price': 1800, 'size': 10},
            {'type': 'exit', 'price': 1850, 'size': 10},
            {'type': 'entry', 'price': 1820, 'size': 10},
            {'type': 'exit', 'price': 1790, 'size': 10},
        ]
        
        prices = pd.Series(1800 + np.random.normal(0, 50, n_days), index=portfolio_values.index)
        
        stats = self.backtest_engine._calculate_stats(portfolio_values, trades, prices)
        
        assert stats is not None
        assert 'total_return' in stats
        assert 'ann_return' in stats
        assert 'sharpe' in stats
        assert 'max_dd' in stats
        assert 'win_rate' in stats
        assert 'n_trades' in stats


class TestFactorEngine:
    """测试FactorEngine类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.factor_engine = FactorEngine()
        
        # 生成测试数据
        self.data_engine = DataEngine(use_cache=False)
        self.price_data = self.data_engine._generate_simulation_data(
            '2020-01-01', '2020-06-30'
        )
    
    def test_initialization(self):
        """测试初始化"""
        assert self.factor_engine.factor_data is None
    
    def test_calculate_all_factors(self):
        """测试计算所有因子"""
        result = self.factor_engine.calculate_all_factors(self.price_data)
        
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        
        # 检查趋势因子
        assert 'sma_fast' in result.columns
        assert 'sma_slow' in result.columns
        assert 'macd_line' in result.columns
        assert 'macd_signal' in result.columns
        assert 'macd_histogram' in result.columns
        
        # 检查震荡因子
        assert 'rsi' in result.columns
        assert 'bb_middle' in result.columns
        assert 'bb_upper' in result.columns
        assert 'bb_lower' in result.columns
        
        # 检查波动因子
        assert 'atr' in result.columns
        
        # 检查动量因子
        assert 'momentum_20d' in result.columns
        assert 'momentum_60d' in result.columns
        
        # 检查Regime
        assert 'regime' in result.columns
    
    def test_get_factor_list(self):
        """测试获取因子列表"""
        self.factor_engine.calculate_all_factors(self.price_data)
        
        factor_list = self.factor_engine.get_factor_list()
        
        assert factor_list is not None
        assert isinstance(factor_list, list)
        assert len(factor_list) > 0
        assert 'close' not in factor_list
        assert 'open' not in factor_list


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

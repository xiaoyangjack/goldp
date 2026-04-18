import pytest
import pandas as pd
import numpy as np
from core.event_driven_strategy import EventDrivenStrategy


def test_event_driven_strategy_initialization():
    """测试事件驱动策略初始化"""
    strategy = EventDrivenStrategy()
    assert strategy.support_zone_lower == 4650
    assert strategy.support_zone_upper == 4720
    assert strategy.stop_loss == 4580
    assert strategy.position_size_range == (0.3, 0.4)
    assert strategy.current_position == 0
    assert strategy.event_weights['iran_ceasefire'] == 0.5
    assert strategy.event_weights['rate_cut_probability'] == 0.2


def test_support_test_condition():
    """测试支撑位二次测试条件"""
    strategy = EventDrivenStrategy()
    
    # 创建模拟价格数据
    dates = pd.date_range('2024-01-01', '2024-01-30')
    prices = np.linspace(4640, 4730, 30)
    # 在支撑位附近创建二次测试
    prices[-5] = 4655  # 第一次测试
    prices[-2] = 4652  # 第二次测试
    
    price_data = pd.DataFrame({
        'close': prices
    }, index=dates)
    
    # 测试支撑位二次测试
    result = strategy.check_support_test(price_data)
    assert result is True
    assert strategy.support_test_count >= 2


def test_event_score_calculation():
    """测试事件权重得分计算"""
    strategy = EventDrivenStrategy()
    
    # 测试单个事件
    event_conditions = {'iran_ceasefire': True, 'rate_cut_probability': False}
    strategy.update_event_conditions(event_conditions)
    score = strategy.calculate_event_score()
    assert score == 0.5
    
    # 测试多个事件
    event_conditions = {'iran_ceasefire': True, 'rate_cut_probability': True, 'etf_outflow': True}
    strategy.update_event_conditions(event_conditions)
    score = strategy.calculate_event_score()
    assert score == 0.5 + 0.2 + 0.1 == 0.8


def test_buy_signal_generation():
    """测试买入信号生成"""
    strategy = EventDrivenStrategy()
    
    # 创建模拟价格数据
    dates = pd.date_range('2024-01-01', '2024-01-30')
    prices = np.linspace(4640, 4700, 30)
    # 在支撑位附近创建二次测试
    prices[-5] = 4655  # 第一次测试
    prices[-2] = 4652  # 第二次测试
    
    price_data = pd.DataFrame({
        'close': prices,
        'atr': [15] * 30
    }, index=dates)
    
    # 测试买入信号
    event_conditions = {'iran_ceasefire': False, 'rate_cut_probability': False}
    result = strategy.run_strategy(price_data, event_conditions)
    
    assert result['signal']['signal_type'] == 'buy'
    assert 0.3 <= result['trade']['position'] <= 0.4
    assert result['trade']['stop_loss'] == 4580


def test_sell_signal_generation():
    """测试卖出信号生成"""
    strategy = EventDrivenStrategy()
    
    # 先设置当前仓位为40%
    strategy.current_position = 0.4
    strategy.entry_price = 4680
    
    # 创建模拟价格数据
    dates = pd.date_range('2024-01-01', '2024-01-30')
    price_data = pd.DataFrame({
        'close': [4700] * 30,
        'atr': [15] * 30
    }, index=dates)
    
    # 测试卖出信号（2个预警条件触发）
    event_conditions = {'iran_ceasefire': True, 'rate_cut_probability': True}
    result = strategy.run_strategy(price_data, event_conditions)
    
    assert result['signal']['signal_type'] == 'sell'
    assert result['trade']['position'] == 0.3
    assert 'dynamic_stop_loss' in result['trade']


def test_stop_loss_trigger():
    """测试止损触发"""
    strategy = EventDrivenStrategy()
    
    # 设置当前仓位
    strategy.current_position = 0.35
    strategy.entry_price = 4680
    
    # 创建模拟价格数据（价格低于止损）
    dates = pd.date_range('2024-01-01', '2024-01-30')
    price_data = pd.DataFrame({
        'close': [4570],  # 低于止损价4580
        'atr': [15]
    }, index=dates[-1:])
    
    # 测试止损触发
    event_conditions = {'iran_ceasefire': False, 'rate_cut_probability': False}
    result = strategy.run_strategy(price_data, event_conditions)
    
    assert result['current_position'] == 0


def test_no_signal_generation():
    """测试无信号生成的情况"""
    strategy = EventDrivenStrategy()
    
    # 创建模拟价格数据（价格不在支撑区间）
    dates = pd.date_range('2024-01-01', '2024-01-30')
    price_data = pd.DataFrame({
        'close': [4800] * 30,  # 价格高于支撑区间
        'atr': [15] * 30
    }, index=dates)
    
    # 测试无信号
    event_conditions = {'iran_ceasefire': False, 'rate_cut_probability': False}
    result = strategy.run_strategy(price_data, event_conditions)
    
    assert result['signal']['signal_type'] == 'none'
    assert result['trade']['action'] == 'none'


if __name__ == '__main__':
    pytest.main(['-v', __file__])

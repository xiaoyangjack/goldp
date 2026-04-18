import pandas as pd
import numpy as np
from gold_quant_system.core.event_driven_strategy import EventDrivenStrategy


def test_event_driven_strategy():
    """测试事件驱动策略"""
    print("=== 测试事件驱动策略 ===")
    
    # 初始化策略
    strategy = EventDrivenStrategy()
    print("策略初始化完成")
    print(f"支撑区: ${strategy.support_zone_lower}-${strategy.support_zone_upper}")
    print(f"止损: ${strategy.stop_loss}")
    print(f"仓位范围: {strategy.position_size_range[0]*100}%-{strategy.position_size_range[1]*100}%")
    print(f"事件权重: {strategy.event_weights}")
    
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
    
    print("\n=== 测试1: 支撑位二次测试 ===")
    support_test_result = strategy.check_support_test(price_data)
    print(f"支撑位二次测试结果: {support_test_result}")
    print(f"支撑测试次数: {strategy.support_test_count}")
    
    print("\n=== 测试2: 事件得分计算 ===")
    event_conditions = {'iran_ceasefire': True, 'rate_cut_probability': True, 'etf_outflow': True}
    strategy.update_event_conditions(event_conditions)
    event_score = strategy.calculate_event_score()
    print(f"事件得分: {event_score:.2f}")
    
    print("\n=== 测试3: 买入信号生成 ===")
    # 重置策略状态
    strategy = EventDrivenStrategy()
    event_conditions = {'iran_ceasefire': False, 'rate_cut_probability': False}
    result = strategy.run_strategy(price_data, event_conditions)
    print(f"信号类型: {result['signal']['signal_type']}")
    print(f"交易动作: {result['trade']['action']}")
    if result['trade']['action'] == 'buy':
        print(f"仓位: {result['trade']['position']:.2f}")
        print(f"止损: {result['trade']['stop_loss']}")
    
    print("\n=== 测试4: 卖出信号生成 ===")
    # 设置当前仓位
    strategy.current_position = 0.4
    strategy.entry_price = 4680
    # 触发2个预警条件
    event_conditions = {'iran_ceasefire': True, 'rate_cut_probability': True}
    result = strategy.run_strategy(price_data, event_conditions)
    print(f"信号类型: {result['signal']['signal_type']}")
    print(f"交易动作: {result['trade']['action']}")
    if result['trade']['action'] == 'sell':
        print(f"仓位: {result['trade']['position']:.2f}")
        print(f"动态止损: {result['trade']['dynamic_stop_loss']:.2f}")
    
    print("\n=== 测试5: 止损触发 ===")
    # 设置当前仓位
    strategy = EventDrivenStrategy()
    strategy.current_position = 0.35
    strategy.entry_price = 4680
    # 创建低于止损的价格数据
    stop_loss_data = pd.DataFrame({
        'close': [4570],  # 低于止损价4580
        'atr': [15]
    }, index=[dates[-1]])
    event_conditions = {'iran_ceasefire': False, 'rate_cut_probability': False}
    result = strategy.run_strategy(stop_loss_data, event_conditions)
    print(f"当前仓位: {result['current_position']}")
    print(f"是否触发止损: {result['current_position'] == 0}")
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    test_event_driven_strategy()

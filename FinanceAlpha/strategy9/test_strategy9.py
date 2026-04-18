import numpy as np
import pandas as pd
from .strategy9 import Strategy9

def generate_mock_option_chain(underlying_price=4500, time_to_expiry=1):
    """生成模拟期权链数据"""
    strikes = np.arange(4400, 4600, 25)
    option_types = ['call', 'put']
    
    data = []
    for strike in strikes:
        for option_type in option_types:
            # 计算理论IV（基于moneyness）
            moneyness = strike / underlying_price
            if option_type == 'call':
                iv = 0.2 + 0.1 * abs(moneyness - 1)  # 平值期权IV较低
            else:
                iv = 0.22 + 0.08 * abs(moneyness - 1)
            
            # 添加一些随机噪声
            iv += np.random.normal(0, 0.01)
            
            data.append({
                'strike': strike,
                'option_type': option_type,
                'implied_volatility': max(0.05, iv),  # 确保IV为正
                'last_price': np.random.uniform(10, 100),
                'underlying_price': underlying_price,
                'time_to_expiry': time_to_expiry
            })
    
    return pd.DataFrame(data)

def generate_mock_historical_data(days=10):
    """生成模拟历史数据"""
    historical_data = {}
    
    for i in range(days):
        date = pd.Timestamp.now() - pd.Timedelta(days=i)
        underlying_price = 4500 + np.random.normal(0, 50)
        time_to_expiry = 1
        
        option_chain = generate_mock_option_chain(underlying_price, time_to_expiry)
        
        # 生成第二天数据（用于计算收益）
        next_day_underlying = underlying_price * (1 + np.random.normal(0, 0.01))
        
        historical_data[date.strftime('%Y-%m-%d')] = {
            'option_chain': option_chain,
            'underlying_price': underlying_price,
            'time_to_expiry': time_to_expiry,
            'next_day_data': {
                'underlying_price': next_day_underlying
            }
        }
    
    return historical_data

def test_strategy9():
    """测试策略9"""
    print("=== Testing Strategy9 ===")
    
    # 初始化策略
    strategy = Strategy9()
    
    # 生成模拟数据
    option_chain = generate_mock_option_chain()
    underlying_price = 4500
    time_to_expiry = 1
    
    print(f"Generated option chain with {len(option_chain)} options")
    print(f"Underlying price: {underlying_price}")
    print(f"Time to expiry: {time_to_expiry} day")
    
    # 运行策略
    result = strategy.run_strategy(option_chain, underlying_price, time_to_expiry)
    
    # 打印策略结果摘要
    print("\n=== Strategy Result Summary ===")
    summary = strategy.get_strategy_summary(result)
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    # 测试回测功能
    print("\n=== Backtesting Strategy ===")
    historical_data = generate_mock_historical_data(days=5)
    backtest_result = strategy.backtest_strategy(historical_data)
    
    # 打印回测统计
    print("\n=== Backtest Statistics ===")
    for key, value in backtest_result['stats'].items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    # 测试风险参数设置
    print("\n=== Testing Risk Parameters ===")
    new_risk_params = {
        'max_position_size': 500000,
        'stop_loss': 0.01,
        'take_profit': 0.03
    }
    strategy.set_risk_parameters(new_risk_params)
    
    print("Strategy9 test completed successfully!")

if __name__ == "__main__":
    test_strategy9()
import sys
import os

# 添加FinanceAlpha目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'FinanceAlpha'))

import numpy as np
import pandas as pd
from strategy9.strategy9 import Strategy9

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
    
    print("Strategy9 test completed successfully!")

if __name__ == "__main__":
    test_strategy9()
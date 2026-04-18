#!/usr/bin/env python3
"""
Task 8: 回测与参数调优 - 简化版
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("开始执行Task 8: 回测与参数调优")

# 生成模拟数据
def generate_mock_data():
    """
    生成模拟黄金价格数据
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='B')
    n = len(dates)
    
    # 生成基础价格序列（包含2026年ATH$5589及回调）
    np.random.seed(42)
    
    # 初始价格
    base_price = 4500
    prices = [base_price]
    
    # 模拟上涨趋势到ATH
    for i in range(n // 3):
        daily_change = np.random.normal(0.001, 0.003)
        new_price = prices[-1] * (1 + daily_change)
        prices.append(new_price)
    
    # 达到ATH $5589
    ath_price = 5589
    prices[-1] = ath_price
    
    # 模拟回调
    for i in range(n // 3):
        daily_change = np.random.normal(-0.001, 0.003)
        new_price = prices[-1] * (1 + daily_change)
        prices.append(new_price)
    
    # 模拟震荡
    for i in range(n - len(prices)):
        daily_change = np.random.normal(0, 0.002)
        new_price = prices[-1] * (1 + daily_change)
        prices.append(new_price)
    
    # 生成DataFrame
    data = pd.DataFrame({
        'close': prices,
        'open': [p * 0.999 for p in prices],
        'high': [p * 1.002 for p in prices],
        'low': [p * 0.998 for p in prices]
    }, index=dates)
    
    # 计算ATR
    high = data['high']
    low = data['low']
    close = data['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    data['atr'] = tr.rolling(window=14).mean()
    
    print(f"模拟数据生成完成，共 {len(data)} 条记录")
    print(f"价格范围: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    print(f"ATH: ${ath_price:.2f}")
    
    return data

# 简单回测函数
def backtest(data, atr_multiplier, batch_buy_min, batch_buy_max):
    """
    简单回测策略
    """
    # 计算GRAM因子
    df = data.copy()
    
    # 计算R因子
    df['r_5d'] = df['close'].pct_change(5)
    df['r_20d'] = df['close'].pct_change(20)
    df['r_60d'] = df['close'].pct_change(60)
    df['r_factor'] = 0.4 * df['r_5d'] + 0.3 * df['r_20d'] + 0.3 * df['r_60d']
    
    # 标准化
    mean = df['r_factor'].rolling(window=60).mean()
    std = df['r_factor'].rolling(window=60).std()
    df['r_factor_norm'] = (df['r_factor'] - mean) / std
    
    # 生成信号
    def generate_signal(row):
        if row['r_factor_norm'] > 0.5:
            return 1
        elif row['r_factor_norm'] < -0.5:
            return -1
        elif batch_buy_min <= row['close'] <= batch_buy_max:
            return 0.5
        else:
            return 0
    
    df['signal'] = df.apply(generate_signal, axis=1)
    
    # 回测
    portfolio_value = 1.0
    position = 0.0
    entry_price = 0.0
    stop_loss = 0.0
    trades = []
    
    for i in range(1, len(df)):
        current_price = df['close'].iloc[i]
        current_signal = df['signal'].iloc[i]
        atr = df['atr'].iloc[i]
        
        # 检查止损
        if position != 0:
            if position > 0 and current_price <= stop_loss:
                # 多头止损
                exit_price = stop_loss
                trade_return = (exit_price - entry_price) / entry_price - 0.0015
                portfolio_value *= (1 + trade_return * position)
                trades.append(trade_return)
                position = 0
            elif position < 0 and current_price >= stop_loss:
                # 空头止损
                exit_price = stop_loss
                trade_return = (entry_price - exit_price) / entry_price - 0.0015
                portfolio_value *= (1 + trade_return * abs(position))
                trades.append(trade_return)
                position = 0
        
        # 执行交易信号
        if current_signal == 1 and position <= 0:
            # 多头入场
            position = 1.0
            entry_price = current_price
            stop_loss = entry_price - atr_multiplier * atr
        elif current_signal == -1 and position >= 0:
            # 空头入场
            position = -1.0
            entry_price = current_price
            stop_loss = entry_price + atr_multiplier * atr
        elif current_signal == 0.5 and position == 0:
            # 半仓建仓
            position = 0.5
            entry_price = current_price
            stop_loss = entry_price - atr_multiplier * atr
        elif current_signal == 0 and position != 0:
            # 平仓
            exit_price = current_price
            if position > 0:
                trade_return = (exit_price - entry_price) / entry_price - 0.0015
            else:
                trade_return = (entry_price - exit_price) / entry_price - 0.0015
            portfolio_value *= (1 + trade_return * abs(position))
            trades.append(trade_return)
            position = 0
    
    # 计算指标
    total_return = portfolio_value - 1
    annualized_return = (portfolio_value ** (252 / len(df))) - 1
    
    # 计算胜率和盈亏比
    win_trades = [t for t in trades if t > 0]
    loss_trades = [t for t in trades if t < 0]
    win_rate = len(win_trades) / len(trades) if trades else 0
    avg_win = np.mean(win_trades) if win_trades else 0
    avg_loss = np.mean([abs(t) for t in loss_trades]) if loss_trades else 1
    win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
    
    return {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'win_rate': win_rate,
        'win_loss_ratio': win_loss_ratio,
        'total_trades': len(trades)
    }

# 主函数
def main():
    try:
        # 生成数据
        data = generate_mock_data()
        
        # 比较权重调整前后（简化版）
        print("\n权重调整前后对比:")
        print("新权重 (R:40%, O:25%, E:20%, M:15%):")
        base_result = backtest(data, 1.5, 4650, 4720)
        print(f"  总收益率: {base_result['total_return'] * 100:.2f}%")
        print(f"  年化收益率: {base_result['annualized_return'] * 100:.2f}%")
        print(f"  胜率: {base_result['win_rate'] * 100:.2f}%")
        print(f"  盈亏比: {base_result['win_loss_ratio']:.2f}")
        
        # 网格调优
        print("\n开始网格调优...")
        param_grid = {
            'atr_multiplier': [1.0, 1.2, 1.5, 1.8, 2.0],
            'batch_buy_min': [4600, 4650, 4700],
            'batch_buy_max': [4720, 4750, 4800]
        }
        
        best_score = -float('inf')
        best_params = None
        best_result = None
        
        for atr in param_grid['atr_multiplier']:
            for min_price in param_grid['batch_buy_min']:
                for max_price in param_grid['batch_buy_max']:
                    if min_price >= max_price:
                        continue
                    
                    result = backtest(data, atr, min_price, max_price)
                    score = result['annualized_return'] - (1 - result['win_rate'])
                    
                    print(f"参数组合: ATR={atr}, 建仓区间={min_price}-{max_price}")
                    print(f"  总收益率: {result['total_return'] * 100:.2f}%")
                    print(f"  年化收益率: {result['annualized_return'] * 100:.2f}%")
                    print(f"  胜率: {result['win_rate'] * 100:.2f}%")
                    print(f"  盈亏比: {result['win_loss_ratio']:.2f}")
                    
                    if score > best_score:
                        best_score = score
                        best_params = (atr, min_price, max_price)
                        best_result = result
        
        # 打印最优参数
        print("\n最优参数组合:")
        print(f"ATR止损系数: {best_params[0]}")
        print(f"分批建仓区间: ${best_params[1]} - ${best_params[2]}")
        print(f"总收益率: {best_result['total_return'] * 100:.2f}%")
        print(f"年化收益率: {best_result['annualized_return'] * 100:.2f}%")
        print(f"胜率: {best_result['win_rate'] * 100:.2f}%")
        print(f"盈亏比: {best_result['win_loss_ratio']:.2f}")
        
        print("\nTask 8: 回测与参数调优完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

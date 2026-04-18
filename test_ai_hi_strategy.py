#!/usr/bin/env python3
# 测试AI+HI融合的基本面量化多因子策略

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gold_quant_system.strategies.advanced.ai_hi_fundamental_quant_strategy import AIHIFundamentalQuantStrategy

if __name__ == "__main__":
    # 初始化策略
    strategy = AIHIFundamentalQuantStrategy()
    
    # 测试单个股票
    test_symbol = 'AAPL'
    
    # 测试时间范围
    start_date = '2020-01-01'
    end_date = '2023-12-31'
    
    print("开始测试AI+HI融合的基本面量化多因子策略...")
    print(f"测试股票: {test_symbol}")
    print(f"时间范围: {start_date} 到 {end_date}")
    
    try:
        # 获取数据
        data = strategy.fetch_stock_data(test_symbol, start_date, end_date)
        print(f"\n获取数据成功: {len(data)} 条记录")
        
        # 生成模拟基本面数据
        data = strategy.generate_fake_fundamental_data(data)
        print("生成模拟基本面数据成功")
        
        # 准备训练数据
        training_data = strategy.prepare_training_data(data)
        print(f"准备训练数据成功: {len(training_data)} 条记录")
        
        # 训练AI模型
        strategy.train_ai_model(training_data)
        print("训练AI模型成功")
        
        # 生成信号
        data_with_signals = strategy.generate_signals(data)
        print(f"生成信号成功: {len(data_with_signals[data_with_signals['signal'] != 0])} 个交易信号")
        
        # 测试动态因子加权
        if strategy.factor_weights:
            bull_weights = strategy.dynamic_factor_weighting('bull')
            bear_weights = strategy.dynamic_factor_weighting('bear')
            print("\n动态因子加权测试成功")
            print("牛市因子权重:")
            for factor, weight in sorted(bull_weights.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"{factor}: {weight:.4f}")
            print("熊市因子权重:")
            for factor, weight in sorted(bear_weights.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"{factor}: {weight:.4f}")
        
        print("\n策略测试完成！")
        
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
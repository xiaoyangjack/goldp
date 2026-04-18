#!/usr/bin/env python3
"""
测试多模态语义Alpha量化策略
"""

import pandas as pd
import numpy as np
from gold_quant_system.strategies.advanced.multimodal_semantic_alpha_strategy import MultimodalSemanticAlphaStrategy


def test_multimodal_strategy():
    """
    测试多模态语义Alpha策略
    """
    print("=== 测试多模态语义Alpha量化策略 ===")
    
    # 初始化策略
    config = {
        'signal_threshold': 0.01,
        'target_vol': 0.01,
        'max_drawdown': 0.2,
        'asset_weight_limit': 0.4,
        'llm_model_name': 'bert-base-uncased'
    }
    
    strategy = MultimodalSemanticAlphaStrategy(config)
    
    # 生成模拟数据
    print("生成模拟数据...")
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    assets = ['SPY', 'TLT', 'GLD', 'QQQ']
    
    # 生成市场数据
    market_data = pd.DataFrame(
        np.random.randn(len(dates), len(assets)) * 0.01 + 1.001,
        index=dates, columns=assets
    ).cumprod()
    
    # 生成多模态数据
    multimodal_data = pd.DataFrame({
        'text': ['Economic growth is strong', 'Inflation is rising', 'Market is volatile', 'Technology sector is booming', 'Interest rates are falling'] * (len(dates) // 5 + 1),
        'audio': np.random.randint(50, 500, size=len(dates)),
        'social_media': np.random.randint(5, 50, size=len(dates))
    }).iloc[:len(dates)]
    multimodal_data.index = dates
    
    print(f"生成了 {len(dates)} 个交易日的数据")
    print(f"市场数据形状: {market_data.shape}")
    print(f"多模态数据形状: {multimodal_data.shape}")
    
    # 测试数据处理
    print("\n测试数据处理...")
    sample_data = multimodal_data.iloc[0].to_dict()
    processed_data = strategy.process_multimodal_data(sample_data)
    print(f"处理后的数据: {processed_data}")
    
    # 测试语义特征提取
    print("\n测试语义特征提取...")
    semantic_features = strategy.extract_semantic_features(processed_data)
    print(f"语义特征维度: {len(semantic_features)}")
    print(f"前10个特征值: {semantic_features[:10]}")
    
    # 测试信号体系构建
    print("\n测试信号体系构建...")
    signal_features = strategy.build_signal_system(semantic_features, market_data.iloc[:10])
    print(f"信号特征维度: {len(signal_features)}")
    
    # 运行回测
    print("\n运行回测...")
    result = strategy.run_backtest(market_data, multimodal_data, initial_cash=1000000)
    
    # 计算风险指标
    print("\n计算风险指标...")
    metrics = strategy.get_risk_metrics(result['portfolio_values'])
    
    # 输出结果
    print("\n=== 回测结果 ===")
    print(f"初始资金: $1,000,000")
    print(f"最终价值: ${result['final_value']:.2f}")
    print(f"总收益: {result['total_return']:.2f}%")
    print(f"交易天数: {len(market_data)}")
    
    print("\n=== 风险指标 ===")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")
    
    # 可视化结果
    print("\n=== 策略表现 ===")
    print(f"组合价值走势:")
    print(result['portfolio_values'].tail())
    
    # 测试实时预测
    print("\n测试实时预测...")
    latest_data = multimodal_data.iloc[-1].to_dict()
    processed_latest = strategy.process_multimodal_data(latest_data)
    semantic_latest = strategy.extract_semantic_features(processed_latest)
    signal_latest = strategy.build_signal_system(semantic_latest, market_data)
    
    # 准备训练数据进行预测
    X_train = []
    y_train = []
    for j in range(len(market_data) - 10, len(market_data) - 1):
        train_data = strategy.process_multimodal_data(multimodal_data.iloc[j].to_dict())
        train_features = strategy.extract_semantic_features(train_data)
        train_signal_features = strategy.build_signal_system(train_features, market_data.iloc[:j+1])
        X_train.append(train_signal_features)
        y_train.append(market_data.iloc[j+1].mean() - market_data.iloc[j].mean())
    
    if len(X_train) > 0:
        strategy.train_hybrid_model(np.array(X_train), np.array(y_train))
        predictions = strategy.generate_predictions(np.array([signal_latest]))
        signals = {asset: pred for asset, pred in zip(market_data.columns, predictions)}
        weights = strategy.allocate_portfolio(signals, market_data)
        
        print("\n=== 实时预测结果 ===")
        print("预测收益率:")
        for asset, pred in signals.items():
            print(f"{asset}: {pred:.4f}")
        
        print("\n推荐仓位:")
        for asset, weight in weights.items():
            print(f"{asset}: {weight:.4f}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_multimodal_strategy()

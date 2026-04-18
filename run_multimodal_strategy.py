#!/usr/bin/env python3
"""
运行多模态语义Alpha量化策略
"""

import pandas as pd
import numpy as np
from gold_quant_system.strategies.advanced.multimodal_semantic_alpha_strategy import MultimodalSemanticAlphaStrategy
from config.multimodal_config import MULTIMODAL_STRATEGY_CONFIG, DATA_SOURCES, ASSETS, STRATEGY_TYPES


def run_multimodal_strategy():
    """
    运行多模态语义Alpha策略
    """
    print("=== 多模态语义Alpha量化策略 ===")
    print("基于LLM+梯度提升树(GBM)混合架构")
    print("从非结构化多模态数据中实时提取语义Alpha信号")
    print("\n" + "="*60)
    
    # 1. 初始化策略
    print("1. 初始化策略...")
    strategy = MultimodalSemanticAlphaStrategy(MULTIMODAL_STRATEGY_CONFIG)
    
    # 2. 显示配置信息
    print("\n2. 策略配置:")
    print(f"- LLM模型: {MULTIMODAL_STRATEGY_CONFIG['llm_model_name']}")
    print(f"- 信号阈值: {MULTIMODAL_STRATEGY_CONFIG['signal_threshold']}")
    print(f"- 目标波动率: {MULTIMODAL_STRATEGY_CONFIG['target_vol']}")
    print(f"- 最大回撤: {MULTIMODAL_STRATEGY_CONFIG['max_drawdown']}")
    
    # 3. 显示数据来源
    print("\n3. 多模态数据来源:")
    for source_type, config in DATA_SOURCES.items():
        if config['enabled']:
            print(f"- {source_type}: {', '.join(config['sources'])} (更新频率: {config['update_frequency']})")
    
    # 4. 显示资产配置
    print("\n4. 资产配置:")
    for asset_class, subclasses in ASSETS.items():
        print(f"- {asset_class}:")
        for subclass, assets in subclasses.items():
            print(f"  * {subclass}: {', '.join(assets[:3])}{'...' if len(assets) > 3 else ''}")
    
    # 5. 生成模拟数据
    print("\n5. 生成模拟数据...")
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    
    # 选择部分资产进行测试
    test_assets = ['SPY', 'TLT', 'GLD', 'QQQ', 'AAPL', 'MSFT']
    
    # 生成市场数据
    market_data = pd.DataFrame(
        np.random.randn(len(dates), len(test_assets)) * 0.01 + 1.001,
        index=dates, columns=test_assets
    ).cumprod()
    
    # 生成多模态数据
    # 模拟不同类型的文本数据
    text_samples = [
        'Economic growth is strong, corporate earnings are exceeding expectations',
        'Inflation is rising, central bank may raise interest rates',
        'Market is volatile due to geopolitical tensions',
        'Technology sector is booming with new innovations',
        'Interest rates are falling, boosting equity valuations',
        'Energy prices are rising due to supply constraints',
        'Consumer spending is strong, retail sales are up',
        'Housing market is cooling due to higher mortgage rates',
        'Unemployment rate is low, labor market is tight',
        'Global trade tensions are affecting market sentiment'
    ]
    
    multimodal_data = pd.DataFrame({
        'text': np.random.choice(text_samples, size=len(dates)),
        'audio': np.random.randint(50, 500, size=len(dates)),
        'social_media': np.random.randint(5, 100, size=len(dates))
    })
    multimodal_data.index = dates
    
    print(f"生成了 {len(dates)} 个交易日的数据")
    print(f"市场数据: {len(test_assets)} 个资产")
    
    # 6. 运行回测
    print("\n6. 运行回测...")
    result = strategy.run_backtest(market_data, multimodal_data, initial_cash=1000000)
    
    # 7. 计算风险指标
    print("\n7. 计算风险指标...")
    metrics = strategy.get_risk_metrics(result['portfolio_values'])
    
    # 8. 显示回测结果
    print("\n8. 回测结果:")
    print("="*60)
    print(f"初始资金: ${MULTIMODAL_STRATEGY_CONFIG['initial_cash']:,.2f}")
    print(f"最终价值: ${result['final_value']:,.2f}")
    print(f"总收益: {result['total_return']*100:.2f}%")
    print(f"交易周期: {len(dates)} 个交易日")
    print("="*60)
    
    # 9. 显示风险指标
    print("\n9. 风险指标:")
    print("- 年化收益率: {:.2f}%".format(metrics['annual_return']*100))
    print("- 年化波动率: {:.2f}%".format(metrics['annual_volatility']*100))
    print("- 夏普比率: {:.2f}".format(metrics['sharpe_ratio']))
    print("- 最大回撤: {:.2f}%".format(metrics['max_drawdown']*100))
    print("- 索提诺比率: {:.2f}".format(metrics['sortino_ratio']))
    
    # 10. 显示策略类型适配
    print("\n10. 策略类型适配:")
    for strategy_type, config in STRATEGY_TYPES.items():
        if config['enabled']:
            print(f"- {strategy_type}: {config['constraints']}")
    
    # 11. 显示实时预测示例
    print("\n11. 实时预测示例:")
    print("基于最新多模态数据的预测结果:")
    
    # 模拟最新的多模态数据
    latest_data = {
        'text': 'Federal Reserve announces interest rate decision, market reacts positively',
        'audio': 350,
        'social_media': 75
    }
    
    # 处理数据并生成预测
    processed_data = strategy.process_multimodal_data(latest_data)
    semantic_features = strategy.extract_semantic_features(processed_data)
    signal_features = strategy.build_signal_system(semantic_features, market_data)
    
    # 准备训练数据
    X_train = []
    y_train = []
    lookback = MULTIMODAL_STRATEGY_CONFIG['lookback_period']
    
    for j in range(len(market_data) - lookback, len(market_data) - 1):
        train_data = strategy.process_multimodal_data(multimodal_data.iloc[j].to_dict())
        train_features = strategy.extract_semantic_features(train_data)
        train_signal_features = strategy.build_signal_system(train_features, market_data.iloc[:j+1])
        X_train.append(train_signal_features)
        y_train.append(market_data.iloc[j+1].mean() - market_data.iloc[j].mean())
    
    if len(X_train) > 0:
        strategy.train_hybrid_model(np.array(X_train), np.array(y_train))
        predictions = strategy.generate_predictions(np.array([signal_features]))
        signals = {asset: pred for asset, pred in zip(market_data.columns, predictions)}
        weights = strategy.allocate_portfolio(signals, market_data)
        
        print("\n预测收益率:")
        for asset, pred in signals.items():
            print(f"{asset}: {pred:.4f}")
        
        print("\n推荐仓位:")
        for asset, weight in weights.items():
            print(f"{asset}: {weight:.4f}")
    
    # 12. 总结
    print("\n" + "="*60)
    print("策略运行完成！")
    print("\n核心功能:")
    print("- 多模态数据解析: 支持文本、音频、社交媒体数据")
    print("- 语义信号提取: 基于LLM的语义理解")
    print("- 混合预测模型: LLM+GBM架构")
    print("- 策略类型适配: 支持多种策略类型")
    print("- 实时性优化: 支持实时数据处理")
    print("\n可扩展性:")
    print("- 可添加更多数据源")
    print("- 可使用更先进的LLM模型")
    print("- 可优化GBM模型参数")
    print("- 可添加更多风险控制措施")
    print("="*60)


if __name__ == "__main__":
    run_multimodal_strategy()

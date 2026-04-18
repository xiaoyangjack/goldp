#!/usr/bin/env python3
"""
测试报告系统
验证所有标准化报告模板是否正常工作
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from gold_quant_system.core.backtest_engine import BacktestEngine
from gold_quant_system.core.analytics_engine import AnalyticsEngine
from gold_quant_system.gui.report_exporter import ReportExporter


def generate_test_data(n_days=365):
    """生成测试数据"""
    dates = pd.date_range(start='2020-01-01', periods=n_days, freq='D')
    
    # 生成随机价格数据
    np.random.seed(42)
    returns = np.random.normal(0, 0.01, n_days)
    price = 100 * np.exp(np.cumsum(returns))
    
    # 生成因子数据
    df = pd.DataFrame({
        'close': price,
        'sma_fast': price.rolling(20).mean(),
        'sma_slow': price.rolling(60).mean(),
        'rsi': 50 + np.random.normal(0, 10, n_days),
        'macd_histogram': np.random.normal(0, 1, n_days),
        'bb_position': np.random.uniform(0, 1, n_days),
        'atr': np.random.uniform(0.5, 2.0, n_days),
        'atr_pct': np.random.uniform(0.005, 0.02, n_days),
        'sma_signal': np.where(np.random.random(n_days) > 0.5, 1, -1),
        'rsi_signal': np.where(np.random.random(n_days) > 0.5, 1, -1),
        'macd_signal_flag': np.where(np.random.random(n_days) > 0.5, 1, -1),
        'regime': np.random.choice(['TREND', 'RANGE'], n_days)
    }, index=dates)
    
    return df


def test_report_system():
    """测试报告系统"""
    print("=== 测试报告系统 ===")
    
    # 生成测试数据
    print("1. 生成测试数据...")
    df = generate_test_data()
    print(f"   生成了 {len(df)} 天的测试数据")
    
    # 运行回测
    print("2. 运行回测...")
    backtest_engine = BacktestEngine()
    backtest_results = backtest_engine.run_all_strategies(df)
    print(f"   完成 {len(backtest_results)} 个策略的回测")
    
    # 运行分析
    print("3. 运行分析...")
    analytics_engine = AnalyticsEngine()
    analysis_results = analytics_engine.analyze_results(backtest_results, df)
    print("   完成分析")
    
    # 导出报告
    print("4. 导出标准化报告...")
    exporter = ReportExporter()
    
    # 导出所有标准化报告
    results = exporter.export_standard_reports(backtest_results, analysis_results, df)
    
    print("   导出结果:")
    for report_type, report_info in results.items():
        print(f"   - {report_info['name']}:")
        print(f"     Markdown: {'✓' if report_info['markdown'] else '✗'}")
        print(f"     PDF: {'✓' if report_info['pdf'] else '✗'}")
        print(f"     Excel: {'✓' if report_info['excel'] else '✗'}")
    
    print("\n=== 测试完成 ===")
    print("所有报告已导出到:")
    print(f"   {exporter.export_dir}")


if __name__ == "__main__":
    test_report_system()
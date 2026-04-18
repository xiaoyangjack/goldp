#!/usr/bin/env python3
"""
测试报告模板
验证所有标准化报告模板是否能正常生成
"""

from gold_quant_system.core.report_templates import ReportTemplates


def test_report_templates():
    """测试报告模板"""
    print("=== 测试报告模板 ===")
    
    # 创建报告模板实例
    templates = ReportTemplates()
    
    # 模拟回测结果
    backtest_results = {
        'sma': {
            'stats': {
                'total_return': 0.25,
                'ann_return': 0.15,
                'sharpe': 1.8,
                'max_dd': -0.12,
                'win_rate': 0.6,
                'n_trades': 50
            },
            'trades': []
        },
        'rsi': {
            'stats': {
                'total_return': 0.30,
                'ann_return': 0.18,
                'sharpe': 2.1,
                'max_dd': -0.10,
                'win_rate': 0.65,
                'n_trades': 60
            },
            'trades': []
        }
    }
    
    # 模拟分析结果
    analysis_results = {
        'ic_analysis': {
            'sma_signal': 0.15,
            'rsi': 0.12,
            'macd_histogram': 0.08
        },
        'correlation_matrix': None
    }
    
    # 测试所有报告模板
    report_types = [
        'performance',
        'trading_behavior',
        'factor_effectiveness',
        'risk_attribution',
        'param_sensitivity',
        'out_of_sample',
        'portfolio_optimization',
        'sector_adaptability',
        'implementation_feasibility',
        'optimization_suggestions'
    ]
    
    for report_type in report_types:
        print(f"\n测试 {report_type} 报告...")
        try:
            content = templates.generate_report(report_type, backtest_results, analysis_results)
            print(f"  ✓ 成功生成报告，长度: {len(content)} 字符")
            # 打印报告开头部分
            print(f"  报告开头: {content[:100]}...")
        except Exception as e:
            print(f"  ✗ 生成报告失败: {e}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_report_templates()
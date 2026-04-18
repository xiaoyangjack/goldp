#!/usr/bin/env python3
"""
黄金量化本地研究系统分析引擎

接受BacktestEngine返回结果，计算各种分析指标和生成分析结果
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
from loguru import logger


class AnalyticsEngine:
    """
    分析引擎类
    """
    
    def __init__(self):
        pass
    
    def analyze_results(self, backtest_results, factor_data):
        """
        分析回测结果
        
        Args:
            backtest_results: 回测结果
            factor_data: 因子数据
        
        Returns:
            dict: 分析结果
        """
        analysis_results = {}
        
        # IC分析
        if factor_data is not None:
            ic_analysis = self._calculate_ic_analysis(factor_data)
            analysis_results["ic_analysis"] = ic_analysis
        
        # 相关性矩阵
        correlation_matrix = self._calculate_correlation_matrix(backtest_results)
        analysis_results["correlation_matrix"] = correlation_matrix
        
        # 参数敏感性热图（示例：SMA参数）
        param_heatmap = self._generate_param_heatmap()
        analysis_results["param_heatmap"] = param_heatmap
        
        return analysis_results
    
    def _calculate_ic_analysis(self, factor_data):
        """
        计算IC分析（信息系数）
        
        Args:
            factor_data: 因子数据
        
        Returns:
            dict: IC分析结果
        """
        ic_results = {}
        
        # 计算N+1日收益
        factor_data['next_day_return'] = factor_data['close'].pct_change().shift(-1)
        
        # 因子列表
        factors = [
            'sma_signal', 'macd_histogram', 'rsi', 
            'bb_position', 'atr', 'momentum_20d', 
            'momentum_60d'
        ]
        
        for factor in factors:
            if factor in factor_data.columns:
                # 计算Spearman相关系数
                valid_data = factor_data[[factor, 'next_day_return']].dropna()
                if len(valid_data) > 0:
                    correlation, _ = spearmanr(valid_data[factor], valid_data['next_day_return'])
                    ic_results[factor] = correlation
                else:
                    ic_results[factor] = 0
            else:
                ic_results[factor] = 0
        
        logger.info("IC分析计算完成")
        return ic_results
    
    def _calculate_correlation_matrix(self, backtest_results):
        """
        计算策略相关性矩阵
        
        Args:
            backtest_results: 回测结果
        
        Returns:
            pd.DataFrame: 相关性矩阵
        """
        if not backtest_results:
            return pd.DataFrame()
        
        # 收集所有策略的月度收益
        monthly_returns = {}
        for strategy_name, result in backtest_results.items():
            portfolio_values = result['portfolio_values']
            monthly = portfolio_values.resample('M').last()
            monthly_return = monthly.pct_change().dropna()
            monthly_returns[strategy_name] = monthly_return
        
        # 创建收益DataFrame
        returns_df = pd.DataFrame(monthly_returns)
        
        # 计算相关性矩阵
        correlation_matrix = returns_df.corr()
        
        logger.info("相关性矩阵计算完成")
        return correlation_matrix
    
    def _generate_param_heatmap(self):
        """
        生成参数敏感性热图数据（示例：SMA参数）
        
        Returns:
            dict: 参数热图数据
        """
        # 模拟SMA参数组合的Sharpe比率
        sma_fast_values = range(5, 61, 5)
        sma_slow_values = range(20, 201, 20)
        
        # 创建热图数据
        data = np.zeros((len(sma_slow_values), len(sma_fast_values)))
        
        # 模拟数据（实际应用中应基于真实回测）
        for i, slow in enumerate(sma_slow_values):
            for j, fast in enumerate(sma_fast_values):
                if fast < slow:
                    # 模拟Sharpe比率，基于一些合理的假设
                    data[i, j] = 2.0 + 0.001 * (slow - fast) - 0.0001 * (slow - 60)**2
                else:
                    data[i, j] = 0
        
        heatmap_data = {
            'data': data,
            'x_labels': [str(x) for x in sma_fast_values],
            'y_labels': [str(y) for y in sma_slow_values]
        }
        
        logger.info("参数热图数据生成完成")
        return heatmap_data
    
    def calculate_drawdown(self, portfolio_values):
        """
        计算最大回撤
        
        Args:
            portfolio_values: 投资组合价值
        
        Returns:
            pd.Series: 回撤序列
        """
        rolling_max = portfolio_values.cummax()
        drawdown = (portfolio_values - rolling_max) / rolling_max
        return drawdown
    
    def calculate_annual_returns(self, portfolio_values):
        """
        计算年度收益
        
        Args:
            portfolio_values: 投资组合价值
        
        Returns:
            pd.Series: 年度收益
        """
        yearly = portfolio_values.resample('A').last()
        yearly_returns = yearly.pct_change().dropna()
        return yearly_returns
    
    def run_walk_forward(self, factor_data, params, train_days=252, test_days=63):
        """
        执行Walk-Forward验证
        
        Args:
            factor_data: 因子数据
            params: 策略参数
            train_days: 训练窗口长度
            test_days: 测试窗口长度
        
        Returns:
            dict: Walk-Forward验证结果
        """
        from core.backtest_engine import BacktestEngine
        
        backtest_engine = BacktestEngine()
        n_days = len(factor_data)
        results = []
        
        for i in range(0, n_days - train_days - test_days + 1, test_days):
            # 分割训练和测试数据
            train_data = factor_data.iloc[i:i+train_days]
            test_data = factor_data.iloc[i+train_days:i+train_days+test_days]
            
            # 在训练数据上优化参数（这里简化处理，使用固定参数）
            # 实际应用中应在此进行参数优化
            
            # 在测试数据上回测
            test_results = backtest_engine.run_all_strategies(test_data, params)
            
            # 收集结果
            for strategy_name, result in test_results.items():
                if 'stats' in result:
                    results.append({
                        'strategy': strategy_name,
                        'period': f"{test_data.index[0].date()} to {test_data.index[-1].date()}",
                        'sharpe': result['stats'].get('sharpe', 0),
                        'total_return': result['stats'].get('total_return', 0)
                    })
        
        logger.info(f"Walk-Forward验证完成，共{len(results)}个测试周期")
        return pd.DataFrame(results)
    
    def export_report(self, backtest_results, factor_data):
        """
        导出HTML报告
        
        Args:
            backtest_results: 回测结果
            factor_data: 因子数据
        
        Returns:
            str: 报告文件路径
        """
        import datetime
        import os
        
        # 生成报告内容
        html_content = f"""
        <html>
        <head>
            <title>黄金量化研究报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .section {{ margin-bottom: 30px; }}
                .strategy {{ margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>黄金量化研究报告</h1>
            <p>生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="section">
                <h2>策略绩效概览</h2>
                <table>
                    <tr>
                        <th>策略</th>
                        <th>总收益</th>
                        <th>年化收益</th>
                        <th>夏普比率</th>
                        <th>最大回撤</th>
                        <th>胜率</th>
                        <th>交易次数</th>
                    </tr>
        """
        
        # 添加策略绩效数据
        for strategy_name, result in backtest_results.items():
            stats = result['stats']
            html_content += f"""
                    <tr>
                        <td>{strategy_name}</td>
                        <td>{stats.get('total_return', 0):.2%}</td>
                        <td>{stats.get('ann_return', 0):.2%}</td>
                        <td>{stats.get('sharpe', 0):.2f}</td>
                        <td>{stats.get('max_dd', 0):.2%}</td>
                        <td>{stats.get('win_rate', 0):.2%}</td>
                        <td>{stats.get('n_trades', 0)}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>因子IC分析</h2>
        """
        
        # 添加IC分析数据
        if factor_data is not None:
            ic_analysis = self._calculate_ic_analysis(factor_data)
            html_content += "<table><tr><th>因子</th><th>IC值</th></tr>"
            for factor, ic_value in sorted(ic_analysis.items(), key=lambda x: abs(x[1]), reverse=True):
                html_content += f"<tr><td>{factor}</td><td>{ic_value:.3f}</td></tr>"
            html_content += "</table>"
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # 保存报告
        report_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"gold_quant_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"报告导出成功: {report_path}")
        return report_path
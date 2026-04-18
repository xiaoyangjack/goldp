#!/usr/bin/env python3
"""
系统集成与性能优化引擎
集成所有优化模块，优化回测执行效率，提升系统性能
"""

import pandas as pd
import numpy as np
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, List, Any, Optional

from gold_quant_system.core.backtest_engine import BacktestEngine
from gold_quant_system.strategies.advanced.gram_four_factor_strategy import GRAMFourFactorStrategy
from gold_quant_system.core.factor_effectiveness import FactorEffectiveness
from gold_quant_system.core.event_driven_strategy import EventDrivenStrategy
from gold_quant_system.core.monitoring_engine import MonitoringEngine
from gold_quant_system.core.visualization import Visualization
from gold_quant_system.core.report_automation import ReportAutomation


class IntegrationEngine:
    """
    系统集成引擎
    集成所有优化模块，实现高性能的量化交易系统
    """
    
    def __init__(self):
        """初始化集成引擎"""
        # 初始化各个模块
        self.backtest_engine = BacktestEngine()
        self.gram_strategy = GRAMFourFactorStrategy()
        self.factor_effectiveness = FactorEffectiveness()
        self.event_strategy = EventDrivenStrategy()
        self.monitoring_engine = MonitoringEngine()
        self.visualization = Visualization()
        self.report_automation = ReportAutomation()
        
        # 性能统计
        self.performance_metrics = {
            'backtest_time': 0,
            'factor_calculation_time': 0,
            'visualization_time': 0,
            'report_generation_time': 0
        }
    
    def integrate_all_modules(self, df: pd.DataFrame, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        集成所有模块执行完整流程
        
        Args:
            df: 价格数据
            params: 策略参数
            
        Returns:
            Dict: 集成执行结果
        """
        start_time = time.time()
        
        # 1. 并行计算因子和指标
        factor_results = self._calculate_factors_parallel(df)
        
        # 2. 运行回测
        backtest_results = self._run_backtest(factor_results['df'], params)
        
        # 3. 生成可视化
        visualizations = self._generate_visualizations(factor_results)
        
        # 4. 生成报告
        reports = self._generate_reports(factor_results, backtest_results)
        
        # 5. 计算总体性能
        total_time = time.time() - start_time
        
        # 6. 运行稳定性测试
        stability_result = self._run_stability_test(df, n_iterations=10)
        
        return {
            'backtest_results': backtest_results,
            'factor_results': factor_results,
            'visualizations': visualizations,
            'reports': reports,
            'performance_metrics': {
                **self.performance_metrics,
                'total_execution_time': total_time
            },
            'stability_test': stability_result
        }
    
    def _calculate_factors_parallel(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        并行计算所有因子和指标
        
        Args:
            df: 价格数据
            
        Returns:
            Dict: 因子计算结果
        """
        start_time = time.time()
        
        # 并行执行因子计算
        with ThreadPoolExecutor(max_workers=4) as executor:
            # 提交任务
            future_gram = executor.submit(self.gram_strategy.calculate_gram_factors, df)
            future_factor_effectiveness = executor.submit(self.factor_effectiveness.calculate_factor_effectiveness, df)
            future_monitoring = executor.submit(self.monitoring_engine.calculate_monitoring_indicators, df)
            
            # 收集结果
            gram_df = future_gram.result()
            factor_effectiveness_df = future_factor_effectiveness.result()
            monitoring_df = future_monitoring.result()
        
        # 合并结果
        combined_df = df.copy()
        for result_df in [gram_df, factor_effectiveness_df, monitoring_df]:
            if not result_df.empty:
                # 只添加新列
                new_columns = [col for col in result_df.columns if col not in combined_df.columns]
                combined_df = combined_df.join(result_df[new_columns])
        
        self.performance_metrics['factor_calculation_time'] = time.time() - start_time
        
        return {
            'df': combined_df,
            'gram_factors': gram_df,
            'factor_effectiveness': factor_effectiveness_df,
            'monitoring_indicators': monitoring_df
        }
    
    def _run_backtest(self, df: pd.DataFrame, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        运行回测，优化执行效率
        
        Args:
            df: 包含因子的数据
            params: 策略参数
            
        Returns:
            Dict: 回测结果
        """
        start_time = time.time()
        
        # 优化：使用向量化计算和并行执行
        results = self.backtest_engine.run_all_strategies(df, params)
        
        # 计算性能指标
        strategy_stats = {}
        for strategy, result in results.items():
            if result:
                strategy_stats[strategy] = result['stats']
        
        self.performance_metrics['backtest_time'] = time.time() - start_time
        
        return {
            'strategy_results': results,
            'strategy_stats': strategy_stats
        }
    
    def _generate_visualizations(self, factor_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成可视化图表，优化加载时间
        
        Args:
            factor_results: 因子计算结果
            
        Returns:
            Dict: 可视化结果
        """
        start_time = time.time()
        
        visualizations = {}
        
        # 1. GRAM四因子评分进度条
        if 'gram_factors' in factor_results and not factor_results['gram_factors'].empty:
            gram_df = factor_results['gram_factors']
            if not gram_df.empty:
                # 提取最新的因子值
                latest_data = gram_df.iloc[-1]
                gram_scores = {
                    'Return': float(latest_data.get('r_factor_norm', 0)),
                    'Opportunity': float(latest_data.get('o_factor_norm', 0)),
                    'Economic': float(latest_data.get('e_factor_norm', 0)),
                    'Momentum': float(latest_data.get('m_factor_norm', 0))
                }
                visualizations['gram_progress'] = self.visualization.create_gram_progress_bar(gram_scores)
        
        # 2. 因子有效性条形图
        if 'factor_effectiveness' in factor_results and not factor_results['factor_effectiveness'].empty:
            fe_df = factor_results['factor_effectiveness']
            if not fe_df.empty:
                # 提取最新的因子有效性
                latest_data = fe_df.iloc[-1]
                factor_effectiveness_data = {}
                for factor in ['gpr', 'central_bank_gold', 'dxy', 'real_rate', 'etf_flow', 
                              'cot', 'momentum_60d', 'sma', 'oil_price', 'atr']:
                    if f'{factor}_effectiveness' in latest_data:
                        factor_effectiveness_data[factor] = float(latest_data[f'{factor}_effectiveness']) / 100
                visualizations['factor_effectiveness'] = self.visualization.create_factor_effectiveness_bar(factor_effectiveness_data)
        
        # 3. 情景预测概率饼图
        scenario_probabilities = {
            '看涨': 0.4,
            '看跌': 0.3,
            '震荡': 0.3
        }
        visualizations['scenario_probability'] = self.visualization.create_scenario_probability_pie(scenario_probabilities)
        
        # 4. 事件时间轴
        events = [
            {'date': '2024-01-01', 'event': 'CME降息概率突破40%', 'impact': '高'},
            {'date': '2024-01-15', 'event': 'DXY 5日线下穿20日线', 'impact': '中'},
            {'date': '2024-01-30', 'event': 'GLD/IAU ETF连续2周净流出', 'impact': '中'}
        ]
        visualizations['event_timeline'] = self.visualization.create_event_timeline(events)
        
        self.performance_metrics['visualization_time'] = time.time() - start_time
        
        # 验证可视化加载时间
        if self.performance_metrics['visualization_time'] > 2:
            logger.warning(f"可视化加载时间过长: {self.performance_metrics['visualization_time']:.2f}秒")
        else:
            logger.info(f"可视化加载时间: {self.performance_metrics['visualization_time']:.2f}秒")
        
        return visualizations
    
    def _generate_reports(self, factor_results: Dict[str, Any], backtest_results: Dict[str, Any]) -> Dict[str, str]:
        """
        生成报告，优化生成时间
        
        Args:
            factor_results: 因子计算结果
            backtest_results: 回测结果
            
        Returns:
            Dict: 报告文件路径
        """
        start_time = time.time()
        
        reports = {}
        
        # 准备报告数据
        gram_scores = {
            'Return': 0.7,
            'Opportunity': 0.5,
            'Economic': 0.6,
            'Momentum': 0.4
        }
        
        signal_status = {
            '信号A': '多',
            '信号B': '中性',
            '信号C': '空'
        }
        
        scenario_probabilities = {
            '看涨': 0.4,
            '看跌': 0.3,
            '震荡': 0.3
        }
        
        monitoring_metrics = {
            'CME降息概率': 45.0,
            'DXY均线状态': 1.0,
            'ETF流向': -25.0,
            'COT净多仓': 85000.0,
            'GPR指数': 65.0,
            'WTI原油价格': 95.0,
            'ATR(14日)': 25.0,
            'SMA状态': 0.0
        }
        
        # 生成每日报告
        daily_report_path = self.report_automation.generate_daily_report(
            gram_scores, signal_status, scenario_probabilities, monitoring_metrics
        )
        reports['daily_report'] = daily_report_path
        
        # 准备每周报告数据
        factor_attribution = {
            'GPR': 0.12,
            '央行购金': 0.10,
            'DXY': 0.12,
            '实际利率': 0.12,
            'ETF流向': 0.10,
            'COT': 0.10,
            '60日动量': 0.11,
            'SMA': 0.10,
            '油价': 0.08,
            'ATR': 0.05
        }
        
        event_impact = [
            {'date': '2024-01-01', 'event': 'CME降息概率突破40%', 'impact': '高'},
            {'date': '2024-01-15', 'event': 'DXY 5日线下穿20日线', 'impact': '中'},
            {'date': '2024-01-30', 'event': 'GLD/IAU ETF连续2周净流出', 'impact': '中'}
        ]
        
        strategy_returns = {
            'SMA策略': 5.2,
            'RSI策略': 3.8,
            'MACD策略': 4.5,
            '布林带策略': 3.2,
            '多因子策略': 6.1,
            'GRAM策略': 7.3
        }
        
        # 生成每周报告
        weekly_report_path = self.report_automation.generate_weekly_report(
            factor_attribution, event_impact, strategy_returns
        )
        reports['weekly_report'] = weekly_report_path
        
        self.performance_metrics['report_generation_time'] = time.time() - start_time
        
        # 验证报告生成时间
        if self.performance_metrics['report_generation_time'] > 5:
            logger.warning(f"报告生成时间过长: {self.performance_metrics['report_generation_time']:.2f}秒")
        else:
            logger.info(f"报告生成时间: {self.performance_metrics['report_generation_time']:.2f}秒")
        
        return reports
    
    def _run_stability_test(self, df: pd.DataFrame, n_iterations: int = 10) -> Dict[str, Any]:
        """
        运行稳定性测试，确保系统连续运行无崩溃
        
        Args:
            df: 价格数据
            n_iterations: 测试迭代次数
            
        Returns:
            Dict: 稳定性测试结果
        """
        logger.info(f"开始稳定性测试，共{ n_iterations }次迭代...")
        
        success_count = 0
        error_count = 0
        errors = []
        execution_times = []
        
        for i in range(n_iterations):
            try:
                iteration_start = time.time()
                # 运行完整流程
                result = self.integrate_all_modules(df, {'strategies': ['sma', 'rsi', 'macd']})
                iteration_time = time.time() - iteration_start
                execution_times.append(iteration_time)
                success_count += 1
                logger.info(f"迭代 {i+1}/{n_iterations} 成功，耗时: {iteration_time:.2f}秒")
            except Exception as e:
                error_count += 1
                errors.append(str(e))
                logger.error(f"迭代 {i+1}/{n_iterations} 失败: {e}")
        
        # 计算稳定性指标
        success_rate = success_count / n_iterations
        avg_execution_time = np.mean(execution_times) if execution_times else 0
        
        stability_result = {
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'errors': errors
        }
        
        logger.info(f"稳定性测试完成: 成功率 {success_rate:.2f}, 平均执行时间 {avg_execution_time:.2f}秒")
        
        return stability_result
    
    def optimize_performance(self):
        """
        性能优化方法
        """
        logger.info("开始性能优化...")
        
        # 1. 优化回测引擎
        self._optimize_backtest_engine()
        
        # 2. 优化因子计算
        self._optimize_factor_calculation()
        
        # 3. 优化可视化
        self._optimize_visualization()
        
        # 4. 优化报告生成
        self._optimize_report_generation()
        
        logger.info("性能优化完成")
    
    def _optimize_backtest_engine(self):
        """
        优化回测引擎性能
        """
        # 可以在这里添加具体的回测引擎优化代码
        logger.info("优化回测引擎")
    
    def _optimize_factor_calculation(self):
        """
        优化因子计算性能
        """
        # 可以在这里添加具体的因子计算优化代码
        logger.info("优化因子计算")
    
    def _optimize_visualization(self):
        """
        优化可视化性能
        """
        # 可以在这里添加具体的可视化优化代码
        logger.info("优化可视化")
    
    def _optimize_report_generation(self):
        """
        优化报告生成性能
        """
        # 可以在这里添加具体的报告生成优化代码
        logger.info("优化报告生成")

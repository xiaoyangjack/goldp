#!/usr/bin/env python3
"""
报告自动化模块
实现每日和每周报告的自动生成
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

from gold_quant_system.core.visualization import Visualization
from gold_quant_system.core.report_templates import ReportTemplates


class ReportAutomation:
    """报告自动化管理器"""
    
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or Path.home() / "Downloads" / "GoldQuant_Reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.visualization = Visualization()
        self.report_templates = ReportTemplates()
        logger.info(f"报告自动化输出目录: {self.output_dir}")
    
    def generate_daily_report(self, gram_scores: Dict[str, float], signal_status: Dict[str, str],
                             scenario_probabilities: Dict[str, float], monitoring_metrics: Dict[str, float]) -> str:
        """
        生成每日极简报告
        内容包括：因子净驱动评分 + 信号触发状态 + 情景概率 + 监控指标读数
        
        Args:
            gram_scores: GRAM四因子评分
            signal_status: 信号触发状态
            scenario_probabilities: 情景概率
            monitoring_metrics: 监控指标读数
            
        Returns:
            str: 保存的报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"GoldQuant_Daily_Report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        # 生成可视化图表
        gram_fig = self.visualization.create_gram_progress_bar(gram_scores)
        scenario_fig = self.visualization.create_scenario_probability_pie(scenario_probabilities)
        
        # 保存图表为HTML
        gram_chart_path = self.visualization.save_figure(gram_fig, f"gram_chart_{timestamp}.html", self.output_dir)
        scenario_chart_path = self.visualization.save_figure(scenario_fig, f"scenario_chart_{timestamp}.html", self.output_dir)
        
        # 生成HTML报告
        html_content = self._generate_daily_report_html(
            gram_scores, signal_status, scenario_probabilities, monitoring_metrics,
            gram_chart_path, scenario_chart_path
        )
        
        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"每日报告已生成: {filepath}")
        return str(filepath)
    
    def generate_weekly_report(self, factor_attribution: Dict[str, float], event_impact: List[Dict[str, Any]],
                              strategy_returns: Dict[str, float]) -> str:
        """
        生成每周深度报告
        内容包括：因子归因 + 事件影响 + 策略收益
        
        Args:
            factor_attribution: 因子归因数据
            event_impact: 事件影响数据
            strategy_returns: 策略收益数据
            
        Returns:
            str: 保存的报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"GoldQuant_Weekly_Report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        # 生成可视化图表
        factor_fig = self.visualization.create_factor_effectiveness_bar(factor_attribution)
        event_fig = self.visualization.create_event_timeline(event_impact)
        
        # 保存图表为HTML
        factor_chart_path = self.visualization.save_figure(factor_fig, f"factor_chart_{timestamp}.html", self.output_dir)
        event_chart_path = self.visualization.save_figure(event_fig, f"event_chart_{timestamp}.html", self.output_dir)
        
        # 生成HTML报告
        html_content = self._generate_weekly_report_html(
            factor_attribution, event_impact, strategy_returns,
            factor_chart_path, event_chart_path
        )
        
        # 保存报告
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"每周报告已生成: {filepath}")
        return str(filepath)
    
    def _generate_daily_report_html(self, gram_scores: Dict[str, float], signal_status: Dict[str, str],
                                   scenario_probabilities: Dict[str, float], monitoring_metrics: Dict[str, float],
                                   gram_chart_path: str, scenario_chart_path: str) -> str:
        """
        生成每日报告的HTML内容
        """
        # 读取图表HTML内容
        with open(gram_chart_path, 'r', encoding='utf-8') as f:
            gram_chart_html = f.read()
        
        with open(scenario_chart_path, 'r', encoding='utf-8') as f:
            scenario_chart_html = f.read()
        
        # 信号状态颜色映射
        signal_colors = {
            '多': '#22c55e',
            '空': '#ef4444',
            '中性': '#f59e0b'
        }
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GoldQuant 每日报告 - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: #0f0f10;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1, h2, h3 {{
                    color: #ffffff;
                }}
                .section {{
                    background-color: #1a1a1c;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .metric-card {{
                    background-color: #252529;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .metric-label {{
                    font-size: 14px;
                    color: #6b7280;
                }}
                .signal-status {{
                    display: inline-block;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                }}
                .chart-container {{
                    margin: 20px 0;
                }}
                .timestamp {{
                    color: #6b7280;
                    font-size: 14px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 GoldQuant 每日极简报告</h1>
                <div class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                
                <!-- GRAM四因子评分 -->
                <div class="section">
                    <h2>🎯 GRAM四因子评分</h2>
                    <div class="chart-container">
                        {gram_chart_html}
                    </div>
                </div>
                
                <!-- 信号触发状态 -->
                <div class="section">
                    <h2>🚨 信号触发状态</h2>
                    <div class="grid">
                        {''.join([f"""
                        <div class="metric-card">
                            <div class="metric-label">{signal}</div>
                            <div class="signal-status" style="background-color: {signal_colors.get(status, '#6b7280')}">
                                {status}
                            </div>
                        </div>
                        """ for signal, status in signal_status.items()])}
                    </div>
                </div>
                
                <!-- 情景概率 -->
                <div class="section">
                    <h2>📈 情景预测概率</h2>
                    <div class="chart-container">
                        {scenario_chart_html}
                    </div>
                </div>
                
                <!-- 监控指标读数 -->
                <div class="section">
                    <h2>📊 监控指标读数</h2>
                    <div class="grid">
                        {''.join([f"""
                        <div class="metric-card">
                            <div class="metric-label">{metric}</div>
                            <div class="metric-value">{value:.2f}</div>
                        </div>
                        """ for metric, value in monitoring_metrics.items()])}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_weekly_report_html(self, factor_attribution: Dict[str, float], event_impact: List[Dict[str, Any]],
                                    strategy_returns: Dict[str, float], factor_chart_path: str, event_chart_path: str) -> str:
        """
        生成每周报告的HTML内容
        """
        # 读取图表HTML内容
        with open(factor_chart_path, 'r', encoding='utf-8') as f:
            factor_chart_html = f.read()
        
        with open(event_chart_path, 'r', encoding='utf-8') as f:
            event_chart_html = f.read()
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GoldQuant 每周深度报告 - {datetime.now().strftime('%Y-%m-%d')}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: #0f0f10;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                h1, h2, h3 {{
                    color: #ffffff;
                }}
                .section {{
                    background-color: #1a1a1c;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .metric-card {{
                    background-color: #252529;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .metric-label {{
                    font-size: 14px;
                    color: #6b7280;
                }}
                .chart-container {{
                    margin: 20px 0;
                }}
                .timestamp {{
                    color: #6b7280;
                    font-size: 14px;
                    margin-bottom: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #374151;
                }}
                th {{
                    background-color: #252529;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 GoldQuant 每周深度报告</h1>
                <div class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                
                <!-- 因子归因 -->
                <div class="section">
                    <h2>🔍 因子归因分析</h2>
                    <div class="chart-container">
                        {factor_chart_html}
                    </div>
                </div>
                
                <!-- 事件影响 -->
                <div class="section">
                    <h2>📅 事件影响分析</h2>
                    <div class="chart-container">
                        {event_chart_html}
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>日期</th>
                                <th>事件</th>
                                <th>影响程度</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f"""
                            <tr>
                                <td>{event['date']}</td>
                                <td>{event['event']}</td>
                                <td>{event['impact']}</td>
                            </tr>
                            """ for event in event_impact])}
                        </tbody>
                    </table>
                </div>
                
                <!-- 策略收益 -->
                <div class="section">
                    <h2>💰 策略收益分析</h2>
                    <div class="grid">
                        {''.join([f"""
                        <div class="metric-card">
                            <div class="metric-label">{strategy}</div>
                            <div class="metric-value">{return_value:.2f}%</div>
                        </div>
                        """ for strategy, return_value in strategy_returns.items()])}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def schedule_reports(self):
        """
        调度报告生成
        实际使用时可以结合定时任务系统
        """
        logger.info("开始调度报告生成...")
        
        # 这里可以集成到系统的定时任务中
        # 例如使用APScheduler或系统的cron
        
        logger.info("报告调度完成")

#!/usr/bin/env python3
"""
数据可视化模块
支持GRAM四因子评分进度条、全因子有效性条形图、事件时间轴、情景预测概率饼图
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List


class Visualization:
    """数据可视化管理器"""
    
    def __init__(self):
        # 暗黑主题配色
        self.theme = {
            'background': '#0f0f10',
            'text': '#ffffff',
            'bull': '#22c55e',  # 多信号颜色
            'bear': '#ef4444',   # 空信号颜色
            'neutral': '#f59e0b',  # 中性信号颜色
            'grid': '#374151',
            'secondary': '#6b7280'
        }
    
    def create_gram_progress_bar(self, gram_scores: Dict[str, float]) -> go.Figure:
        """
        创建GRAM四因子评分进度条
        
        Args:
            gram_scores: GRAM四因子评分，格式为 {'Growth': 0.7, 'Risk': 0.3, 'Momentum': 0.8, 'Value': 0.5}
            
        Returns:
            go.Figure: 进度条图表
        """
        factors = list(gram_scores.keys())
        scores = list(gram_scores.values())
        
        # 根据分数确定颜色
        colors = []
        for score in scores:
            if score >= 0.6:
                colors.append(self.theme['bull'])
            elif score <= 0.4:
                colors.append(self.theme['bear'])
            else:
                colors.append(self.theme['neutral'])
        
        fig = go.Figure()
        
        for i, (factor, score, color) in enumerate(zip(factors, scores, colors)):
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=score * 100,
                title={'text': factor, 'font': {'color': self.theme['text']}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': self.theme['text']},
                    'bar': {'color': color},
                    'bgcolor': self.theme['background'],
                    'borderwidth': 1,
                    'bordercolor': self.theme['grid'],
                    'steps': [
                        {'range': [0, 40], 'color': self.theme['bear']},
                        {'range': [40, 60], 'color': self.theme['neutral']},
                        {'range': [60, 100], 'color': self.theme['bull']}
                    ],
                    'threshold': {
                        'line': {'color': self.theme['text'], 'width': 2},
                        'thickness': 0.75,
                        'value': score * 100
                    }
                },
                domain={'row': i // 2, 'column': i % 2}
            ))
        
        fig.update_layout(
            grid={'rows': 2, 'columns': 2},
            paper_bgcolor=self.theme['background'],
            plot_bgcolor=self.theme['background'],
            font={'color': self.theme['text']},
            title={'text': 'GRAM四因子评分', 'font': {'color': self.theme['text']}}
        )
        
        return fig
    
    def create_factor_effectiveness_bar(self, factor_effectiveness: Dict[str, float]) -> go.Figure:
        """
        创建全因子有效性条形图
        
        Args:
            factor_effectiveness: 因子有效性数据，格式为 {'Factor1': 0.7, 'Factor2': 0.4, ...}
            
        Returns:
            go.Figure: 条形图图表
        """
        factors = list(factor_effectiveness.keys())
        effectiveness = list(factor_effectiveness.values())
        
        # 根据有效性值确定颜色
        colors = []
        for value in effectiveness:
            if value >= 0.6:
                colors.append(self.theme['bull'])
            elif value <= 0.4:
                colors.append(self.theme['bear'])
            else:
                colors.append(self.theme['neutral'])
        
        fig = go.Figure(data=[
            go.Bar(
                x=factors,
                y=effectiveness,
                marker_color=colors,
                text=[f"{v:.2f}" for v in effectiveness],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            paper_bgcolor=self.theme['background'],
            plot_bgcolor=self.theme['background'],
            font={'color': self.theme['text']},
            title={'text': '全因子有效性分析', 'font': {'color': self.theme['text']}},
            xaxis={'color': self.theme['text'], 'gridcolor': self.theme['grid']},
            yaxis={'color': self.theme['text'], 'gridcolor': self.theme['grid'], 'range': [0, 1]},
            margin={'l': 40, 'r': 40, 't': 60, 'b': 40}
        )
        
        return fig
    
    def create_event_timeline(self, events: List[Dict[str, Any]]) -> go.Figure:
        """
        创建事件时间轴图表
        
        Args:
            events: 事件数据，格式为 [{'date': '2024-01-01', 'event': '事件1', 'impact': '高'},
                                      {'date': '2024-01-15', 'event': '事件2', 'impact': '中'}]
            
        Returns:
            go.Figure: 时间轴图表
        """
        # 转换日期格式
        for event in events:
            if isinstance(event['date'], str):
                event['date'] = datetime.strptime(event['date'], '%Y-%m-%d')
        
        # 按日期排序
        events.sort(key=lambda x: x['date'])
        
        # 提取数据
        dates = [event['date'] for event in events]
        event_names = [event['event'] for event in events]
        impacts = [event['impact'] for event in events]
        
        # 根据影响程度确定颜色
        impact_colors = {
            '高': self.theme['bear'],
            '中': self.theme['neutral'],
            '低': self.theme['bull']
        }
        colors = [impact_colors.get(impact, self.theme['secondary']) for impact in impacts]
        
        fig = go.Figure()
        
        # 添加时间轴
        fig.add_trace(go.Scatter(
            x=dates,
            y=[1] * len(dates),
            mode='markers+text',
            marker=dict(
                size=15,
                color=colors,
                line=dict(width=2, color=self.theme['background'])
            ),
            text=event_names,
            textposition='top center',
            textfont=dict(color=self.theme['text'])
        ))
        
        # 添加连接线
        fig.add_trace(go.Scatter(
            x=dates,
            y=[1] * len(dates),
            mode='lines',
            line=dict(color=self.theme['grid'], width=2),
            showlegend=False
        ))
        
        fig.update_layout(
            paper_bgcolor=self.theme['background'],
            plot_bgcolor=self.theme['background'],
            font={'color': self.theme['text']},
            title={'text': '事件时间轴', 'font': {'color': self.theme['text']}},
            xaxis={'color': self.theme['text'], 'gridcolor': self.theme['grid']},
            yaxis={'showticklabels': False, 'showgrid': False},
            margin={'l': 40, 'r': 40, 't': 60, 'b': 40},
            height=300
        )
        
        return fig
    
    def create_scenario_probability_pie(self, scenario_probabilities: Dict[str, float]) -> go.Figure:
        """
        创建情景预测的概率饼图
        
        Args:
            scenario_probabilities: 情景概率数据，格式为 {'看涨': 0.4, '看跌': 0.3, '震荡': 0.3}
            
        Returns:
            go.Figure: 饼图图表
        """
        scenarios = list(scenario_probabilities.keys())
        probabilities = list(scenario_probabilities.values())
        
        # 定义情景颜色
        scenario_colors = {
            '看涨': self.theme['bull'],
            '看跌': self.theme['bear'],
            '震荡': self.theme['neutral'],
            '牛市': self.theme['bull'],
            '熊市': self.theme['bear'],
            '横盘': self.theme['neutral']
        }
        
        # 为每个情景分配颜色
        colors = []
        for scenario in scenarios:
            if scenario in scenario_colors:
                colors.append(scenario_colors[scenario])
            else:
                colors.append(self.theme['secondary'])
        
        fig = go.Figure(data=[go.Pie(
            labels=scenarios,
            values=probabilities,
            textinfo='label+percent',
            textfont=dict(color=self.theme['text']),
            marker=dict(colors=colors, line=dict(color=self.theme['background'], width=2))
        )])
        
        fig.update_layout(
            paper_bgcolor=self.theme['background'],
            plot_bgcolor=self.theme['background'],
            font={'color': self.theme['text']},
            title={'text': '情景预测概率', 'font': {'color': self.theme['text']}},
            margin={'l': 40, 'r': 40, 't': 60, 'b': 40}
        )
        
        return fig
    
    def save_figure(self, fig: go.Figure, filename: str, directory: str = './') -> str:
        """
        保存图表为HTML文件
        
        Args:
            fig: 图表对象
            filename: 文件名
            directory: 保存目录
            
        Returns:
            str: 保存的文件路径
        """
        import os
        
        # 确保目录存在
        os.makedirs(directory, exist_ok=True)
        
        # 保存为HTML文件
        filepath = os.path.join(directory, filename)
        fig.write_html(filepath)
        
        return filepath

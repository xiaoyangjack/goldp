#!/usr/bin/env python3
"""
黄金量化本地研究系统图表面板

实现中间图表展示区域，包含多个标签页和各种图表
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import mplcursors
import pandas as pd
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False


class ChartPanel(QWidget):
    """
    图表面板类
    """
    
    def __init__(self):
        super().__init__()
        
        # 创建布局
        self._create_layout()
    
    def _create_layout(self):
        """
        创建布局
        """
        main_layout = QVBoxLayout(self)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 净值曲线对比
        self.nav_tab = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_tab)
        self.nav_figure = Figure(figsize=(8, 6))
        self.nav_canvas = FigureCanvas(self.nav_figure)
        self.nav_layout.addWidget(self.nav_canvas)
        self.tab_widget.addTab(self.nav_tab, "净值曲线对比")
        
        # 年度收益柱状图
        self.annual_tab = QWidget()
        self.annual_layout = QVBoxLayout(self.annual_tab)
        self.annual_figure = Figure(figsize=(8, 6))
        self.annual_canvas = FigureCanvas(self.annual_figure)
        self.annual_layout.addWidget(self.annual_canvas)
        self.tab_widget.addTab(self.annual_tab, "年度收益柱状图")
        
        # 水下回撤图
        self.drawdown_tab = QWidget()
        self.drawdown_layout = QVBoxLayout(self.drawdown_tab)
        self.drawdown_figure = Figure(figsize=(8, 6))
        self.drawdown_canvas = FigureCanvas(self.drawdown_figure)
        self.drawdown_layout.addWidget(self.drawdown_canvas)
        self.tab_widget.addTab(self.drawdown_tab, "水下回撤图")
        
        # IC因子排名
        self.ic_tab = QWidget()
        self.ic_layout = QVBoxLayout(self.ic_tab)
        self.ic_figure = Figure(figsize=(8, 6))
        self.ic_canvas = FigureCanvas(self.ic_figure)
        self.ic_layout.addWidget(self.ic_canvas)
        self.tab_widget.addTab(self.ic_tab, "IC因子排名")
        
        # 参数热图
        self.param_tab = QWidget()
        self.param_layout = QVBoxLayout(self.param_tab)
        self.param_figure = Figure(figsize=(8, 6))
        self.param_canvas = FigureCanvas(self.param_figure)
        self.param_layout.addWidget(self.param_canvas)
        self.tab_widget.addTab(self.param_tab, "参数热图")
        
        # 相关性热力图
        self.correlation_tab = QWidget()
        self.correlation_layout = QVBoxLayout(self.correlation_tab)
        self.correlation_figure = Figure(figsize=(8, 6))
        self.correlation_canvas = FigureCanvas(self.correlation_figure)
        self.correlation_layout.addWidget(self.correlation_canvas)
        self.tab_widget.addTab(self.correlation_tab, "相关性热力图")
        
        main_layout.addWidget(self.tab_widget)
    
    def update_charts(self, backtest_results, analysis_results, factor_data):
        """
        更新所有图表
        """
        if backtest_results is None:
            return
        
        # 更新净值曲线
        self._update_nav_chart(backtest_results)
        
        # 更新年度收益
        self._update_annual_chart(backtest_results)
        
        # 更新水下回撤
        self._update_drawdown_chart(backtest_results)
        
        # 更新IC因子排名
        if analysis_results and "ic_analysis" in analysis_results:
            self._update_ic_chart(analysis_results["ic_analysis"])
        
        # 更新参数热图
        if analysis_results and "param_heatmap" in analysis_results:
            self._update_param_heatmap(analysis_results["param_heatmap"])
        
        # 更新相关性热力图
        if analysis_results and "correlation_matrix" in analysis_results:
            self._update_correlation_heatmap(analysis_results["correlation_matrix"])
    
    def _update_nav_chart(self, backtest_results):
        """
        更新净值曲线图表
        """
        self.nav_figure.clear()
        ax = self.nav_figure.add_subplot(111)
        
        # 设置图表样式
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for strategy_name, result in backtest_results.items():
            portfolio_values = result["portfolio_values"]
            ax.plot(portfolio_values.index, portfolio_values, label=strategy_name, linewidth=2)
        
        # 设置字体和标签
        ax.set_title("策略净值曲线对比", fontsize=14, fontweight='bold')
        ax.set_xlabel("日期", fontsize=12)
        ax.set_ylabel("净值", fontsize=12)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=10, frameon=False)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        # 添加tooltip
        mplcursors.cursor(ax, hover=True).connect("add", lambda sel: sel.annotation.set_text(
            f"日期: {portfolio_values.index[np.argmin(np.abs(portfolio_values.index.astype('O') - sel.target[0]))].strftime('%Y-%m-%d')}\n净值: {sel.target[1]:.2f}"
        ))
        
        # 调整布局
        self.nav_figure.tight_layout()
        self.nav_canvas.draw()
    
    def _update_annual_chart(self, backtest_results):
        """
        更新年度收益柱状图
        """
        self.annual_figure.clear()
        ax = self.annual_figure.add_subplot(111)
        
        # 设置图表样式
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # 计算年度收益
        annual_returns = {}
        for strategy_name, result in backtest_results.items():
            portfolio_values = result["portfolio_values"]
            # 按年重采样
            yearly = portfolio_values.resample('A').last()
            yearly_returns = yearly.pct_change().dropna()
            annual_returns[strategy_name] = yearly_returns
        
        # 准备数据
        years = sorted(set(year for returns in annual_returns.values() for year in returns.index.year))
        strategies = list(annual_returns.keys())
        
        # 绘制柱状图
        width = 0.8 / len(strategies)
        for i, strategy in enumerate(strategies):
            returns = annual_returns[strategy]
            x = np.arange(len(years)) + i * width
            y = [returns.get(pd.Timestamp(f"{year}-12-31"), 0) for year in years]
            ax.bar(x, y, width=width, label=strategy, alpha=0.8)
        
        # 设置字体和标签
        ax.set_title("策略年度收益", fontsize=14, fontweight='bold')
        ax.set_xlabel("年份", fontsize=12)
        ax.set_ylabel("收益率", fontsize=12)
        ax.tick_params(axis='both', labelsize=10)
        ax.set_xticks(np.arange(len(years)) + width * (len(strategies) - 1) / 2)
        ax.set_xticklabels(years, fontsize=10)
        ax.legend(fontsize=10, frameon=False)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        # 添加百分比标签
        for i, strategy in enumerate(strategies):
            returns = annual_returns[strategy]
            x = np.arange(len(years)) + i * width
            y = [returns.get(pd.Timestamp(f"{year}-12-31"), 0) for year in years]
            for j, (xi, yi) in enumerate(zip(x, y)):
                ax.text(xi, yi, f"{yi:.1%}", ha='center', va='bottom' if yi >= 0 else 'top', fontsize=9)
        
        # 调整布局
        self.annual_figure.tight_layout()
        self.annual_canvas.draw()
    
    def _update_drawdown_chart(self, backtest_results):
        """
        更新水下回撤图
        """
        self.drawdown_figure.clear()
        ax = self.drawdown_figure.add_subplot(111)
        
        # 设置图表样式
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        for strategy_name, result in backtest_results.items():
            portfolio_values = result["portfolio_values"]
            # 计算最大回撤
            rolling_max = portfolio_values.cummax()
            drawdown = (portfolio_values - rolling_max) / rolling_max
            ax.plot(drawdown.index, drawdown, label=strategy_name, linewidth=2)
        
        # 设置字体和标签
        ax.set_title("策略水下回撤", fontsize=14, fontweight='bold')
        ax.set_xlabel("日期", fontsize=12)
        ax.set_ylabel("回撤", fontsize=12)
        ax.tick_params(axis='both', labelsize=10)
        ax.legend(fontsize=10, frameon=False)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        # 添加tooltip
        mplcursors.cursor(ax, hover=True).connect("add", lambda sel: sel.annotation.set_text(
            f"日期: {portfolio_values.index[np.argmin(np.abs(portfolio_values.index.astype('O') - sel.target[0]))].strftime('%Y-%m-%d')}\n回撤: {sel.target[1]:.2%}"
        ))
        
        # 调整布局
        self.drawdown_figure.tight_layout()
        self.drawdown_canvas.draw()
    
    def _update_ic_chart(self, ic_analysis):
        """
        更新IC因子排名图
        """
        self.ic_figure.clear()
        ax = self.ic_figure.add_subplot(111)
        
        # 设置图表样式
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # 排序IC值
        sorted_ic = sorted(ic_analysis.items(), key=lambda x: x[1], reverse=True)
        factors = [item[0] for item in sorted_ic]
        ic_values = [item[1] for item in sorted_ic]
        
        # 绘制条形图
        y_pos = np.arange(len(factors))
        bars = ax.barh(y_pos, ic_values, align='center', alpha=0.8)
        
        # 设置颜色
        for bar, value in zip(bars, ic_values):
            if value > 0.3:
                bar.set_color('#10b981')  # 绿色
            elif value > 0.1:
                bar.set_color('#3b82f6')  # 蓝色
            else:
                bar.set_color('#f59e0b')  # 橙色
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(factors, fontsize=10)
        
        # 设置字体和标签
        ax.set_xlabel("IC值", fontsize=12)
        ax.set_title("因子IC排名", fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', labelsize=10)
        ax.grid(True, alpha=0.2, linestyle='--')
        
        # 添加IC值标签
        for i, v in enumerate(ic_values):
            ax.text(v + 0.01, i, f"{v:.3f}", ha='left', va='center', fontsize=9)
        
        # 调整布局
        self.ic_figure.tight_layout()
        self.ic_canvas.draw()
    
    def _update_param_heatmap(self, param_heatmap):
        """
        更新参数热图
        """
        self.param_figure.clear()
        ax = self.param_figure.add_subplot(111)
        
        # 假设param_heatmap是一个二维数组
        data = param_heatmap["data"]
        x_labels = param_heatmap["x_labels"]
        y_labels = param_heatmap["y_labels"]
        
        # 绘制热图
        im = ax.imshow(data, cmap='viridis', aspect='auto')
        
        # 添加颜色条
        colorbar = self.param_figure.colorbar(im, ax=ax, label='Sharpe Ratio')
        colorbar.ax.tick_params(labelsize=10)
        
        # 设置标签
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_xticklabels(x_labels, fontsize=10)
        ax.set_yticklabels(y_labels, fontsize=10)
        
        # 设置字体和标签
        ax.set_xlabel('SMA Fast', fontsize=12)
        ax.set_ylabel('SMA Slow', fontsize=12)
        ax.set_title('SMA参数敏感性热图', fontsize=14, fontweight='bold')
        ax.tick_params(axis='both', labelsize=10)
        
        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        
        # 添加数值标签
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                text = ax.text(j, i, f"{data[i, j]:.2f}",
                              ha="center", va="center", color="w", fontsize=9)
        
        # 调整布局
        self.param_figure.tight_layout()
        self.param_canvas.draw()
    
    def _update_correlation_heatmap(self, correlation_matrix):
        """
        更新相关性热力图
        """
        self.correlation_figure.clear()
        ax = self.correlation_figure.add_subplot(111)
        
        # 绘制热力图
        im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
        
        # 添加颜色条
        colorbar = self.correlation_figure.colorbar(im, ax=ax, label='Correlation')
        colorbar.ax.tick_params(labelsize=10)
        
        # 设置标签
        strategies = list(correlation_matrix.columns)
        ax.set_xticks(np.arange(len(strategies)))
        ax.set_yticks(np.arange(len(strategies)))
        ax.set_xticklabels(strategies, fontsize=10)
        ax.set_yticklabels(strategies, fontsize=10)
        
        # 设置字体和标签
        ax.set_title('策略相关性热力图', fontsize=14, fontweight='bold')
        ax.tick_params(axis='both', labelsize=10)
        
        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        
        # 添加数值标签
        for i in range(len(strategies)):
            for j in range(len(strategies)):
                value = correlation_matrix.iloc[i, j]
                # 根据值的大小设置文本颜色
                if abs(value) > 0.7:
                    text_color = "w"
                else:
                    text_color = "#333"
                text = ax.text(j, i, f"{value:.2f}",
                              ha="center", va="center", color=text_color, fontsize=9)
        
        # 调整布局
        self.correlation_figure.tight_layout()
        self.correlation_canvas.draw()
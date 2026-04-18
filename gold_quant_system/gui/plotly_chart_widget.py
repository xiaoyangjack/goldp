#!/usr/bin/env python3
"""
黄金量化本地研究系统 - 简化图表组件
"""

import plotly.graph_objects as go
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt6.QtCore import Qt
from loguru import logger

# 尝试导入 WebEngine
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    logger.warning("PyQt6.WebEngineWidgets 不可用，使用简化图表模式")


class PlotlyChartWidget(QWidget):
    """Plotly 图表组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backtest_results = None
        self.analysis_results = None
        self.factor_data = None
        self.chart_tabs = {}
        self._create_ui()
    
    def _create_ui(self):
        """创建 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 图表标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background-color: #0f172a;
            }
            QTabBar::tab {
                background-color: #1e293b;
                color: #94a3b8;
                padding: 8px 16px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #0f172a;
                color: #f8fafc;
            }
        """)
        
        # 图表类型标签页
        chart_types = [
            ('equity', '📈 净值曲线'),
            ('returns', '📊 年度收益'),
            ('drawdown', '📉 回撤曲线'),
            ('ic', '🎯 IC分析'),
            ('heatmap', '🔥 参数热图'),
            ('correlation', '🔗 相关性'),
        ]
        
        for chart_id, chart_name in chart_types:
            if WEBENGINE_AVAILABLE:
                content = QWebEngineView()
                content.setHtml(self._get_empty_html())
            else:
                content = QLabel()
                content.setAlignment(Qt.AlignmentFlag.AlignCenter)
                content.setStyleSheet("""
                    background-color: #0f172a;
                    color: #64748b;
                    font-size: 16px;
                    padding: 40px;
                """)
                content.setText(
                    f"📊 {chart_name}\n\n"
                    "等待回测数据\n\n"
                    "（安装 PyQt6-WebEngine 获得交互式图表）"
                )
            
            self.tab_widget.addTab(content, chart_name)
            self.chart_tabs[chart_id] = content
        
        layout.addWidget(self.tab_widget)
    
    def _get_plotly_theme(self):
        """获取 Plotly 深色主题配置"""
        return {
            'layout': {
                'template': 'plotly_dark',
                'paper_bgcolor': 'rgba(15, 23, 42, 1)',
                'plot_bgcolor': 'rgba(15, 23, 42, 1)',
                'font': {'color': '#f8fafc'},
                'colorway': ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'],
                'xaxis': {'gridcolor': 'rgba(51, 65, 85, 0.5)', 'title_font': {'color': '#94a3b8'}},
                'yaxis': {'gridcolor': 'rgba(51, 65, 85, 0.5)', 'title_font': {'color': '#94a3b8'}},
                'margin': {'l': 60, 'r': 30, 't': 40, 'b': 60},
            },
            'config': {'displayModeBar': True, 'responsive': True}
        }
    
    def _get_loading_html(self):
        """获取加载中状态 HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8">
        <style>
            body { margin: 0; padding: 0; background-color: #0f172a; color: #94a3b8;
                   font-family: sans-serif; display: flex; align-items: center;
                   justify-content: center; min-height: 100vh; }
            .container { text-align: center; padding: 40px; }
            .spinner { width: 48px; height: 48px; margin: 0 auto 24px; border: 4px solid #1e293b;
                       border-top-color: #6366f1; border-radius: 50%;
                       animation: spin 1s linear infinite; }
            @keyframes spin { to { transform: rotate(360deg); } }
            .title { font-size: 20px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; }
            .desc { font-size: 14px; color: #64748b; }
        </style>
        </head>
        <body>
            <div class="container">
                <div class="spinner"></div>
                <div class="title">正在加载图表...</div>
                <div class="desc">请稍候</div>
            </div>
        </body>
        </html>
        """
    
    def _get_error_html(self, message="图表加载失败"):
        """获取错误状态 HTML"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8">
        <style>
            body {{ margin: 0; padding: 0; background-color: #0f172a; color: #94a3b8;
                   font-family: sans-serif; display: flex; align-items: center;
                   justify-content: center; min-height: 100vh; }}
            .container {{ text-align: center; padding: 40px; }}
            .icon {{ font-size: 64px; margin-bottom: 24px; opacity: 0.8; }}
            .title {{ font-size: 20px; font-weight: 600; color: #ef4444; margin-bottom: 12px; }}
            .desc {{ font-size: 14px; color: #64748b; margin-bottom: 24px; }}
            .btn {{ background-color: #6366f1; color: white; border: none; padding: 10px 24px;
                    border-radius: 8px; font-size: 14px; cursor: pointer; }}
            .btn:hover {{ background-color: #4f46e5; }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">⚠️</div>
                <div class="title">加载失败</div>
                <div class="desc">{message}</div>
                <button class="btn" onclick="location.reload()">重试</button>
            </div>
        </body>
        </html>
        """
    
    def _get_empty_html(self):
        """获取空白图表 HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8">
        <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
        <style>
            body { margin: 0; padding: 0; background-color: #0f172a; color: #94a3b8;
                   font-family: sans-serif; display: flex; align-items: center;
                   justify-content: center; min-height: 100vh; }
            .container { text-align: center; padding: 40px; }
            .icon { font-size: 72px; margin-bottom: 24px; opacity: 0.6; }
            .title { font-size: 28px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; }
            .desc { font-size: 14px; color: #64748b; max-width: 300px; line-height: 1.6; }
        </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">📊</div>
                <div class="title">等待回测数据</div>
                <div class="desc">运行回测后，策略表现图表将在这里展示</div>
            </div>
        </body>
        </html>
        """
    
    def update_charts(self, backtest_results, analysis_results, factor_data):
        """更新所有图表"""
        self.backtest_results = backtest_results
        self.analysis_results = analysis_results
        self.factor_data = factor_data
        
        if not backtest_results:
            logger.warning("没有回测结果，跳过图表更新")
            return
        
        # 显示骨架屏
        if WEBENGINE_AVAILABLE:
            loading_html = self._get_loading_html()
            for chart_id in self.chart_tabs:
                self.chart_tabs[chart_id].setHtml(loading_html)
        
        try:
            self._update_equity_chart()
            self._update_returns_chart()
            self._update_drawdown_chart()
            self._update_ic_chart()
            self._update_heatmap_chart()
            self._update_correlation_chart()
            logger.info("图表更新完成")
        except Exception as e:
            logger.error(f"更新图表时发生错误: {e}")
            if WEBENGINE_AVAILABLE:
                error_html = self._get_error_html(str(e))
                for chart_id in self.chart_tabs:
                    self.chart_tabs[chart_id].setHtml(error_html)
    
    def _update_equity_chart(self):
        """更新净值曲线图"""
        try:
            if not self.backtest_results:
                return
            
            if WEBENGINE_AVAILABLE:
                fig = go.Figure()
                colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
                strategy_names = {'sma': 'SMA均线', 'rsi': 'RSI回归', 'macd': 'MACD动量',
                                'bb': '布林带', 'multi': '多因子', 'regime': 'Regime'}
                
                for i, (strategy, result) in enumerate(self.backtest_results.items()):
                    if 'portfolio_values' in result and len(result['portfolio_values']) > 0:
                        portfolio = result['portfolio_values']
                        fig.add_trace(go.Scatter(
                            x=portfolio.index.strftime('%Y-%m-%d').tolist(),
                            y=portfolio.values.tolist(),
                            mode='lines',
                            name=strategy_names.get(strategy, strategy),
                            line=dict(color=colors[i % len(colors)], width=2)
                        ))
                
                fig.update_layout(
                    title=dict(text='📈 策略净值对比', font=dict(size=20, color='#f8fafc'), x=0.5),
                    xaxis_title='日期', yaxis_title='净值 ($)',
                    hovermode='x unified', showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    **self._get_plotly_theme()['layout']
                )
                
                html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=self._get_plotly_theme()['config'])
                self.chart_tabs['equity'].setHtml(html)
            else:
                portfolio = list(self.backtest_results.values())[0].get('portfolio_values', [])
                self.chart_tabs['equity'].setText(
                    f"📈 净值曲线\n\n"
                    f"策略数量: {len(self.backtest_results)}\n"
                    f"数据点: {len(portfolio)}\n\n"
                    f"（安装 PyQt6-WebEngine 获得交互式图表）"
                )
        except Exception as e:
            logger.error(f"更新净值曲线图表失败: {e}")
            if WEBENGINE_AVAILABLE:
                self.chart_tabs['equity'].setHtml(self._get_error_html(str(e)))
    
    def _update_returns_chart(self):
        """更新年度收益柱状图"""
        try:
            if not self.backtest_results:
                return
            
            years = set()
            for result in self.backtest_results.values():
                if 'portfolio_values' in result:
                    years.update(result['portfolio_values'].index.year.tolist())
            
            years = sorted(list(years))
            if not years:
                return
            
            if WEBENGINE_AVAILABLE:
                fig = go.Figure()
                colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
                strategy_names = {'sma': 'SMA均线', 'rsi': 'RSI回归', 'macd': 'MACD动量',
                                'bb': '布林带', 'multi': '多因子', 'regime': 'Regime'}
                
                for i, (strategy, result) in enumerate(self.backtest_results.items()):
                    if 'portfolio_values' in result and len(result['portfolio_values']) > 0:
                        portfolio = result['portfolio_values']
                        yearly_returns = []
                        for year in years:
                            year_data = portfolio[portfolio.index.year == year]
                            if len(year_data) > 1:
                                ret = (year_data.iloc[-1] - year_data.iloc[0]) / year_data.iloc[0] * 100
                                yearly_returns.append(ret)
                            else:
                                yearly_returns.append(0)
                        
                        fig.add_trace(go.Bar(
                            x=years, y=yearly_returns,
                            name=strategy_names.get(strategy, strategy),
                            marker_color=colors[i % len(colors)]
                        ))
                
                fig.update_layout(
                    title=dict(text='📊 年度收益率对比 (%)', font=dict(size=20, color='#f8fafc'), x=0.5),
                    xaxis_title='年份', yaxis_title='收益率 (%)',
                    barmode='group', showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    **self._get_plotly_theme()['layout']
                )
                
                html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=self._get_plotly_theme()['config'])
                self.chart_tabs['returns'].setHtml(html)
            else:
                self.chart_tabs['returns'].setText(
                    f"📊 年度收益\n\n"
                    f"年份范围: {min(years)} - {max(years)}\n"
                    f"策略数量: {len(self.backtest_results)}\n\n"
                    f"（安装 PyQt6-WebEngine 获得交互式图表）"
                )
        except Exception as e:
            logger.error(f"更新年度收益图表失败: {e}")
            if WEBENGINE_AVAILABLE:
                self.chart_tabs['returns'].setHtml(self._get_error_html(str(e)))
    
    def _update_drawdown_chart(self):
        """更新回撤曲线图"""
        try:
            if not self.backtest_results:
                return
            
            if WEBENGINE_AVAILABLE:
                fig = go.Figure()
                colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
                strategy_names = {'sma': 'SMA均线', 'rsi': 'RSI回归', 'macd': 'MACD动量',
                                'bb': '布林带', 'multi': '多因子', 'regime': 'Regime'}
                
                for i, (strategy, result) in enumerate(self.backtest_results.items()):
                    if 'portfolio_values' in result and len(result['portfolio_values']) > 0:
                        portfolio = result['portfolio_values']
                        running_max = portfolio.cummax()
                        drawdown = (portfolio - running_max) / running_max * 100
                        
                        fig.add_trace(go.Scatter(
                            x=drawdown.index.strftime('%Y-%m-%d').tolist(),
                            y=drawdown.values.tolist(),
                            mode='lines',
                            name=strategy_names.get(strategy, strategy),
                            fill='tozeroy',
                            line=dict(color=colors[i % len(colors)], width=1.5)
                        ))
                
                fig.update_layout(
                    title=dict(text='📉 回撤曲线 (%)', font=dict(size=20, color='#f8fafc'), x=0.5),
                    xaxis_title='日期', yaxis_title='回撤 (%)',
                    hovermode='x unified', showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    **self._get_plotly_theme()['layout']
                )
                
                html = fig.to_html(include_plotlyjs='cdn', full_html=False, config=self._get_plotly_theme()['config'])
                self.chart_tabs['drawdown'].setHtml(html)
            else:
                max_drawdowns = []
                for result in self.backtest_results.values():
                    if 'portfolio_values' in result:
                        portfolio = result['portfolio_values']
                        running_max = portfolio.cummax()
                        drawdown = (portfolio - running_max) / running_max
                        max_drawdowns.append(drawdown.min() * 100)
                
                avg_drawdown = sum(max_drawdowns)/len(max_drawdowns) if max_drawdowns else 0
                self.chart_tabs['drawdown'].setText(
                    f"📉 回撤曲线\n\n"
                    f"策略平均最大回撤: {avg_drawdown:.2f}%\n"
                    f"策略数量: {len(self.backtest_results)}\n\n"
                    f"（安装 PyQt6-WebEngine 获得交互式图表）"
                )
        except Exception as e:
            logger.error(f"更新回撤曲线图表失败: {e}")
            if WEBENGINE_AVAILABLE:
                self.chart_tabs['drawdown'].setHtml(self._get_error_html(str(e)))
    
    def _update_ic_chart(self):
        """更新 IC 分析图"""
        self._set_empty_chart('ic')
    
    def _update_heatmap_chart(self):
        """更新参数热图"""
        self._set_empty_chart('heatmap')
    
    def _update_correlation_chart(self):
        """更新相关性热图"""
        self._set_empty_chart('correlation')
    
    def _set_empty_chart(self, chart_id):
        """设置空图表"""
        if WEBENGINE_AVAILABLE:
            self.chart_tabs[chart_id].setHtml(self._get_empty_html())
        else:
            self.chart_tabs[chart_id].setText(
                f"📊 暂无数据\n\n"
                f"（安装 PyQt6-WebEngine 获得交互式图表）"
            )

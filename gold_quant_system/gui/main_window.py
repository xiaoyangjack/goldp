#!/usr/bin/env python3
"""
黄金量化本地研究系统主窗口

实现三栏布局：参数区、图表区、绩效指标
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QPushButton, QLabel, QStatusBar, QTabWidget, 
    QSplitter, QComboBox, QDateTimeEdit, QProgressBar,
    QScrollArea, QFrame
)
from PyQt6.QtCore import QDate, Qt, QTimer
from gui.param_panel import ParamPanel
from gui.chart_panel import ChartPanel
from gui.stats_panel import StatsPanel
from gui.data_status_panel import DataStatusPanel
from gui.backtest_thread import BacktestThread
from core.data_engine import DataEngine
from core.factor_engine import FactorEngine
from core.backtest_engine import BacktestEngine
from core.analytics_engine import AnalyticsEngine
from core.cache_manager import get_cache_manager


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    
    def __init__(self):
        super().__init__()
        
        # 初始化引擎
        self.data_engine = DataEngine()
        self.factor_engine = FactorEngine()
        self.backtest_engine = BacktestEngine()
        self.analytics_engine = AnalyticsEngine()
        self.cache_manager = get_cache_manager()
        
        # 初始化数据和结果
        self.price_data = None
        self.factor_data = None
        self.backtest_results = None
        
        # 设置窗口标题和大小
        self.setWindowTitle("黄金量化本地研究系统 v2.0")
        self.resize(1600, 1000)
        self.setMinimumSize(1200, 800)
        
        # 创建主布局
        self._create_main_layout()
        
        # 创建状态栏
        self._create_status_bar()
        
        # 初始化默认数据
        self._initialize_data()
    
    def _create_main_layout(self):
        """
        创建主布局
        """
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主水平布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # 工具栏
        toolbar = QWidget()
        toolbar.setMinimumHeight(60)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setSpacing(16)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧控件组
        left_group = QWidget()
        left_layout = QHBoxLayout(left_group)
        left_layout.setSpacing(12)
        
        # 数据源选择
        left_layout.addWidget(QLabel("📈 数据源:"))
        self.ticker_combo = QComboBox()
        self.ticker_combo.addItems(["GC=F (黄金期货)", "GLD (黄金ETF)"])
        self.ticker_combo.setMinimumWidth(180)
        self.ticker_combo.setMaximumWidth(200)
        left_layout.addWidget(self.ticker_combo)
        
        # 日期范围选择
        left_layout.addWidget(QLabel("📅 开始日期:"))
        self.start_date_edit = QDateTimeEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate(2020, 1, 1))
        self.start_date_edit.setFixedWidth(150)
        left_layout.addWidget(self.start_date_edit)
        
        left_layout.addWidget(QLabel("结束日期:"))
        self.end_date_edit = QDateTimeEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setFixedWidth(150)
        left_layout.addWidget(self.end_date_edit)
        
        toolbar_layout.addWidget(left_group)
        
        # 添加弹性空间
        toolbar_layout.addStretch()
        
        # 右侧控件组
        right_group = QWidget()
        right_layout = QHBoxLayout(right_group)
        right_layout.setSpacing(12)
        
        # 进度条
        right_layout.addWidget(QLabel("进度:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(180)
        right_layout.addWidget(self.progress_bar)
        
        # 运行回测按钮
        self.run_button = QPushButton("▶️ 运行回测")
        self.run_button.clicked.connect(self.run_backtest)
        self.run_button.setFixedWidth(120)
        right_layout.addWidget(self.run_button)
        
        # 重置参数按钮
        self.reset_button = QPushButton("🔄 重置")
        self.reset_button.setProperty("secondary", "true")
        self.reset_button.clicked.connect(self.reset_parameters)
        self.reset_button.setFixedWidth(80)
        right_layout.addWidget(self.reset_button)
        
        # 导出报告按钮
        self.export_button = QPushButton("📊 导出报告")
        self.export_button.setProperty("secondary", "true")
        self.export_button.clicked.connect(self.export_report)
        self.export_button.setFixedWidth(100)
        right_layout.addWidget(self.export_button)
        
        toolbar_layout.addWidget(right_group)
        
        main_layout.addWidget(toolbar)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(10)
        main_splitter.setChildrenCollapsible(False)
        
        # 左侧面板 - 使用滚动区域包装参数面板和数据状态面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 数据状态面板 - 使用滚动区域
        data_status_scroll = QScrollArea()
        data_status_scroll.setWidgetResizable(True)
        data_status_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.data_status_panel = DataStatusPanel()
        self.data_status_panel.refresh_data.connect(self._on_refresh_data)
        self.data_status_panel.clear_cache.connect(self._on_clear_cache)
        self.data_status_panel.setMinimumHeight(200)
        data_status_scroll.setWidget(self.data_status_panel)
        left_layout.addWidget(data_status_scroll)
        
        # 参数面板 - 使用滚动区域
        param_scroll = QScrollArea()
        param_scroll.setWidgetResizable(True)
        param_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.param_panel = ParamPanel()
        param_scroll.setWidget(self.param_panel)
        left_layout.addWidget(param_scroll)
        
        main_splitter.addWidget(left_widget)
        
        # 中间图表面板 - 使用滚动区域
        chart_scroll = QScrollArea()
        chart_scroll.setWidgetResizable(True)
        chart_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.chart_panel = ChartPanel()
        chart_scroll.setWidget(self.chart_panel)
        main_splitter.addWidget(chart_scroll)
        
        # 右侧绩效指标面板 - 使用滚动区域
        stats_scroll = QScrollArea()
        stats_scroll.setWidgetResizable(True)
        stats_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.stats_panel = StatsPanel()
        stats_scroll.setWidget(self.stats_panel)
        main_splitter.addWidget(stats_scroll)
        
        # 设置分割器比例
        main_splitter.setSizes([350, 900, 300])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(main_splitter)
    
    def _create_status_bar(self):
        """
        创建状态栏
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _initialize_data(self):
        """
        初始化数据
        """
        try:
            # 获取默认数据
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            ticker_text = self.ticker_combo.currentText()
            ticker = ticker_text.split()[0]
            
            self.status_bar.showMessage(f"正在获取数据: {ticker}")
            self.price_data = self.data_engine.fetch_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                use_dxy=True
            )
            
            if self.price_data is not None:
                self.status_bar.showMessage(f"数据获取成功: {len(self.price_data)} 条记录")
                # 更新数据状态面板
                self._update_data_status_panel()
                # 计算因子
                self.factor_data = self.factor_engine.calculate_all_factors(self.price_data)
                if self.factor_data is not None:
                    self.status_bar.showMessage("因子计算完成")
        except Exception as e:
            self.status_bar.showMessage(f"初始化失败: {e}")
    
    def _update_data_status_panel(self):
        """更新数据状态面板"""
        # 更新数据源状态
        source_name = self.data_engine.get_data_summary().get('data_source', 'unknown') if self.data_engine.get_data_summary() else 'unknown'
        self.data_status_panel.update_data_source(self.data_engine.is_online, source_name)
        
        # 更新数据摘要
        summary = self.data_engine.get_data_summary()
        self.data_status_panel.update_data_summary(summary)
        
        # 更新缓存状态
        cache_status = self.cache_manager.get_status()
        self.data_status_panel.update_cache_status(cache_status)
    
    def _on_refresh_data(self):
        """刷新数据"""
        try:
            self.status_bar.showMessage("正在刷新数据...")
            self.data_status_panel.set_refresh_enabled(False)
            
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            ticker_text = self.ticker_combo.currentText()
            ticker = ticker_text.split()[0]
            
            # 强制刷新
            self.price_data = self.data_engine.fetch_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                use_dxy=True,
                force_refresh=True
            )
            
            if self.price_data is not None:
                self.factor_data = self.factor_engine.calculate_all_factors(self.price_data)
                self._update_data_status_panel()
                self.status_bar.showMessage("数据刷新成功")
            
            self.data_status_panel.set_refresh_enabled(True)
            
        except Exception as e:
            self.status_bar.showMessage(f"刷新失败: {e}")
            self.data_status_panel.set_refresh_enabled(True)
    
    def _on_clear_cache(self):
        """清除缓存"""
        try:
            self.status_bar.showMessage("正在清除缓存...")
            self.data_status_panel.set_clear_cache_enabled(False)
            
            self.cache_manager.invalidate_all()
            
            # 更新缓存状态
            cache_status = self.cache_manager.get_status()
            self.data_status_panel.update_cache_status(cache_status)
            
            self.status_bar.showMessage("缓存已清除")
            self.data_status_panel.set_clear_cache_enabled(True)
            
        except Exception as e:
            self.status_bar.showMessage(f"清除缓存失败: {e}")
            self.data_status_panel.set_clear_cache_enabled(True)
    
    def run_backtest(self):
        """
        运行回测
        """
        try:
            self.status_bar.showMessage("正在准备回测...")
            
            # 禁用运行按钮
            self.run_button.setEnabled(False)
            
            # 获取参数
            params = self.param_panel.get_parameters()
            
            # 确保数据已初始化
            if self.factor_data is None:
                self._initialize_data()
            
            # 创建回测线程
            self.backtest_thread = BacktestThread(
                self.factor_data, 
                params, 
                self.backtest_engine, 
                self.analytics_engine
            )
            
            # 连接信号
            self.backtest_thread.finished.connect(self.on_backtest_finished)
            self.backtest_thread.error.connect(self.on_backtest_error)
            self.backtest_thread.progress.connect(self.on_backtest_progress)
            
            # 启动线程
            self.backtest_thread.start()
            
        except Exception as e:
            self.status_bar.showMessage(f"回测准备失败: {e}")
            self.run_button.setEnabled(True)
    
    def on_backtest_progress(self, progress, message):
        """
        回测进度更新
        """
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(message)
    
    def on_backtest_finished(self, backtest_results, analysis_results):
        """
        回测完成
        """
        try:
            # 保存结果
            self.backtest_results = backtest_results
            
            # 更新图表
            self.chart_panel.update_charts(
                backtest_results, analysis_results, self.factor_data
            )
            
            # 更新绩效指标
            self.stats_panel.update_stats(backtest_results)
            
            self.status_bar.showMessage("回测完成")
        except Exception as e:
            self.status_bar.showMessage(f"更新结果失败: {e}")
        finally:
            # 启用运行按钮
            self.run_button.setEnabled(True)
            # 重置进度条
            self.progress_bar.setValue(0)
    
    def on_backtest_error(self, error_message):
        """
        回测错误
        """
        self.status_bar.showMessage(f"回测失败: {error_message}")
        # 启用运行按钮
        self.run_button.setEnabled(True)
        # 重置进度条
        self.progress_bar.setValue(0)
    
    def reset_parameters(self):
        """
        重置参数
        """
        self.param_panel.reset_parameters()
        self.status_bar.showMessage("参数已重置")
    
    def export_report(self):
        """
        导出报告
        """
        try:
            if self.backtest_results is not None:
                report_path = self.analytics_engine.export_report(
                    self.backtest_results, self.factor_data
                )
                self.status_bar.showMessage(f"报告导出成功: {report_path}")
            else:
                self.status_bar.showMessage("请先运行回测")
        except Exception as e:
            self.status_bar.showMessage(f"导出失败: {e}")
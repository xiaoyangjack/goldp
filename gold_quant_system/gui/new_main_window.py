#!/usr/bin/env python3
"""
黄金量化本地研究系统 - 新主窗口

采用简洁的三段式布局：Header + 全屏图表 + Footer
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QDateEdit, QProgressBar,
    QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon
from loguru import logger


class NewMainWindow(QMainWindow):
    """
    新主窗口类
    
    采用简洁的三段式布局：
    - Header: Logo + 数据选择 + 控制按钮
    - Content: 全屏图表展示
    - Footer: 状态栏
    """
    
    def __init__(self):
        super().__init__()
        
        # 数据
        self.price_data = None
        self.factor_data = None
        self.backtest_results = None
        self.current_params = None
        
        # 引擎初始化标志
        self.engines_initialized = False
        
        # 设置窗口
        self.setWindowTitle("📊 GoldQuant - 黄金量化研究系统")
        self.resize(1600, 900)
        self.setMinimumSize(1200, 700)
        
        # 设置窗口样式，确保背景可见
        self.setStyleSheet("background-color: #0f172a;")
        
        self._create_ui()
        
        # 居中显示
        self._center_on_screen()
        
        logger.info("NewMainWindow 初始化完成")
    
    def _center_on_screen(self):
        """将窗口居中显示在屏幕上"""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtGui import QScreen
            app = QApplication.instance()
            if app:
                screens = app.screens()
                if screens:
                    screen = screens[0]  # 使用主屏幕
                    screen_geometry = screen.geometry()
                    window_geometry = self.frameGeometry()
                    
                    # 计算居中位置
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    
                    # 如果窗口位置超出屏幕，调整为可见位置
                    if x < 50:
                        x = 50
                    if y < 50:
                        y = 50
                    
                    self.move(x, y)
        except Exception as e:
            # 如果居中失败，使用默认位置
            logger.warning(f"窗口居中失败: {e}")
    
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        
        # 窗口显示后延迟初始化
        if not self.engines_initialized:
            QTimer.singleShot(200, self._initialize_engines_and_data)
    
    def _initialize_engines_and_data(self):
        """初始化引擎和数据"""
        try:
            # 初始化引擎
            from core.data_engine import DataEngine
            from core.factor_engine import FactorEngine
            from core.backtest_engine import BacktestEngine
            from core.analytics_engine import AnalyticsEngine
            from core.cache_manager import get_cache_manager
            
            self.data_engine = DataEngine()
            self.factor_engine = FactorEngine()
            self.backtest_engine = BacktestEngine()
            self.analytics_engine = AnalyticsEngine()
            self.cache_manager = get_cache_manager()
            
            self.engines_initialized = True
            
            # 初始化数据
            self._initialize_data()
            
        except Exception as e:
            logger.error(f"初始化引擎失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _create_ui(self):
        """创建 UI"""
        logger.info("开始创建 UI...")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Content - 图表区域
        from gui.plotly_chart_widget import PlotlyChartWidget
        self.chart_widget = PlotlyChartWidget()
        main_layout.addWidget(self.chart_widget, 1)
        
        # Footer - 状态栏
        footer = self._create_footer()
        main_layout.addWidget(footer)
        
        # 初始化Toast管理器
        from gui.toast_notification import get_toast_manager
        self.toast_manager = get_toast_manager()
        self.toast_manager.set_parent(self)
        
        logger.info("UI 创建完成")
    
    def _create_header(self):
        """创建头部"""
        header = QWidget()
        header.setObjectName("header")
        header.setStyleSheet("""
            #header {
                background-color: #0f172a;
                border-bottom: 1px solid #334155;
                padding: 12px 20px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(16)
        
        # Logo
        logo_label = QLabel("📊 GoldQuant")
        logo_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #6366f1;
        """)
        layout.addWidget(logo_label)
        
        layout.addStretch()
        
        # 数据源选择
        data_group = QWidget()
        data_layout = QHBoxLayout(data_group)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(12)
        
        # 数据源
        data_layout.addWidget(QLabel("📈"))
        self.ticker_combo = QComboBox()
        self.ticker_combo.addItems(["GC=F (黄金期货)", "GLD (黄金ETF)", "GDX (黄金矿企)"])
        self.ticker_combo.setMinimumWidth(160)
        self.ticker_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 12px;
                color: #f8fafc;
                min-height: 32px;
            }
            QComboBox:hover {
                border-color: #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e293b;
                border: 1px solid #334155;
                selection-background-color: #6366f1;
            }
        """)
        data_layout.addWidget(self.ticker_combo)
        
        # 日期范围
        data_layout.addWidget(QLabel("📅"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate(2020, 1, 1))
        self.start_date_edit.setStyleSheet("""
            QDateEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 12px;
                color: #f8fafc;
                min-height: 32px;
            }
        """)
        data_layout.addWidget(self.start_date_edit)
        
        data_layout.addWidget(QLabel("至"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setStyleSheet("""
            QDateEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px 12px;
                color: #f8fafc;
                min-height: 32px;
            }
        """)
        data_layout.addWidget(self.end_date_edit)
        
        layout.addWidget(data_group)
        
        # 控制按钮
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(8)
        
        # 设置按钮
        settings_btn = QPushButton("⚙️ 设置")
        settings_btn.setProperty("secondary", "true")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #f8fafc;
                font-weight: 500;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        settings_btn.clicked.connect(self._on_open_settings)
        btn_layout.addWidget(settings_btn)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.setProperty("secondary", "true")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #f8fafc;
                font-weight: 500;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        refresh_btn.clicked.connect(self._on_refresh_data)
        btn_layout.addWidget(refresh_btn)
        
        # 导出按钮
        self.export_btn = QPushButton("📥 导出报告")
        self.export_btn.setProperty("secondary", "true")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #f8fafc;
                font-weight: 500;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            QPushButton:disabled {
                background-color: #1e293b;
                color: #64748b;
            }
        """)
        self.export_btn.clicked.connect(self._on_export_report)
        self.export_btn.setEnabled(False)
        btn_layout.addWidget(self.export_btn)
        
        # 运行按钮
        self.run_btn = QPushButton("▶️ 运行回测")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                color: #ffffff;
                font-weight: 600;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #818cf8;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #94a3b8;
            }
        """)
        self.run_btn.clicked.connect(self._on_run_backtest)
        btn_layout.addWidget(self.run_btn)
        
        layout.addWidget(btn_group)
        
        return header
    
    def _create_footer(self):
        """创建底部状态栏"""
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setStyleSheet("""
            #footer {
                background-color: #0f172a;
                border-top: 1px solid #334155;
                padding: 8px 20px;
            }
            QLabel {
                color: #94a3b8;
                font-size: 12px;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(20, 4, 20, 4)
        layout.setSpacing(16)
        
        # 状态标签
        self.status_label = QLabel("⚡ 就绪")
        layout.addWidget(self.status_label)
        
        layout.addSpacing(20)
        
        # 数据信息
        self.data_info_label = QLabel("📁 数据: --")
        layout.addWidget(self.data_info_label)
        
        self.data_count_label = QLabel("📊 条数: --")
        layout.addWidget(self.data_count_label)
        
        self.price_range_label = QLabel("💰 价格: --")
        layout.addWidget(self.price_range_label)
        
        self.cache_label = QLabel("💾 缓存: --")
        layout.addWidget(self.cache_label)
        
        layout.addStretch()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border: none;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        return footer
    
    def _initialize_data(self):
        """初始化数据"""
        try:
            if not hasattr(self, 'status_label') or self.status_label is None:
                logger.warning("窗口未准备好，跳过数据初始化")
                return
            
            if not hasattr(self, 'data_engine'):
                logger.warning("引擎未初始化，跳过数据初始化")
                return
            
            self.status_label.setText("⏳ 加载数据中...")
            
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            ticker_text = self.ticker_combo.currentText()
            ticker = ticker_text.split()[0]
            
            self.price_data = self.data_engine.fetch_data(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                use_dxy=True
            )
            
            if self.price_data is not None:
                self.factor_data = self.factor_engine.calculate_all_factors(self.price_data)
                self._update_data_info()
                self.status_label.setText("✅ 数据加载完成")
            else:
                self.status_label.setText("⚠️ 数据加载失败")
                
        except Exception as e:
            if hasattr(self, 'status_label') and self.status_label is not None:
                self.status_label.setText(f"❌ 错误: {str(e)}")
            logger.error(f"数据初始化失败: {e}")
    
    def _update_data_info(self):
        """更新数据信息"""
        if self.price_data is None:
            return
        
        try:
            summary = self.data_engine.get_data_summary()
            if summary:
                ticker_text = self.ticker_combo.currentText()
                self.data_info_label.setText(f"📁 数据: {ticker_text.split()[0]}")
                self.data_count_label.setText(f"📊 条数: {summary.get('total_days', 0)}")
                self.price_range_label.setText(
                    f"💰 价格: ${summary.get('min_price', 0):.0f} ~ ${summary.get('max_price', 0):.0f}"
                )
            
            if hasattr(self, 'cache_manager'):
                cache_status = self.cache_manager.get_status()
                if cache_status:
                    self.cache_label.setText(f"💾 缓存: {cache_status.get('total_size_mb', 0):.1f}MB")
        except Exception as e:
            logger.error(f"更新数据信息失败: {e}")
    
    def _on_open_settings(self):
        """打开设置对话框"""
        from gui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.current_params, self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()
    
    def _on_settings_changed(self, params):
        """设置变更"""
        self.current_params = params
        logger.info("设置已更新")
    
    def _on_refresh_data(self):
        """刷新数据"""
        try:
            self.status_label.setText("⏳ 刷新数据中...")
            self._initialize_data()
        except Exception as e:
            self.status_label.setText(f"❌ 刷新失败: {str(e)}")
    
    def _on_run_backtest(self):
        """运行回测"""
        try:
            if self.factor_data is None:
                self._initialize_data()
            
            if self.factor_data is None:
                self.status_label.setText("⚠️ 数据未加载")
                self.toast_manager.warning("数据未加载，请先刷新数据")
                return
            
            self.status_label.setText("⏳ 回测中...")
            self.run_btn.setEnabled(False)
            self.progress_bar.setValue(10)
            self.toast_manager.info("回测任务已创建，正在初始化回测引擎与历史数据")
            
            # 获取参数
            params = self.current_params or {}
            
            # 构建策略列表
            strategies = []
            if params.get('sma_enabled', True):
                strategies.append('sma')
            if params.get('rsi_enabled', True):
                strategies.append('rsi')
            if params.get('macd_enabled', True):
                strategies.append('macd')
            if params.get('bb_enabled', True):
                strategies.append('bb')
            if params.get('multi_enabled', True):
                strategies.append('multi')
            
            if not strategies:
                strategies = ['sma', 'rsi', 'macd', 'bb', 'multi']
            
            # 完整参数
            full_params = {
                'strategies': strategies,
                'sma_fast': params.get('sma_fast', 20),
                'sma_slow': params.get('sma_slow', 60),
                'rsi_period': params.get('rsi_period', 14),
                'rsi_overbought': params.get('rsi_overbought', 65),
                'rsi_oversold': params.get('rsi_oversold', 35),
                'macd_fast': params.get('macd_fast', 12),
                'macd_slow': params.get('macd_slow', 26),
                'macd_signal': params.get('macd_signal', 9),
                'bb_period': params.get('bb_period', 20),
                'bb_std': params.get('bb_std', 2.0),
                'atr_multiplier': params.get('atr_multiplier', 1.5),
                'target_vol': params.get('target_vol', 0.01),
                'use_vol_sizing': params.get('use_vol_sizing', True),
                'use_dxy_filter': params.get('use_dxy_filter', False),
                'multi_factor_threshold': params.get('multi_factor_threshold', 2),
            }
            
            # 创建回测线程
            from gui.backtest_thread import BacktestThread
            self.backtest_thread = BacktestThread(
                self.factor_data,
                full_params,
                self.backtest_engine,
                self.analytics_engine
            )
            
            # 连接信号
            self.backtest_thread.finished.connect(self._on_backtest_finished)
            self.backtest_thread.error.connect(self._on_backtest_error)
            self.backtest_thread.progress.connect(self._on_backtest_progress)
            
            # 启动
            self.backtest_thread.start()
            
        except Exception as e:
            self.status_label.setText(f"❌ 回测失败: {str(e)}")
            self.run_btn.setEnabled(True)
            logger.error(f"回测失败: {e}")
    
    def _on_backtest_progress(self, progress, message):
        """回测进度更新"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"⏳ {message}")
    
    def _on_backtest_finished(self, backtest_results, analysis_results):
        """回测完成"""
        try:
            self.backtest_results = backtest_results
            self.analysis_results = analysis_results
            
            self.toast_manager.info("回测执行完成，正在生成回测报告与绩效指标")
            
            # 更新图表
            self.chart_widget.update_charts(
                backtest_results,
                analysis_results,
                self.factor_data
            )
            
            self.progress_bar.setValue(100)
            self.status_label.setText("✅ 回测完成")
            self.run_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            
            self.toast_manager.success("回测报告生成完成，可查看详情或导出报告")
            logger.info(f"回测完成: {len(backtest_results)} 个策略")
            
        except Exception as e:
            self.status_label.setText(f"❌ 显示结果失败: {str(e)}")
            self.run_btn.setEnabled(True)
            logger.error(f"显示结果失败: {e}")
    
    def _on_export_report(self):
        """导出报告"""
        try:
            if not self.backtest_results:
                self.status_label.setText("⚠️ 没有回测结果可导出")
                self.toast_manager.warning("没有回测结果可导出，请先运行回测")
                return
            
            self.status_label.setText("⏳ 正在导出报告...")
            self.export_btn.setEnabled(False)
            self.progress_bar.setValue(0)
            self.toast_manager.info("报告正在生成与导出中，请稍候...")
            
            def export_progress_callback(progress, message):
                self.progress_bar.setValue(progress)
                self.status_label.setText(f"⏳ {message}")
            
            from gui.report_exporter import ReportExporter
            exporter = ReportExporter()
            
            results = exporter.export_all(
                self.backtest_results,
                self.analysis_results,
                self.factor_data,
                self.current_params,
                progress_callback=export_progress_callback
            )
            
            success_count = sum(1 for v in results.values() if v)
            self.status_label.setText(f"✅ 导出完成: 成功 {success_count} 个文件")
            self.export_btn.setEnabled(True)
            self.progress_bar.setValue(100)
            
            self.toast_manager.success(f"报告导出成功，已保存至下载目录 (成功 {success_count} 个文件)")
            logger.info(f"报告导出完成: {results}")
            
        except Exception as e:
            self.status_label.setText(f"❌ 导出失败: {str(e)}")
            self.export_btn.setEnabled(True)
            self.progress_bar.setValue(0)
            self.toast_manager.error(f"报告导出失败: {str(e)}，可点击重试")
            logger.error(f"导出报告失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _on_backtest_error(self, error_message):
        """回测错误"""
        self.status_label.setText(f"❌ 回测错误: {error_message}")
        self.run_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.toast_manager.error(f"回测执行失败: {error_message}，请检查后重试")
        logger.error(f"回测错误: {error_message}")

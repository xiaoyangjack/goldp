from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QProgressBar, QFrame,
    QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from loguru import logger


class DataStatusPanel(QWidget):
    """
    数据状态面板 - 显示数据采集状态、缓存信息等
    
    功能：
    - 数据源状态指示
    - 缓存使用情况
    - 数据范围显示
    - 缓存刷新/清理功能
    """
    
    refresh_data = pyqtSignal()
    clear_cache = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.data_summary = None
        self.cache_status = None
        
        self._create_ui()
        self._setup_refresh_timer()
    
    def _create_ui(self):
        """创建界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # 标题
        title_label = QLabel("📊 数据状态")
        title_label.setProperty("heading", "true")
        title_label.setFont(QFont(title_label.font().family(), 14, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        # 数据源状态
        source_group = self._create_source_status_group()
        main_layout.addWidget(source_group)
        
        # 数据摘要
        summary_group = self._create_data_summary_group()
        main_layout.addWidget(summary_group)
        
        # 缓存状态
        cache_group = self._create_cache_status_group()
        main_layout.addWidget(cache_group)
        
        # 操作按钮
        buttons_group = self._create_buttons_group()
        main_layout.addWidget(buttons_group)
        
        main_layout.addStretch()
    
    def _create_source_status_group(self):
        """创建数据源状态组"""
        group = QGroupBox("数据源状态")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # 数据源状态指示器
        self.source_status_widget = QWidget()
        source_layout = QHBoxLayout(self.source_status_widget)
        source_layout.setContentsMargins(0, 0, 0, 0)
        
        self.source_indicator = QLabel("●")
        self.source_indicator.setStyleSheet("color: #ef4444; font-size: 20px;")
        source_layout.addWidget(self.source_indicator)
        
        self.source_status_label = QLabel("未连接")
        self.source_status_label.setStyleSheet("color: #94a3b8;")
        source_layout.addWidget(self.source_status_label)
        source_layout.addStretch()
        
        layout.addWidget(self.source_status_widget)
        
        # 数据源信息
        self.source_info_label = QLabel("数据源: --")
        self.source_info_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.source_info_label)
        
        return group
    
    def _create_data_summary_group(self):
        """创建数据摘要组"""
        group = QGroupBox("数据摘要")
        layout = QGridLayout(group)
        layout.setSpacing(8)
        
        # 数据范围
        layout.addWidget(QLabel("日期范围:"), 0, 0)
        self.date_range_label = QLabel("-- 至 --")
        self.date_range_label.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(self.date_range_label, 0, 1)
        
        # 数据量
        layout.addWidget(QLabel("数据条数:"), 1, 0)
        self.data_count_label = QLabel("--")
        self.data_count_label.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(self.data_count_label, 1, 1)
        
        # 价格范围
        layout.addWidget(QLabel("价格区间:"), 2, 0)
        self.price_range_label = QLabel("-- ~ --")
        self.price_range_label.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(self.price_range_label, 2, 1)
        
        # DXY数据
        layout.addWidget(QLabel("DXY数据:"), 3, 0)
        self.dxy_status_label = QLabel("--")
        self.dxy_status_label.setStyleSheet("color: #e2e8f0;")
        layout.addWidget(self.dxy_status_label, 3, 1)
        
        return group
    
    def _create_cache_status_group(self):
        """创建缓存状态组"""
        group = QGroupBox("缓存状态")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # 缓存使用进度条
        self.cache_progress = QProgressBar()
        self.cache_progress.setMaximum(100)
        self.cache_progress.setValue(0)
        self.cache_progress.setFormat("缓存使用: %p%")
        self.cache_progress.setFixedHeight(24)
        layout.addWidget(self.cache_progress)
        
        # 缓存详情
        cache_info_layout = QGridLayout()
        cache_info_layout.setSpacing(4)
        
        cache_info_layout.addWidget(QLabel("活跃项:"), 0, 0)
        self.cache_active_label = QLabel("--")
        self.cache_active_label.setStyleSheet("color: #e2e8f0;")
        cache_info_layout.addWidget(self.cache_active_label, 0, 1)
        
        cache_info_layout.addWidget(QLabel("已过期:"), 1, 0)
        self.cache_expired_label = QLabel("--")
        self.cache_expired_label.setStyleSheet("color: #e2e8f0;")
        cache_info_layout.addWidget(self.cache_expired_label, 1, 1)
        
        cache_info_layout.addWidget(QLabel("总大小:"), 2, 0)
        self.cache_size_label = QLabel("--")
        self.cache_size_label.setStyleSheet("color: #e2e8f0;")
        cache_info_layout.addWidget(self.cache_size_label, 2, 1)
        
        layout.addLayout(cache_info_layout)
        
        return group
    
    def _create_buttons_group(self):
        """创建按钮组"""
        group = QGroupBox("操作")
        layout = QHBoxLayout(group)
        layout.setSpacing(8)
        
        # 刷新数据按钮
        self.refresh_button = QPushButton("🔄 刷新数据")
        self.refresh_button.clicked.connect(self.refresh_data.emit)
        self.refresh_button.setProperty("secondary", "true")
        layout.addWidget(self.refresh_button)
        
        # 清除缓存按钮
        self.clear_cache_button = QPushButton("🗑️ 清除缓存")
        self.clear_cache_button.clicked.connect(self.clear_cache.emit)
        self.clear_cache_button.setProperty("secondary", "true")
        layout.addWidget(self.clear_cache_button)
        
        return group
    
    def _setup_refresh_timer(self):
        """设置自动刷新定时器"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(30000)  # 每30秒刷新一次
    
    def _auto_refresh(self):
        """自动刷新（不触发信号）"""
        pass
    
    def update_data_source(self, is_online, source_name):
        """
        更新数据源状态
        
        Args:
            is_online: 是否在线
            source_name: 数据源名称
        """
        if is_online:
            self.source_indicator.setStyleSheet("color: #10b981; font-size: 20px;")
            self.source_status_label.setText("已连接")
            self.source_status_label.setStyleSheet("color: #10b981;")
        else:
            self.source_indicator.setStyleSheet("color: #f59e0b; font-size: 20px;")
            self.source_status_label.setText("离线模式")
            self.source_status_label.setStyleSheet("color: #f59e0b;")
        
        self.source_info_label.setText(f"数据源: {source_name}")
    
    def update_data_summary(self, summary):
        """
        更新数据摘要
        
        Args:
            summary: 数据摘要字典
        """
        if summary is None:
            self.date_range_label.setText("-- 至 --")
            self.data_count_label.setText("--")
            self.price_range_label.setText("-- ~ --")
            self.dxy_status_label.setText("--")
            return
        
        self.data_summary = summary
        
        start_date = summary.get('start_date', '--')
        end_date = summary.get('end_date', '--')
        self.date_range_label.setText(f"{start_date} 至 {end_date}")
        
        total_days = summary.get('total_days', 0)
        self.data_count_label.setText(f"{total_days} 条")
        
        min_price = summary.get('min_price', 0)
        max_price = summary.get('max_price', 0)
        self.price_range_label.setText(f"${min_price:.0f} ~ ${max_price:.0f}")
        
        has_dxy = summary.get('has_dxy', False)
        self.dxy_status_label.setText("✓ 可用" if has_dxy else "✗ 不可用")
        self.dxy_status_label.setStyleSheet(
            "color: #10b981;" if has_dxy else "color: #ef4444;"
        )
    
    def update_cache_status(self, status):
        """
        更新缓存状态
        
        Args:
            status: 缓存状态字典
        """
        if status is None:
            self.cache_progress.setValue(0)
            self.cache_active_label.setText("--")
            self.cache_expired_label.setText("--")
            self.cache_size_label.setText("--")
            return
        
        self.cache_status = status
        
        total_items = status.get('total_items', 0)
        active_items = status.get('active_items', 0)
        expired_items = status.get('expired_items', 0)
        total_size_mb = status.get('total_size_mb', 0)
        
        # 计算进度（最大100MB）
        progress = min(int((total_size_mb / 100) * 100), 100)
        self.cache_progress.setValue(progress)
        self.cache_progress.setFormat(f"缓存使用: {total_size_mb} MB")
        
        self.cache_active_label.setText(f"{active_items} 项")
        self.cache_expired_label.setText(f"{expired_items} 项")
        self.cache_size_label.setText(f"{total_size_mb} MB")
    
    def set_refresh_enabled(self, enabled):
        """设置刷新按钮是否可用"""
        self.refresh_button.setEnabled(enabled)
    
    def set_clear_cache_enabled(self, enabled):
        """设置清除缓存按钮是否可用"""
        self.clear_cache_button.setEnabled(enabled)

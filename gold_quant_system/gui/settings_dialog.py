#!/usr/bin/env python3
"""
黄金量化本地研究系统 - 设置对话框

提供策略参数、风控设置、数据源配置等功能
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QSlider,
    QGroupBox, QFormLayout, QScrollArea, QPushButton,
    QDialogButtonBox, QComboBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from loguru import logger


class SettingsDialog(QDialog):
    """
    设置对话框
    
    提供选项卡式设置界面
    """
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_params=None, parent=None):
        super().__init__(parent)
        self.current_params = current_params or self._get_default_params()
        self.setWindowTitle("⚙️ 系统设置")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self._create_ui()
    
    def _get_default_params(self):
        """获取默认参数"""
        return {
            # 策略开关
            'sma_enabled': True,
            'rsi_enabled': True,
            'macd_enabled': True,
            'bb_enabled': True,
            'multi_enabled': True,
            
            # SMA
            'sma_fast': 20,
            'sma_slow': 60,
            
            # RSI
            'rsi_period': 14,
            'rsi_overbought': 65,
            'rsi_oversold': 35,
            
            # MACD
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # 布林带
            'bb_period': 20,
            'bb_std': 2.0,
            
            # 风控
            'atr_period': 14,
            'atr_multiplier': 1.5,
            'target_vol': 0.01,
            'use_vol_sizing': True,
            
            # 宏观
            'use_dxy_filter': False,
            'real_rate_threshold': 0.02,
            
            # 多因子
            'multi_factor_threshold': 2,
            
            # 数据源
            'ticker': 'GC=F',
            'start_date': '2020-01-01',
            'end_date': None,
        }
    
    def _create_ui(self):
        """创建 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # 创建各个选项卡
        self.tab_widget.addTab(self._create_strategy_tab(), "📋 策略")
        self.tab_widget.addTab(self._create_params_tab(), "📊 参数")
        self.tab_widget.addTab(self._create_risk_tab(), "🛡️ 风控")
        self.tab_widget.addTab(self._create_data_tab(), "📁 数据源")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setProperty("secondary", "true")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
    
    def _create_strategy_tab(self):
        """创建策略选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 策略开关
        strategy_group = QGroupBox("策略开关")
        strategy_layout = QVBoxLayout(strategy_group)
        strategy_layout.setSpacing(12)
        
        self.strategy_checks = {}
        strategies = [
            ('sma_enabled', '📈 SMA均线策略', '双均线交叉信号'),
            ('rsi_enabled', '📊 RSI回归策略', 'RSI超买超卖信号'),
            ('macd_enabled', '📉 MACD动量策略', 'MACD零轴交叉信号'),
            ('bb_enabled', '🎯 布林带策略', '布林带突破信号'),
            ('multi_enabled', '🔗 多因子策略', '多因子综合信号'),
        ]
        
        for key, name, desc in strategies:
            check_layout = QHBoxLayout()
            self.strategy_checks[key] = QCheckBox(name)
            self.strategy_checks[key].setChecked(self.current_params.get(key, True))
            check_layout.addWidget(self.strategy_checks[key])
            check_layout.addWidget(QLabel(f"<span style='color: #64748b; font-size: 12px;'>{desc}</span>"))
            check_layout.addStretch()
            strategy_layout.addLayout(check_layout)
        
        layout.addWidget(strategy_group)
        layout.addStretch()
        
        return widget
    
    def _create_params_tab(self):
        """创建参数选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # SMA 参数
        sma_group = QGroupBox("SMA 参数")
        sma_layout = QFormLayout(sma_group)
        
        sma_fast = self._create_spinbox(5, 60, self.current_params.get('sma_fast', 20))
        sma_slow = self._create_spinbox(20, 200, self.current_params.get('sma_slow', 60))
        
        sma_layout.addRow("快线周期:", sma_fast)
        sma_layout.addRow("慢线周期:", sma_slow)
        
        self.param_widgets = {
            'sma_fast': sma_fast,
            'sma_slow': sma_slow,
        }
        
        # RSI 参数
        rsi_group = QGroupBox("RSI 参数")
        rsi_layout = QFormLayout(rsi_group)
        
        rsi_period = self._create_spinbox(5, 50, self.current_params.get('rsi_period', 14))
        rsi_overbought = self._create_spinbox(50, 90, self.current_params.get('rsi_overbought', 65))
        rsi_oversold = self._create_spinbox(10, 50, self.current_params.get('rsi_oversold', 35))
        
        rsi_layout.addRow("周期:", rsi_period)
        rsi_layout.addRow("超买阈值:", rsi_overbought)
        rsi_layout.addRow("超卖阈值:", rsi_oversold)
        
        self.param_widgets.update({
            'rsi_period': rsi_period,
            'rsi_overbought': rsi_overbought,
            'rsi_oversold': rsi_oversold,
        })
        
        # MACD 参数
        macd_group = QGroupBox("MACD 参数")
        macd_layout = QFormLayout(macd_group)
        
        macd_fast = self._create_spinbox(5, 50, self.current_params.get('macd_fast', 12))
        macd_slow = self._create_spinbox(10, 100, self.current_params.get('macd_slow', 26))
        macd_signal = self._create_spinbox(5, 30, self.current_params.get('macd_signal', 9))
        
        macd_layout.addRow("快线周期:", macd_fast)
        macd_layout.addRow("慢线周期:", macd_slow)
        macd_layout.addRow("信号周期:", macd_signal)
        
        self.param_widgets.update({
            'macd_fast': macd_fast,
            'macd_slow': macd_slow,
            'macd_signal': macd_signal,
        })
        
        # 布林带参数
        bb_group = QGroupBox("布林带参数")
        bb_layout = QFormLayout(bb_group)
        
        bb_period = self._create_spinbox(10, 50, self.current_params.get('bb_period', 20))
        bb_std = self._create_double_spinbox(1.0, 3.0, 0.1, self.current_params.get('bb_std', 2.0))
        
        bb_layout.addRow("周期:", bb_period)
        bb_layout.addRow("标准差倍数:", bb_std)
        
        self.param_widgets.update({
            'bb_period': bb_period,
            'bb_std': bb_std,
        })
        
        # 多因子参数
        multi_group = QGroupBox("多因子参数")
        multi_layout = QFormLayout(multi_group)
        
        multi_threshold = self._create_spinbox(1, 3, self.current_params.get('multi_factor_threshold', 2))
        multi_layout.addRow("触发阈值:", multi_threshold)
        
        self.param_widgets['multi_factor_threshold'] = multi_threshold
        
        layout.addWidget(sma_group)
        layout.addWidget(rsi_group)
        layout.addWidget(macd_group)
        layout.addWidget(bb_group)
        layout.addWidget(multi_group)
        layout.addStretch()
        
        return widget
    
    def _create_risk_tab(self):
        """创建风控选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 风控参数
        risk_group = QGroupBox("风控参数")
        risk_layout = QFormLayout(risk_group)
        
        atr_multiplier = self._create_double_spinbox(0.5, 4.0, 0.1, self.current_params.get('atr_multiplier', 1.5))
        target_vol = self._create_double_spinbox(0.001, 0.05, 0.001, self.current_params.get('target_vol', 0.01))
        
        self.param_widgets.update({
            'atr_multiplier': atr_multiplier,
            'target_vol': target_vol,
        })
        
        risk_layout.addRow("ATR止损倍数:", atr_multiplier)
        risk_layout.addRow("目标波动率:", target_vol)
        
        # 波动率仓位
        vol_group = QGroupBox("仓位管理")
        vol_layout = QVBoxLayout(vol_group)
        
        self.vol_sizing_check = QCheckBox("启用波动率仓位管理")
        self.vol_sizing_check.setChecked(self.current_params.get('use_vol_sizing', True))
        vol_layout.addWidget(self.vol_sizing_check)
        
        vol_desc = QLabel("根据市场波动率动态调整仓位，降低高波动期的风险暴露")
        vol_desc.setStyleSheet("color: #64748b; font-size: 12px;")
        vol_layout.addWidget(vol_desc)
        
        # 宏观过滤
        macro_group = QGroupBox("宏观过滤")
        macro_layout = QVBoxLayout(macro_group)
        
        self.dxy_filter_check = QCheckBox("启用 DXY 过滤")
        self.dxy_filter_check.setChecked(self.current_params.get('use_dxy_filter', False))
        macro_layout.addWidget(self.dxy_filter_check)
        
        dxy_desc = QLabel("在美元走强期间降低黄金多头仓位")
        dxy_desc.setStyleSheet("color: #64748b; font-size: 12px;")
        macro_layout.addWidget(dxy_desc)
        
        layout.addWidget(risk_group)
        layout.addWidget(vol_group)
        layout.addWidget(macro_group)
        layout.addStretch()
        
        return widget
    
    def _create_data_tab(self):
        """创建数据源选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 数据源选择
        source_group = QGroupBox("数据源")
        source_layout = QFormLayout(source_group)
        
        self.ticker_combo = QComboBox()
        self.ticker_combo.addItems([
            'GC=F (黄金期货)',
            'GLD (黄金ETF)',
            'GDX (黄金矿企)',
            'IAU (iShares黄金)'
        ])
        
        ticker_text = self.current_params.get('ticker', 'GC=F')
        for i in range(self.ticker_combo.count()):
            if ticker_text in self.ticker_combo.itemText(i):
                self.ticker_combo.setCurrentIndex(i)
                break
        
        source_layout.addRow("交易品种:", self.ticker_combo)
        
        # 日期范围
        date_group = QGroupBox("日期范围")
        date_layout = QFormLayout(date_group)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.fromString(
            self.current_params.get('start_date', '2020-01-01'), 'yyyy-MM-dd'
        ))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        end_date = self.current_params.get('end_date')
        if end_date:
            self.end_date_edit.setDate(QDate.fromString(end_date, 'yyyy-MM-dd'))
        else:
            self.end_date_edit.setDate(QDate.currentDate())
        
        date_layout.addRow("开始日期:", self.start_date_edit)
        date_layout.addRow("结束日期:", self.end_date_edit)
        
        # 数据说明
        info_group = QGroupBox("数据说明")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel(
            "• 数据来源: Yahoo Finance<br>"
            "• 数据更新: 每日收盘后<br>"
            "• 缓存机制: 自动缓存避免重复请求<br>"
            "• 注意事项: 期货数据可能存在跳空"
        )
        info_text.setStyleSheet("color: #94a3b8; line-height: 1.8;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(source_group)
        layout.addWidget(date_group)
        layout.addWidget(info_group)
        layout.addStretch()
        
        return widget
    
    def _create_spinbox(self, min_val, max_val, default_val):
        """创建整数微调框"""
        spinbox = QSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setValue(default_val)
        spinbox.setFixedWidth(100)
        return spinbox
    
    def _create_double_spinbox(self, min_val, max_val, step, default_val):
        """创建浮点数微调框"""
        spinbox = QDoubleSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setSingleStep(step)
        spinbox.setDecimals(3)
        spinbox.setValue(default_val)
        spinbox.setFixedWidth(100)
        return spinbox
    
    def _on_save(self):
        """保存设置"""
        params = {}
        
        # 策略开关
        for key, check in self.strategy_checks.items():
            params[key] = check.isChecked()
        
        # 参数
        for key, widget in self.param_widgets.items():
            params[key] = widget.value()
        
        # 风控
        params['use_vol_sizing'] = self.vol_sizing_check.isChecked()
        params['use_dxy_filter'] = self.dxy_filter_check.isChecked()
        
        # 数据源
        ticker_text = self.ticker_combo.currentText()
        params['ticker'] = ticker_text.split()[0]
        params['start_date'] = self.start_date_edit.date().toString("yyyy-MM-dd")
        params['end_date'] = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        self.settings_changed.emit(params)
        self.accept()
        logger.info(f"设置已保存: {params}")

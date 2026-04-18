#!/usr/bin/env python3
"""
黄金量化本地研究系统参数面板

实现左侧参数调节区域，包含策略选择和各种参数控件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, 
    QCheckBox, QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal


class CollapsibleGroup(QWidget):
    """可折叠分组框"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        
        # 标题栏
        self.header_widget = QWidget()
        self.header_widget.setStyleSheet("background-color: #1e293b; border-radius: 4px;")
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(8, 6, 8, 6)
        
        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setFixedSize(20, 20)
        self.toggle_btn.setProperty("secondary", "true")
        self.toggle_btn.setStyleSheet("font-size: 10px; padding: 0;")
        self.toggle_btn.clicked.connect(self.toggle)
        header_layout.addWidget(self.toggle_btn)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: 600; font-size: 12px; color: #e2e8f0;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        self.main_layout.addWidget(self.header_widget)
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #0f172a; border-radius: 4px;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(6)
        self.main_layout.addWidget(self.content_widget)
    
    def toggle(self):
        """切换折叠状态"""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        self.toggle_btn.setText("▶" if self.is_collapsed else "▼")
    
    def add_widget(self, widget):
        """添加控件到内容区域"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加布局到内容区域"""
        self.content_layout.addLayout(layout)


class ParamPanel(QWidget):
    """
    参数面板类
    """
    
    def __init__(self):
        super().__init__()
        
        # 默认参数
        self.default_params = {
            # 策略开关
            "sma_enabled": True,
            "rsi_enabled": True,
            "macd_enabled": True,
            "bb_enabled": True,
            "multi_enabled": True,
            
            # SMA
            "sma_fast": 20,
            "sma_slow": 60,
            
            # RSI
            "rsi_period": 14,
            "rsi_overbought": 65,
            "rsi_oversold": 35,
            
            # MACD
            "macd_fast": 12,
            "macd_slow": 26,
            "macd_signal": 9,
            
            # 布林带
            "bb_period": 20,
            "bb_std": 2.0,
            
            # 风控
            "atr_period": 14,
            "atr_multiplier": 1.5,
            "target_vol": 0.01,
            "use_vol_sizing": True,
            
            # 宏观
            "use_dxy_filter": False,
            "real_rate_threshold": 0.02,
            
            # 多因子
            "multi_factor_threshold": 2,
        }
        
        # 当前参数
        self.current_params = self.default_params.copy()
        
        # 存储所有控件的引用
        self.widgets = {}
        self.groups = {}
        
        # 创建布局
        self._create_layout()
    
    def _create_layout(self):
        """
        创建布局
        """
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(4, 4, 4, 4)
        
        # 标题
        title_label = QLabel("⚙️ 策略参数")
        title_label.setProperty("heading", "true")
        from PyQt6.QtGui import QFont
        title_label.setFont(QFont(title_label.font().family(), 14, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        # 策略选择组（默认展开）
        self.groups['strategy'] = CollapsibleGroup("📋 策略选择")
        self._create_strategy_group(self.groups['strategy'])
        main_layout.addWidget(self.groups['strategy'])
        
        # SMA参数组（默认展开）
        self.groups['sma'] = CollapsibleGroup("📊 SMA参数")
        self._create_sma_group(self.groups['sma'])
        main_layout.addWidget(self.groups['sma'])
        
        # RSI参数组（默认展开）
        self.groups['rsi'] = CollapsibleGroup("📈 RSI参数")
        self._create_rsi_group(self.groups['rsi'])
        main_layout.addWidget(self.groups['rsi'])
        
        # MACD参数组（默认展开）
        self.groups['macd'] = CollapsibleGroup("📉 MACD参数")
        self._create_macd_group(self.groups['macd'])
        main_layout.addWidget(self.groups['macd'])
        
        # 布林带参数组（默认展开）
        self.groups['bb'] = CollapsibleGroup("🎯 布林带参数")
        self._create_bb_group(self.groups['bb'])
        main_layout.addWidget(self.groups['bb'])
        
        # 风控参数组（默认展开）
        self.groups['risk'] = CollapsibleGroup("🛡️ 风控参数")
        self._create_risk_group(self.groups['risk'])
        main_layout.addWidget(self.groups['risk'])
        
        # 宏观因子组（默认展开）
        self.groups['macro'] = CollapsibleGroup("🌐 宏观因子")
        self._create_macro_group(self.groups['macro'])
        main_layout.addWidget(self.groups['macro'])
        
        # 多因子参数组（默认展开）
        self.groups['multi'] = CollapsibleGroup("🔗 多因子参数")
        self._create_multi_group(self.groups['multi'])
        main_layout.addWidget(self.groups['multi'])
        
        # 添加占位符
        main_layout.addStretch()
    
    def _create_strategy_group(self, group):
        """创建策略选择组"""
        self.widgets['sma_checkbox'] = QCheckBox("SMA均线")
        self.widgets['sma_checkbox'].setChecked(self.current_params["sma_enabled"])
        self.widgets['sma_checkbox'].stateChanged.connect(
            lambda state: self._update_param("sma_enabled", state == Qt.CheckState.Checked.value)
        )
        group.add_widget(self.widgets['sma_checkbox'])
        
        self.widgets['rsi_checkbox'] = QCheckBox("RSI回归")
        self.widgets['rsi_checkbox'].setChecked(self.current_params["rsi_enabled"])
        self.widgets['rsi_checkbox'].stateChanged.connect(
            lambda state: self._update_param("rsi_enabled", state == Qt.CheckState.Checked.value)
        )
        group.add_widget(self.widgets['rsi_checkbox'])
        
        self.widgets['macd_checkbox'] = QCheckBox("MACD动量")
        self.widgets['macd_checkbox'].setChecked(self.current_params["macd_enabled"])
        self.widgets['macd_checkbox'].stateChanged.connect(
            lambda state: self._update_param("macd_enabled", state == Qt.CheckState.Checked.value)
        )
        group.add_widget(self.widgets['macd_checkbox'])
        
        self.widgets['bb_checkbox'] = QCheckBox("布林带")
        self.widgets['bb_checkbox'].setChecked(self.current_params["bb_enabled"])
        self.widgets['bb_checkbox'].stateChanged.connect(
            lambda state: self._update_param("bb_enabled", state == Qt.CheckState.Checked.value)
        )
        group.add_widget(self.widgets['bb_checkbox'])
        
        self.widgets['multi_checkbox'] = QCheckBox("多因子")
        self.widgets['multi_checkbox'].setChecked(self.current_params["multi_enabled"])
        self.widgets['multi_checkbox'].stateChanged.connect(
            lambda state: self._update_param("multi_enabled", state == Qt.CheckState.Checked.value)
        )
        group.add_widget(self.widgets['multi_checkbox'])
    
    def _create_sma_group(self, group):
        """创建SMA参数组"""
        self.widgets['sma_fast_slider'], self.widgets['sma_fast_spinbox'] = self._create_slider_spinbox(
            "快线", 5, 60, self.current_params["sma_fast"], "sma_fast"
        )
        group.add_widget(self.widgets['sma_fast_slider'])
        group.add_widget(self.widgets['sma_fast_spinbox'])
        
        self.widgets['sma_slow_slider'], self.widgets['sma_slow_spinbox'] = self._create_slider_spinbox(
            "慢线", 20, 200, self.current_params["sma_slow"], "sma_slow"
        )
        group.add_widget(self.widgets['sma_slow_slider'])
        group.add_widget(self.widgets['sma_slow_spinbox'])
    
    def _create_rsi_group(self, group):
        """创建RSI参数组"""
        self.widgets['rsi_period_slider'], self.widgets['rsi_period_spinbox'] = self._create_slider_spinbox(
            "周期", 5, 50, self.current_params["rsi_period"], "rsi_period"
        )
        group.add_widget(self.widgets['rsi_period_slider'])
        group.add_widget(self.widgets['rsi_period_spinbox'])
        
        self.widgets['rsi_overbought_slider'], self.widgets['rsi_overbought_spinbox'] = self._create_slider_spinbox(
            "超买", 50, 90, self.current_params["rsi_overbought"], "rsi_overbought"
        )
        group.add_widget(self.widgets['rsi_overbought_slider'])
        group.add_widget(self.widgets['rsi_overbought_spinbox'])
        
        self.widgets['rsi_oversold_slider'], self.widgets['rsi_oversold_spinbox'] = self._create_slider_spinbox(
            "超卖", 10, 50, self.current_params["rsi_oversold"], "rsi_oversold"
        )
        group.add_widget(self.widgets['rsi_oversold_slider'])
        group.add_widget(self.widgets['rsi_oversold_spinbox'])
    
    def _create_macd_group(self, group):
        """创建MACD参数组"""
        self.widgets['macd_fast_slider'], self.widgets['macd_fast_spinbox'] = self._create_slider_spinbox(
            "快线", 5, 50, self.current_params["macd_fast"], "macd_fast"
        )
        group.add_widget(self.widgets['macd_fast_slider'])
        group.add_widget(self.widgets['macd_fast_spinbox'])
        
        self.widgets['macd_slow_slider'], self.widgets['macd_slow_spinbox'] = self._create_slider_spinbox(
            "慢线", 10, 100, self.current_params["macd_slow"], "macd_slow"
        )
        group.add_widget(self.widgets['macd_slow_slider'])
        group.add_widget(self.widgets['macd_slow_spinbox'])
        
        self.widgets['macd_signal_slider'], self.widgets['macd_signal_spinbox'] = self._create_slider_spinbox(
            "信号", 5, 30, self.current_params["macd_signal"], "macd_signal"
        )
        group.add_widget(self.widgets['macd_signal_slider'])
        group.add_widget(self.widgets['macd_signal_spinbox'])
    
    def _create_bb_group(self, group):
        """创建布林带参数组"""
        self.widgets['bb_period_slider'], self.widgets['bb_period_spinbox'] = self._create_slider_spinbox(
            "周期", 10, 50, self.current_params["bb_period"], "bb_period"
        )
        group.add_widget(self.widgets['bb_period_slider'])
        group.add_widget(self.widgets['bb_period_spinbox'])
        
        self.widgets['bb_std_slider'], self.widgets['bb_std_spinbox'] = self._create_double_slider_spinbox(
            "标准差", 1.0, 3.0, 0.1, self.current_params["bb_std"], "bb_std"
        )
        group.add_widget(self.widgets['bb_std_slider'])
        group.add_widget(self.widgets['bb_std_spinbox'])
    
    def _create_risk_group(self, group):
        """创建风控参数组"""
        self.widgets['atr_multiplier_slider'], self.widgets['atr_multiplier_spinbox'] = self._create_double_slider_spinbox(
            "ATR倍数", 0.5, 4.0, 0.1, self.current_params["atr_multiplier"], "atr_multiplier"
        )
        group.add_widget(self.widgets['atr_multiplier_slider'])
        group.add_widget(self.widgets['atr_multiplier_spinbox'])
        
        self.widgets['target_vol_slider'], self.widgets['target_vol_spinbox'] = self._create_double_slider_spinbox(
            "目标波动", 0.001, 0.05, 0.001, self.current_params["target_vol"], "target_vol"
        )
        group.add_widget(self.widgets['target_vol_slider'])
        group.add_widget(self.widgets['target_vol_spinbox'])
        
        self.widgets['vol_sizing_checkbox'] = QCheckBox("启用波动率仓位")
        self.widgets['vol_sizing_checkbox'].setChecked(self.current_params["use_vol_sizing"])
        self.widgets['vol_sizing_checkbox'].stateChanged.connect(
            lambda state: self._update_param("use_vol_sizing", state == Qt.CheckState.Checked.value)
        )
        group.add_widget(self.widgets['vol_sizing_checkbox'])
    
    def _create_macro_group(self, group):
        """创建宏观因子组"""
        self.widgets['dxy_filter_checkbox'] = QCheckBox("DXY过滤")
        self.widgets['dxy_filter_checkbox'].setChecked(self.current_params["use_dxy_filter"])
        self.widgets['dxy_filter_checkbox'].stateChanged.connect(
            lambda state: self._update_param("use_dxy_filter", state == Qt.CheckState.Checked.value)
        )
        group.add_widget(self.widgets['dxy_filter_checkbox'])
        
        self.widgets['real_rate_slider'], self.widgets['real_rate_spinbox'] = self._create_double_slider_spinbox(
            "实际利率阈值", 0.0, 0.1, 0.001, self.current_params["real_rate_threshold"], "real_rate_threshold"
        )
        group.add_widget(self.widgets['real_rate_slider'])
        group.add_widget(self.widgets['real_rate_spinbox'])
    
    def _create_multi_group(self, group):
        """创建多因子参数组"""
        self.widgets['multi_threshold_slider'], self.widgets['multi_threshold_spinbox'] = self._create_slider_spinbox(
            "触发阈值", 1, 3, self.current_params["multi_factor_threshold"], "multi_factor_threshold"
        )
        group.add_widget(self.widgets['multi_threshold_slider'])
        group.add_widget(self.widgets['multi_threshold_spinbox'])
    
    def _create_slider_spinbox(self, label, min_val, max_val, default_val, param_name):
        """
        创建滑块和 spinbox 组合
        """
        # 滑块
        slider_widget = QWidget()
        slider_layout = QHBoxLayout(slider_widget)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.addWidget(QLabel(label))
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.valueChanged.connect(lambda value: self._update_param_and_sync(param_name, value, 'slider'))
        slider_layout.addWidget(slider)
        
        # Spinbox
        spinbox = QSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setValue(default_val)
        spinbox.valueChanged.connect(lambda value: self._update_param_and_sync(param_name, value, 'spinbox'))
        spinbox.setFixedWidth(70)
        
        return slider_widget, spinbox
    
    def _create_double_slider_spinbox(self, label, min_val, max_val, step, default_val, param_name):
        """
        创建双精度滑块和 spinbox 组合
        """
        # 滑块
        slider_widget = QWidget()
        slider_layout = QHBoxLayout(slider_widget)
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.addWidget(QLabel(label))
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(int(min_val * 1000))
        slider.setMaximum(int(max_val * 1000))
        slider.setValue(int(default_val * 1000))
        slider.valueChanged.connect(lambda value: self._update_param_and_sync(param_name, value / 1000, 'slider'))
        slider_layout.addWidget(slider)
        
        # Spinbox
        spinbox = QDoubleSpinBox()
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setSingleStep(step)
        spinbox.setValue(default_val)
        spinbox.setDecimals(3)
        spinbox.valueChanged.connect(lambda value: self._update_param_and_sync(param_name, value, 'spinbox'))
        spinbox.setFixedWidth(90)
        
        return slider_widget, spinbox
    
    def _update_param_and_sync(self, param_name, value, source):
        """更新参数并同步控件"""
        self.current_params[param_name] = value
        
        # 根据参数名找到对应的控件并同步
        if param_name in ['sma_fast', 'sma_slow', 'rsi_period', 'rsi_overbought', 'rsi_oversold', 
                          'macd_fast', 'macd_slow', 'macd_signal', 'bb_period', 'multi_factor_threshold']:
            slider_widget = self.widgets.get(f'{param_name}_slider')
            spinbox = self.widgets.get(f'{param_name}_spinbox')
            if slider_widget and spinbox:
                slider = slider_widget.findChild(QSlider)
                if slider and source != 'slider':
                    slider.setValue(int(value))
                if source != 'spinbox':
                    spinbox.setValue(int(value))
        
        elif param_name in ['bb_std', 'atr_multiplier', 'target_vol', 'real_rate_threshold']:
            slider_widget = self.widgets.get(f'{param_name}_slider')
            spinbox = self.widgets.get(f'{param_name}_spinbox')
            if slider_widget and spinbox:
                slider = slider_widget.findChild(QSlider)
                if slider and source != 'slider':
                    slider.setValue(int(value * 1000))
                if source != 'spinbox':
                    spinbox.setValue(value)
    
    def _update_param(self, param_name, value):
        """
        更新参数
        """
        self.current_params[param_name] = value
    
    def get_parameters(self):
        """
        获取当前参数
        """
        # 构建策略列表
        strategies = []
        if self.current_params["sma_enabled"]:
            strategies.append("sma")
        if self.current_params["rsi_enabled"]:
            strategies.append("rsi")
        if self.current_params["macd_enabled"]:
            strategies.append("macd")
        if self.current_params["bb_enabled"]:
            strategies.append("bb")
        if self.current_params["multi_enabled"]:
            strategies.append("multi")
        
        # 构建参数字典
        params = {
            "strategies": strategies,
            "sma_fast": self.current_params["sma_fast"],
            "sma_slow": self.current_params["sma_slow"],
            "rsi_period": self.current_params["rsi_period"],
            "rsi_overbought": self.current_params["rsi_overbought"],
            "rsi_oversold": self.current_params["rsi_oversold"],
            "macd_fast": self.current_params["macd_fast"],
            "macd_slow": self.current_params["macd_slow"],
            "macd_signal": self.current_params["macd_signal"],
            "bb_period": self.current_params["bb_period"],
            "bb_std": self.current_params["bb_std"],
            "atr_period": self.current_params["atr_period"],
            "atr_multiplier": self.current_params["atr_multiplier"],
            "target_vol": self.current_params["target_vol"],
            "use_vol_sizing": self.current_params["use_vol_sizing"],
            "use_dxy_filter": self.current_params["use_dxy_filter"],
            "real_rate_threshold": self.current_params["real_rate_threshold"],
            "multi_factor_threshold": self.current_params["multi_factor_threshold"],
        }
        
        return params
    
    def reset_parameters(self):
        """
        重置参数到默认值
        """
        self.current_params = self.default_params.copy()
        
        # 更新策略复选框
        self.widgets['sma_checkbox'].setChecked(self.current_params["sma_enabled"])
        self.widgets['rsi_checkbox'].setChecked(self.current_params["rsi_enabled"])
        self.widgets['macd_checkbox'].setChecked(self.current_params["macd_enabled"])
        self.widgets['bb_checkbox'].setChecked(self.current_params["bb_enabled"])
        self.widgets['multi_checkbox'].setChecked(self.current_params["multi_enabled"])
        
        # 更新所有数值控件
        for param_name, value in self.default_params.items():
            if param_name.endswith('_enabled') or param_name.endswith('_threshold') and param_name == 'multi_factor_threshold':
                continue
            
            widget_key = param_name
            slider_widget = self.widgets.get(f'{widget_key}_slider')
            spinbox = self.widgets.get(f'{widget_key}_spinbox')
            
            if slider_widget and spinbox:
                slider = slider_widget.findChild(QSlider)
                if slider:
                    if isinstance(value, float):
                        slider.setValue(int(value * 1000))
                    else:
                        slider.setValue(value)
                if isinstance(value, float):
                    spinbox.setValue(value)
                else:
                    spinbox.setValue(value)
        
        # 更新复选框
        self.widgets['vol_sizing_checkbox'].setChecked(self.current_params["use_vol_sizing"])
        self.widgets['dxy_filter_checkbox'].setChecked(self.current_params["use_dxy_filter"])

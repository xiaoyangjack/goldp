#!/usr/bin/env python3
"""
Toast 轻提示组件
提供全局Toast轻提示功能
"""

from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont
from loguru import logger


class ToastNotification(QLabel):
    """Toast 轻提示组件"""
    
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 1.0
        self._setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)
    
    def _setup_ui(self):
        """设置UI"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.setFont(QFont("Arial", 14))
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.hide()
    
    def _get_style(self, toast_type):
        """获取样式"""
        styles = {
            self.INFO: """
                background-color: #1e40af;
                color: #ffffff;
                border-radius: 8px;
                padding: 12px 20px;
            """,
            self.SUCCESS: """
                background-color: #065f46;
                color: #ffffff;
                border-radius: 8px;
                padding: 12px 20px;
            """,
            self.WARNING: """
                background-color: #92400e;
                color: #ffffff;
                border-radius: 8px;
                padding: 12px 20px;
            """,
            self.ERROR: """
                background-color: #991b1b;
                color: #ffffff;
                border-radius: 8px;
                padding: 12px 20px;
            """
        }
        return styles.get(toast_type, styles[self.INFO])
    
    def show_message(self, message, toast_type=INFO, duration=3000):
        """显示提示消息"""
        icons = {
            self.INFO: "ℹ️",
            self.SUCCESS: "✅",
            self.WARNING: "⚠️",
            self.ERROR: "❌"
        }
        
        icon = icons.get(toast_type, "")
        self.setText(f"{icon} {message}")
        self.setStyleSheet(self._get_style(toast_type))
        
        self._opacity = 1.0
        self.setWindowOpacity(1.0)
        self.show()
        
        if self.parent():
            self._adjust_position()
        
        self.timer.start(duration)
        logger.info(f"Toast: {message}")
    
    def _adjust_position(self):
        """调整位置"""
        parent_rect = self.parent().rect()
        toast_rect = self.rect()
        
        x = (parent_rect.width() - toast_rect.width()) // 2
        y = 40
        
        self.move(x, y)
    
    def get_opacity(self):
        """获取透明度"""
        return self._opacity
    
    def set_opacity(self, opacity):
        """设置透明度"""
        self._opacity = opacity
        self.setWindowOpacity(opacity)
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)


class ToastManager:
    """Toast 管理器"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'toast'):
            self.toast = None
            self.parent = None
    
    def set_parent(self, parent):
        """设置父窗口"""
        self.parent = parent
        if self.parent:
            self.toast = ToastNotification(parent)
    
    def info(self, message, duration=3000):
        """显示信息提示"""
        if self.toast:
            self.toast.show_message(message, ToastNotification.INFO, duration)
    
    def success(self, message, duration=3000):
        """显示成功提示"""
        if self.toast:
            self.toast.show_message(message, ToastNotification.SUCCESS, duration)
    
    def warning(self, message, duration=3000):
        """显示警告提示"""
        if self.toast:
            self.toast.show_message(message, ToastNotification.WARNING, duration)
    
    def error(self, message, duration=3000):
        """显示错误提示"""
        if self.toast:
            self.toast.show_message(message, ToastNotification.ERROR, duration)


def get_toast_manager():
    """获取Toast管理器单例"""
    return ToastManager()

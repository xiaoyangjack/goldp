#!/usr/bin/env python3
"""
黄金量化本地研究系统入口点

启动QApplication和MainWindow，初始化整个系统
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt
from gui.new_main_window import NewMainWindow


def main():
    """
    主函数
    """
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序名称
    app.setApplicationName("黄金量化本地研究系统")
    app.setApplicationVersion("2.0.0")
    
    # 设置全局字体 - 使用现代清晰的字体
    font = QFont("SF Pro Display", 13) if sys.platform == "darwin" else QFont("Segoe UI", 11)
    app.setFont(font)
    
    # 现代深色主题配色方案
    palette = QPalette()
    
    # 主色调
    PRIMARY_COLOR = QColor(79, 70, 229)  # 靛蓝色
    PRIMARY_LIGHT = QColor(99, 102, 241)
    PRIMARY_DARK = QColor(67, 56, 202)
    
    # 背景色
    BG_DARK = QColor(15, 23, 42)
    BG_MEDIUM = QColor(30, 41, 59)
    BG_LIGHT = QColor(51, 65, 85)
    
    # 文本色
    TEXT_PRIMARY = QColor(248, 250, 252)
    TEXT_SECONDARY = QColor(148, 163, 184)
    TEXT_DISABLED = QColor(71, 85, 105)
    
    # 状态色
    SUCCESS = QColor(16, 185, 129)
    WARNING = QColor(245, 158, 11)
    ERROR = QColor(239, 68, 68)
    
    # 设置调色板
    palette.setColor(QPalette.ColorRole.Window, BG_DARK)
    palette.setColor(QPalette.ColorRole.WindowText, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.Base, BG_MEDIUM)
    palette.setColor(QPalette.ColorRole.AlternateBase, BG_LIGHT)
    palette.setColor(QPalette.ColorRole.ToolTipBase, BG_MEDIUM)
    palette.setColor(QPalette.ColorRole.ToolTipText, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.Text, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.Button, BG_LIGHT)
    palette.setColor(QPalette.ColorRole.ButtonText, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.BrightText, TEXT_PRIMARY)
    palette.setColor(QPalette.ColorRole.Link, PRIMARY_LIGHT)
    palette.setColor(QPalette.ColorRole.Highlight, PRIMARY_COLOR)
    palette.setColor(QPalette.ColorRole.HighlightedText, TEXT_PRIMARY)
    
    # 禁用状态
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, TEXT_DISABLED)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, TEXT_DISABLED)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, TEXT_DISABLED)
    
    app.setPalette(palette)
    
    # 设置全局样式表 - 现代化设计
    style_sheet = f"""
    /* 全局样式 */
    QWidget {{
        color: {TEXT_PRIMARY.name()};
        background-color: {BG_DARK.name()};
        selection-background-color: {PRIMARY_COLOR.name()};
        selection-color: {TEXT_PRIMARY.name()};
    }}
    
    /* 主窗口背景 */
    QMainWindow {{
        background-color: {BG_DARK.name()};
    }}
    
    /* 按钮样式 - 现代圆角按钮 */
    QPushButton {{
        background-color: {PRIMARY_COLOR.name()};
        color: {TEXT_PRIMARY.name()};
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        min-height: 36px;
        min-width: 100px;
    }}
    
    QPushButton:hover {{
        background-color: {PRIMARY_LIGHT.name()};
    }}
    
    QPushButton:pressed {{
        background-color: {PRIMARY_DARK.name()};
    }}
    
    QPushButton:disabled {{
        background-color: {BG_LIGHT.name()};
        color: {TEXT_DISABLED.name()};
    }}
    
    /* 次要按钮样式 */
    QPushButton[secondary="true"] {{
        background-color: {BG_LIGHT.name()};
        border: 1px solid {BG_LIGHT.name()};
    }}
    
    QPushButton[secondary="true"]:hover {{
        background-color: {BG_MEDIUM.name()};
        border: 1px solid {PRIMARY_COLOR.name()};
    }}
    
    /* 标签样式 */
    QLabel {{
        color: {TEXT_PRIMARY.name()};
        background: transparent;
    }}
    
    QLabel[heading="true"] {{
        font-size: 16px;
        font-weight: 700;
        color: {TEXT_PRIMARY.name()};
    }}
    
    QLabel[subheading="true"] {{
        font-size: 14px;
        font-weight: 600;
        color: {TEXT_SECONDARY.name()};
    }}
    
    /* 组合框样式 */
    QComboBox {{
        background-color: {BG_MEDIUM.name()};
        border: 1px solid {BG_LIGHT.name()};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 36px;
        min-width: 140px;
    }}
    
    QComboBox:hover {{
        border: 1px solid {PRIMARY_COLOR.name()};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {TEXT_SECONDARY.name()};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {BG_MEDIUM.name()};
        border: 1px solid {BG_LIGHT.name()};
        border-radius: 8px;
        selection-background-color: {PRIMARY_COLOR.name()};
        padding: 4px;
    }}
    
    /* 日期时间编辑样式 */
    QDateTimeEdit {{
        background-color: {BG_MEDIUM.name()};
        border: 1px solid {BG_LIGHT.name()};
        border-radius: 8px;
        padding: 8px 12px;
        min-height: 36px;
        min-width: 160px;
        selection-background-color: {PRIMARY_COLOR.name()};
    }}
    
    QDateTimeEdit:hover {{
        border: 1px solid {PRIMARY_COLOR.name()};
    }}
    
    QDateTimeEdit::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QDateTimeEdit::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {TEXT_SECONDARY.name()};
    }}
    
    QCalendarWidget {{
        background-color: {BG_MEDIUM.name()};
        color: {TEXT_PRIMARY.name()};
    }}
    
    /* 进度条样式 */
    QProgressBar {{
        background-color: {BG_MEDIUM.name()};
        border: none;
        border-radius: 10px;
        height: 20px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {PRIMARY_COLOR.name()}, stop:1 {PRIMARY_LIGHT.name()});
        border-radius: 10px;
    }}
    
    /* 分组框样式 */
    QGroupBox {{
        font-size: 14px;
        font-weight: 700;
        color: {TEXT_PRIMARY.name()};
        border: 1px solid {BG_LIGHT.name()};
        border-radius: 12px;
        margin-top: 20px;
        padding-top: 15px;
        background-color: {BG_MEDIUM.name()};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 8px;
        background-color: {BG_MEDIUM.name()};
    }}
    
    /* 滑块样式 */
    QSlider::groove:horizontal {{
        height: 6px;
        background: {BG_LIGHT.name()};
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {PRIMARY_COLOR.name()};
        width: 18px;
        height: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {PRIMARY_LIGHT.name()};
    }}
    
    QSlider::sub-page:horizontal {{
        background: {PRIMARY_COLOR.name()};
        border-radius: 3px;
    }}
    
    /* 微调框样式 */
    QSpinBox, QDoubleSpinBox {{
        background-color: {BG_MEDIUM.name()};
        border: 1px solid {BG_LIGHT.name()};
        border-radius: 8px;
        padding: 6px 10px;
        min-height: 32px;
        min-width: 90px;
        selection-background-color: {PRIMARY_COLOR.name()};
    }}
    
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border: 1px solid {PRIMARY_COLOR.name()};
    }}
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 24px;
        border-left: 1px solid {BG_LIGHT.name()};
        border-top-right-radius: 8px;
        background-color: {BG_LIGHT.name()};
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 24px;
        border-left: 1px solid {BG_LIGHT.name()};
        border-bottom-right-radius: 8px;
        background-color: {BG_LIGHT.name()};
    }}
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {PRIMARY_COLOR.name()};
    }}
    
    /* 复选框样式 */
    QCheckBox {{
        spacing: 8px;
        min-height: 24px;
    }}
    
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {BG_LIGHT.name()};
        border-radius: 4px;
        background-color: {BG_MEDIUM.name()};
    }}
    
    QCheckBox::indicator:hover {{
        border: 2px solid {PRIMARY_COLOR.name()};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {PRIMARY_COLOR.name()};
        border: 2px solid {PRIMARY_COLOR.name()};
    }}
    
    QCheckBox::indicator:checked::after {{
        content: "✓";
        color: white;
        font-size: 14px;
        font-weight: bold;
    }}
    
    /* 表格样式 */
    QTableWidget {{
        background-color: {BG_MEDIUM.name()};
        border: 1px solid {BG_LIGHT.name()};
        border-radius: 8px;
        gridline-color: {BG_LIGHT.name()};
        selection-background-color: {PRIMARY_COLOR.name()};
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border: none;
    }}
    
    QTableWidget::item:selected {{
        background-color: {PRIMARY_COLOR.name()};
    }}
    
    QHeaderView::section {{
        background-color: {BG_LIGHT.name()};
        color: {TEXT_PRIMARY.name()};
        padding: 10px;
        border: none;
        border-right: 1px solid {BG_MEDIUM.name()};
        border-bottom: 1px solid {BG_LIGHT.name()};
        font-weight: 600;
    }}
    
    /* 滚动条样式 */
    QScrollBar:vertical {{
        background: {BG_MEDIUM.name()};
        width: 10px;
        border-radius: 5px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {BG_LIGHT.name()};
        min-height: 30px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {PRIMARY_COLOR.name()};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background: {BG_MEDIUM.name()};
        height: 10px;
        border-radius: 5px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {BG_LIGHT.name()};
        min-width: 30px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {PRIMARY_COLOR.name()};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* 分割器样式 */
    QSplitter::handle {{
        background-color: {BG_LIGHT.name()};
    }}
    
    QSplitter::handle:hover {{
        background-color: {PRIMARY_COLOR.name()};
    }}
    
    QSplitter::handle:horizontal {{
        width: 3px;
    }}
    
    QSplitter::handle:vertical {{
        height: 3px;
    }}
    
    /* 状态栏样式 */
    QStatusBar {{
        background-color: {BG_MEDIUM.name()};
        border-top: 1px solid {BG_LIGHT.name()};
        color: {TEXT_SECONDARY.name()};
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    """
    
    app.setStyleSheet(style_sheet)
    
    # 创建主窗口
    window = NewMainWindow()
    
    # 显示主窗口
    window.show()
    
    # 确保窗口获得焦点并显示在最前面
    window.activateWindow()
    window.raise_()
    
    # 打印提示信息
    print("=" * 60)
    print("GoldQuant 界面已启动!")
    print("=" * 60)
    print(f"窗口标题: {window.windowTitle()}")
    print(f"窗口大小: {window.width()} x {window.height()}")
    print(f"窗口位置: ({window.x()}, {window.y()})")
    print(f"窗口是否可见: {window.isVisible()}")
    print(f"窗口是否激活: {window.isActiveWindow()}")
    print("=" * 60)
    print("如果看不到窗口，请检查任务栏或Dock栏")
    print("=" * 60)
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
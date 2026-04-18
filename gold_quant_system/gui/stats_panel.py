#!/usr/bin/env python3
"""
黄金量化本地研究系统绩效指标面板

实现右侧绩效指标区域，显示策略的绩效指标和交易记录
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, 
    QLabel, QTableWidget, QTableWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt


class StatsPanel(QWidget):
    """
    绩效指标面板类
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
        main_layout.setSpacing(10)  # 增加布局间距
        
        # 策略绩效概览
        self.stats_group = QGroupBox("策略绩效概览")
        self.stats_layout = QVBoxLayout(self.stats_group)
        
        # 绩效表格
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(6)
        self.stats_table.setHorizontalHeaderLabels(["策略", "总收益", "年化", "夏普", "最大回撤", "胜率"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.horizontalHeader().setMinimumHeight(30)  # 增大表头高度
        self.stats_table.setMinimumHeight(150)  # 增大表格高度
        self.stats_table.verticalHeader().setDefaultSectionSize(30)  # 增大行高
        self.stats_layout.addWidget(self.stats_table)
        
        main_layout.addWidget(self.stats_group)
        
        # 当前策略详细信息
        self.detail_group = QGroupBox("当前策略详细信息")
        self.detail_layout = QVBoxLayout(self.detail_group)
        self.detail_layout.setSpacing(8)  # 增加组内间距
        
        # 策略名称
        self.strategy_name_label = QLabel("策略: ")
        self.detail_layout.addWidget(self.strategy_name_label)
        
        # 详细指标
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(2)
        self.detail_table.setHorizontalHeaderLabels(["指标", "值"])
        self.detail_table.horizontalHeader().setStretchLastSection(True)
        self.detail_table.horizontalHeader().setMinimumHeight(30)  # 增大表头高度
        self.detail_table.verticalHeader().setDefaultSectionSize(30)  # 增大行高
        self.detail_layout.addWidget(self.detail_table)
        
        # 交易记录
        self.trades_group = QGroupBox("交易记录")
        self.trades_layout = QVBoxLayout(self.trades_group)
        
        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(5)
        self.trades_table.setHorizontalHeaderLabels(["类型", "日期", "价格", "数量", "盈亏"])
        self.trades_table.horizontalHeader().setStretchLastSection(True)
        self.trades_table.horizontalHeader().setMinimumHeight(30)  # 增大表头高度
        self.trades_table.verticalHeader().setDefaultSectionSize(30)  # 增大行高
        
        # 添加滚动区域
        self.trades_scroll = QScrollArea()
        self.trades_scroll.setWidget(self.trades_table)
        self.trades_scroll.setWidgetResizable(True)
        self.trades_layout.addWidget(self.trades_scroll)
        
        self.detail_layout.addWidget(self.trades_group)
        main_layout.addWidget(self.detail_group)
        
        # 添加占位符
        main_layout.addStretch()
    
    def update_stats(self, backtest_results):
        """
        更新绩效指标
        """
        if backtest_results is None:
            return
        
        # 更新绩效概览表格
        self._update_stats_table(backtest_results)
        
        # 默认显示第一个策略的详细信息
        if backtest_results:
            first_strategy = list(backtest_results.keys())[0]
            self._update_detail_table(first_strategy, backtest_results[first_strategy])
    
    def _update_stats_table(self, backtest_results):
        """
        更新绩效概览表格
        """
        self.stats_table.setRowCount(len(backtest_results))
        
        for i, (strategy_name, result) in enumerate(backtest_results.items()):
            stats = result["stats"]
            
            # 策略名称
            self.stats_table.setItem(i, 0, QTableWidgetItem(strategy_name))
            
            # 总收益
            total_return = stats.get("total_return", 0)
            item = QTableWidgetItem(f"{total_return:.2%}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.stats_table.setItem(i, 1, item)
            
            # 年化收益
            ann_return = stats.get("ann_return", 0)
            item = QTableWidgetItem(f"{ann_return:.2%}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.stats_table.setItem(i, 2, item)
            
            # 夏普比率
            sharpe = stats.get("sharpe", 0)
            item = QTableWidgetItem(f"{sharpe:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.stats_table.setItem(i, 3, item)
            
            # 最大回撤
            max_dd = stats.get("max_dd", 0)
            item = QTableWidgetItem(f"{max_dd:.2%}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.stats_table.setItem(i, 4, item)
            
            # 胜率
            win_rate = stats.get("win_rate", 0)
            item = QTableWidgetItem(f"{win_rate:.2%}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.stats_table.setItem(i, 5, item)
        
        # 调整列宽
        self.stats_table.resizeColumnsToContents()
    
    def _update_detail_table(self, strategy_name, result):
        """
        更新当前策略详细信息
        """
        # 更新策略名称
        self.strategy_name_label.setText(f"策略: {strategy_name}")
        
        # 更新详细指标
        stats = result.get("stats", {})
        trades = result.get("trades", [])
        
        # 设置详细指标表格
        self.detail_table.setRowCount(6)
        
        # 总收益
        total_return = stats.get("total_return", 0)
        self.detail_table.setItem(0, 0, QTableWidgetItem("总收益"))
        item = QTableWidgetItem(f"{total_return:.2%}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.detail_table.setItem(0, 1, item)
        
        # 年化收益
        ann_return = stats.get("ann_return", 0)
        self.detail_table.setItem(1, 0, QTableWidgetItem("年化收益"))
        item = QTableWidgetItem(f"{ann_return:.2%}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.detail_table.setItem(1, 1, item)
        
        # 夏普比率
        sharpe = stats.get("sharpe", 0)
        self.detail_table.setItem(2, 0, QTableWidgetItem("夏普比率"))
        item = QTableWidgetItem(f"{sharpe:.2f}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.detail_table.setItem(2, 1, item)
        
        # 最大回撤
        max_dd = stats.get("max_dd", 0)
        self.detail_table.setItem(3, 0, QTableWidgetItem("最大回撤"))
        item = QTableWidgetItem(f"{max_dd:.2%}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.detail_table.setItem(3, 1, item)
        
        # 胜率
        win_rate = stats.get("win_rate", 0)
        self.detail_table.setItem(4, 0, QTableWidgetItem("胜率"))
        item = QTableWidgetItem(f"{win_rate:.2%}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.detail_table.setItem(4, 1, item)
        
        # 交易次数
        n_trades = stats.get("n_trades", 0)
        self.detail_table.setItem(5, 0, QTableWidgetItem("交易次数"))
        item = QTableWidgetItem(str(n_trades))
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
        self.detail_table.setItem(5, 1, item)
        
        # 调整列宽
        self.detail_table.resizeColumnsToContents()
        
        # 更新交易记录
        self._update_trades_table(trades)
    
    def _update_trades_table(self, trades):
        """
        更新交易记录表格
        """
        self.trades_table.setRowCount(len(trades))
        
        for i, trade in enumerate(trades):
            # 类型
            trade_type = trade.get("type", "")
            self.trades_table.setItem(i, 0, QTableWidgetItem(trade_type))
            
            # 日期
            date = trade.get("date", "")
            self.trades_table.setItem(i, 1, QTableWidgetItem(str(date)))
            
            # 价格
            price = trade.get("price", 0)
            item = QTableWidgetItem(f"{price:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.trades_table.setItem(i, 2, item)
            
            # 数量
            size = trade.get("size", 0)
            item = QTableWidgetItem(f"{size:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.trades_table.setItem(i, 3, item)
            
            # 盈亏
            profit = trade.get("profit", 0)
            item = QTableWidgetItem(f"{profit:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            # 设置盈亏颜色
            if profit > 0:
                item.setForeground(Qt.GlobalColor.green)
            elif profit < 0:
                item.setForeground(Qt.GlobalColor.red)
            self.trades_table.setItem(i, 4, item)
        
        # 调整列宽
        self.trades_table.resizeColumnsToContents()
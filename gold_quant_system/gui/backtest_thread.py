#!/usr/bin/env python3
"""
黄金量化本地研究系统回测线程

实现QThread异步执行回测，避免GUI卡顿
"""

from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger


class BacktestThread(QThread):
    """
    回测线程类
    """
    
    # 信号定义
    finished = pyqtSignal(dict, dict)  # 回测完成信号，传递回测结果和分析结果
    error = pyqtSignal(str)  # 错误信号，传递错误信息
    progress = pyqtSignal(int, str)  # 进度信号，传递进度百分比和状态信息
    
    def __init__(self, factor_data, params, backtest_engine, analytics_engine):
        """
        初始化回测线程
        
        Args:
            factor_data: 因子数据
            params: 策略参数
            backtest_engine: 回测引擎
            analytics_engine: 分析引擎
        """
        super().__init__()
        self.factor_data = factor_data
        self.params = params
        self.backtest_engine = backtest_engine
        self.analytics_engine = analytics_engine
    
    def run(self):
        """
        线程运行方法
        """
        try:
            # 发送开始信号
            self.progress.emit(0, "开始回测...")
            
            # 运行回测
            self.progress.emit(30, "运行策略回测...")
            backtest_results = self.backtest_engine.run_all_strategies(
                self.factor_data, self.params
            )
            
            # 分析结果
            self.progress.emit(70, "分析回测结果...")
            analysis_results = self.analytics_engine.analyze_results(
                backtest_results, self.factor_data
            )
            
            # 发送完成信号
            self.progress.emit(100, "回测完成")
            self.finished.emit(backtest_results, analysis_results)
            
        except Exception as e:
            logger.error(f"回测线程错误: {e}")
            self.error.emit(str(e))
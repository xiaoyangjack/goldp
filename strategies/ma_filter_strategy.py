"""
MA 过滤策略
基于快慢线金叉/死叉的策略
"""
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MaFilterStrategy(BaseStrategy):
    """
    MA 过滤策略
    基于快慢线金叉/死叉
    
    参数:
        fast_window: 快线窗口
        slow_window: 慢线窗口
    """
    
    def __init__(self, fast_window=10, slow_window=30, **params):
        """
        初始化策略
        
        Args:
            fast_window: 快线窗口
            slow_window: 慢线窗口
            **params: 其他参数
        """
        super().__init__(fast_window=fast_window, slow_window=slow_window, **params)
        self.fast_window = fast_window
        self.slow_window = slow_window
    
    def generate_signals(self, df: pd.DataFrame) -> dict:
        """
        生成交易信号
        
        Args:
            df: 包含价格数据的DataFrame
        
        Returns:
            dict: 包含 entries 和 exits 的字典
        """
        # 计算MA
        df = self.calculate_indicators(df)
        
        # 计算MA金叉死叉
        fast_ma = df['close'].rolling(window=self.fast_window).mean()
        slow_ma = df['close'].rolling(window=self.slow_window).mean()
        
        # 金叉：快MA上穿慢MA
        cross_over = (fast_ma.shift(1) <= slow_ma.shift(1)) & (fast_ma > slow_ma)
        
        # 死叉：快MA下穿慢MA
        cross_under = (fast_ma.shift(1) >= slow_ma.shift(1)) & (fast_ma < slow_ma)
        
        # 生成信号
        entries = cross_over.to_numpy()
        exits = cross_under.to_numpy()
        
        # 确保信号有效性
        entries[0:self.slow_window] = False  # 前slow_window个数据无效
        exits[0:self.slow_window] = False
        
        return {
            'entries': entries,
            'exits': exits
        }
    
    def get_signal_reason(self, df: pd.DataFrame, index: int) -> str:
        """
        获取信号产生原因
        
        Args:
            df: 数据
            index: 索引
        
        Returns:
            str: 原因
        """
        fast_ma = df['close'].rolling(window=self.fast_window).mean()
        slow_ma = df['close'].rolling(window=self.slow_window).mean()
        
        if index >= self.slow_window:
            if fast_ma.iloc[index] > slow_ma.iloc[index] and fast_ma.iloc[index-1] <= slow_ma.iloc[index-1]:
                return f"金叉信号：{self.fast_window}日均线({fast_ma.iloc[index]:.2f})上穿{self.slow_window}日均线({slow_ma.iloc[index]:.2f})"
            elif fast_ma.iloc[index] < slow_ma.iloc[index] and fast_ma.iloc[index-1] >= slow_ma.iloc[index-1]:
                return f"死叉信号：{self.fast_window}日均线({fast_ma.iloc[index]:.2f})下穿{self.slow_window}日均线({slow_ma.iloc[index]:.2f})"
        
        return "无信号"

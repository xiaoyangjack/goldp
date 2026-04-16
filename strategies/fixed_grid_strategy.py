"""
固定网格策略
基于价格网格的策略
"""
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class FixedGridStrategy(BaseStrategy):
    """
    固定网格策略
    基于价格网格的策略
    
    参数:
        base_price: 基准价格
        grid_size: 网格大小
        grid_count: 网格数量
    """
    
    def __init__(self, base_price=None, grid_size=2.0, grid_count=10, **params):
        """
        初始化策略
        
        Args:
            base_price: 基准价格（None时使用数据的平均价格）
            grid_size: 网格大小
            grid_count: 网格数量
            **params: 其他参数
        """
        super().__init__(base_price=base_price, grid_size=grid_size, grid_count=grid_count, **params)
        self.base_price = base_price
        self.grid_size = grid_size
        self.grid_count = grid_count
        self.grids = None
    
    def generate_signals(self, df: pd.DataFrame) -> dict:
        """
        生成交易信号
        
        Args:
            df: 包含价格数据的DataFrame
        
        Returns:
            dict: 包含 entries 和 exits 的字典
        """
        close_prices = df['close'].to_numpy()
        
        # 计算基准价格
        if self.base_price is None:
            base_price = np.mean(close_prices)
        else:
            base_price = self.base_price
        
        # 生成网格
        self.grids = []
        for i in range(-self.grid_count, self.grid_count + 1):
            grid_price = base_price + i * self.grid_size
            if grid_price > 0:
                self.grids.append(grid_price)
        self.grids.sort()
        
        # 生成信号
        entries = np.zeros(len(close_prices), dtype=bool)
        exits = np.zeros(len(close_prices), dtype=bool)
        
        # 前几个数据点不产生信号
        warmup_period = 10
        entries[:warmup_period] = False
        exits[:warmup_period] = False
        
        # 遍历价格生成信号
        for i in range(warmup_period, len(close_prices)):
            current_price = close_prices[i]
            prev_price = close_prices[i-1]
            
            # 检查是否触达买入网格
            for grid_price in self.grids:
                if grid_price < current_price and prev_price >= grid_price:
                    entries[i] = True
                    break
            
            # 检查是否触达卖出网格
            for grid_price in reversed(self.grids):
                if grid_price > current_price and prev_price <= grid_price:
                    exits[i] = True
                    break
        
        return {
            'entries': entries,
            'exits': exits
        }
    
    def get_grid_level(self, price: float) -> int:
        """
        获取价格所在的网格级别
        
        Args:
            price: 价格
        
        Returns:
            int: 网格级别
        """
        if self.grids is None:
            return 0
        
        for i, grid_price in enumerate(self.grids):
            if price <= grid_price:
                return i
        return len(self.grids) - 1
    
    def get_signal_reason(self, df: pd.DataFrame, index: int) -> str:
        """
        获取信号产生原因
        
        Args:
            df: 数据
            index: 索引
        
        Returns:
            str: 原因
        """
        if self.grids is None:
            return "网格未初始化"
        
        if index < 10:
            return "预热期"
        
        current_price = df['close'].iloc[index]
        prev_price = df['close'].iloc[index-1]
        
        # 检查买入信号
        for grid_price in self.grids:
            if grid_price < current_price and prev_price >= grid_price:
                return f"价格触及买入网格: {grid_price:.2f}"
        
        # 检查卖出信号
        for grid_price in reversed(self.grids):
            if grid_price > current_price and prev_price <= grid_price:
                return f"价格触及卖出网格: {grid_price:.2f}"
        
        return "无信号"

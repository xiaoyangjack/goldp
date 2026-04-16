"""
MA 过滤 + 风险控制策略
结合 MA 过滤和风险控制的策略
"""
import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from .ma_filter_strategy import MaFilterStrategy


class MaFilterRiskStrategy(BaseStrategy):
    """
    MA 过滤 + 风险控制策略
    结合 MA 过滤和风险控制
    
    参数:
        fast_window: 快线窗口
        slow_window: 慢线窗口
        max_single_loss: 单笔最大亏损比例
        max_daily_loss: 单日最大亏损比例
        max_weekly_loss: 单周最大亏损比例
        consecutive_loss_limit: 连续亏损次数限制
    """
    
    def __init__(self, 
                 fast_window=10, 
                 slow_window=30, 
                 max_single_loss=0.01,  # 1%
                 max_daily_loss=0.03,  # 3%
                 max_weekly_loss=0.08,  # 8%
                 consecutive_loss_limit=4, 
                 **params):
        """
        初始化策略
        
        Args:
            fast_window: 快线窗口
            slow_window: 慢线窗口
            max_single_loss: 单笔最大亏损比例
            max_daily_loss: 单日最大亏损比例
            max_weekly_loss: 单周最大亏损比例
            consecutive_loss_limit: 连续亏损次数限制
            **params: 其他参数
        """
        super().__init__(
            fast_window=fast_window,
            slow_window=slow_window,
            max_single_loss=max_single_loss,
            max_daily_loss=max_daily_loss,
            max_weekly_loss=max_weekly_loss,
            consecutive_loss_limit=consecutive_loss_limit,
            **params
        )
        
        self.ma_strategy = MaFilterStrategy(fast_window=fast_window, slow_window=slow_window)
        self.max_single_loss = max_single_loss
        self.max_daily_loss = max_daily_loss
        self.max_weekly_loss = max_weekly_loss
        self.consecutive_loss_limit = consecutive_loss_limit
        
        # 风控状态
        self.risk_state = {
            'daily_loss': 0.0,
            'weekly_loss': 0.0,
            'consecutive_losses': 0,
            'last_trade_date': None,
            'last_week_date': None
        }
    
    def generate_signals(self, df: pd.DataFrame) -> dict:
        """
        生成交易信号
        
        Args:
            df: 包含价格数据的DataFrame
        
        Returns:
            dict: 包含 entries 和 exits 的字典
        """
        # 先获取 MA 过滤策略的信号
        ma_signals = self.ma_strategy.generate_signals(df)
        entries = ma_signals['entries'].copy()
        exits = ma_signals['exits'].copy()
        
        # 应用风控逻辑
        for i in range(len(entries)):
            if entries[i]:
                if not self._check_risk_control(df, i):
                    entries[i] = False
            
            if exits[i]:
                # 卖出信号不受风控限制
                pass
        
        return {
            'entries': entries,
            'exits': exits
        }
    
    def _check_risk_control(self, df: pd.DataFrame, index: int) -> bool:
        """
        检查风险控制
        
        Args:
            df: 数据
            index: 索引
        
        Returns:
            bool: 是否通过风控
        """
        current_date = pd.to_datetime(df.iloc[index]['date']).date() if 'date' in df.columns else None
        
        # 重置每日亏损
        if current_date and (self.risk_state['last_trade_date'] is None or 
                           current_date != self.risk_state['last_trade_date']):
            self.risk_state['daily_loss'] = 0.0
            self.risk_state['last_trade_date'] = current_date
        
        # 重置每周亏损
        if current_date and (self.risk_state['last_week_date'] is None or 
                           current_date.weekday() < pd.to_datetime(self.risk_state['last_week_date']).weekday()):
            self.risk_state['weekly_loss'] = 0.0
            self.risk_state['last_week_date'] = current_date
        
        # 检查连续亏损
        if self.risk_state['consecutive_losses'] >= self.consecutive_loss_limit:
            return False
        
        # 检查单日亏损
        if self.risk_state['daily_loss'] >= self.max_daily_loss:
            return False
        
        # 检查单周亏损
        if self.risk_state['weekly_loss'] >= self.max_weekly_loss:
            return False
        
        return True
    
    def record_trade(self, pnl: float):
        """
        记录交易结果
        
        Args:
            pnl: 盈亏
        """
        if pnl < 0:
            self.risk_state['daily_loss'] += abs(pnl)
            self.risk_state['weekly_loss'] += abs(pnl)
            self.risk_state['consecutive_losses'] += 1
        else:
            self.risk_state['consecutive_losses'] = 0
    
    def get_risk_state(self) -> dict:
        """
        获取风控状态
        
        Returns:
            dict: 风控状态
        """
        return self.risk_state
    
    def get_signal_reason(self, df: pd.DataFrame, index: int) -> str:
        """
        获取信号产生原因
        
        Args:
            df: 数据
            index: 索引
        
        Returns:
            str: 原因
        """
        ma_reason = self.ma_strategy.get_signal_reason(df, index)
        
        if not self._check_risk_control(df, index):
            return f"{ma_reason} (风控限制)"
        
        return ma_reason

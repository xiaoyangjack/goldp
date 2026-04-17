import pandas as pd
import numpy as np
from loguru import logger


class MultiStrategy:
    """
    多策略信号层
    负责生成不同策略的信号并根据Regime进行融合
    """
    
    def __init__(self, price):
        """
        初始化多策略模块
        
        Args:
            price: 价格序列
        """
        self.price = price
        self.entries = None
        self.exits = None
        self.regime = None
    
    def generate_trend_signals(self, fast_ma, slow_ma):
        """
        生成趋势策略信号
        
        Args:
            fast_ma: 快线移动平均
            slow_ma: 慢线移动平均
        
        Returns:
            tuple: (entry信号, exit信号)
        """
        try:
            # 金叉买入，死叉卖出
            trend_entry = fast_ma > slow_ma
            trend_exit = fast_ma < slow_ma
            
            logger.info("生成趋势策略信号完成")
            return trend_entry, trend_exit
        except Exception as e:
            logger.error(f"生成趋势策略信号失败: {e}")
            return None, None
    
    def generate_range_signals(self, rsi, entry_threshold=30, exit_threshold=55):
        """
        生成震荡策略信号
        
        Args:
            rsi: RSI指标
            entry_threshold: 买入阈值
            exit_threshold: 卖出阈值
        
        Returns:
            tuple: (entry信号, exit信号)
        """
        try:
            # RSI低于阈值买入，高于阈值卖出
            range_entry = rsi < entry_threshold
            range_exit = rsi > exit_threshold
            
            logger.info(f"生成震荡策略信号完成: entry={entry_threshold}, exit={exit_threshold}")
            return range_entry, range_exit
        except Exception as e:
            logger.error(f"生成震荡策略信号失败: {e}")
            return None, None
    
    def generate_volatility_filter(self, atr, window=50):
        """
        生成波动过滤信号
        
        Args:
            atr: ATR波动率
            window: 滚动窗口大小
        
        Returns:
            pd.Series: 过滤信号
        """
        try:
            # 当ATR低于滚动均值时过滤（防假突破）
            vol_filter = atr < atr.rolling(window).mean()
            
            logger.info(f"生成波动过滤信号完成: window={window}")
            return vol_filter
        except Exception as e:
            logger.error(f"生成波动过滤信号失败: {e}")
            return None
    
    def fuse_strategies(self, regime, trend_entry, trend_exit, range_entry, range_exit, vol_filter=None):
        """
        根据Regime融合策略信号
        
        Args:
            regime: 市场状态序列
            trend_entry: 趋势策略买入信号
            trend_exit: 趋势策略卖出信号
            range_entry: 震荡策略买入信号
            range_exit: 震荡策略卖出信号
            vol_filter: 波动过滤信号
        
        Returns:
            tuple: (最终entry信号, 最终exit信号)
        """
        try:
            # 初始化信号序列
            entries = pd.Series(False, index=self.price.index)
            exits = pd.Series(False, index=self.price.index)
            
            # TREND状态使用趋势策略
            entries[(regime == 'TREND')] = trend_entry
            exits[(regime == 'TREND')] = trend_exit
            
            # RANGE状态使用震荡策略
            entries[(regime == 'RANGE')] = range_entry
            exits[(regime == 'RANGE')] = range_exit
            
            # 应用波动过滤
            if vol_filter is not None:
                entries = entries & vol_filter
                logger.info("应用波动过滤完成")
            
            self.entries = entries
            self.exits = exits
            self.regime = regime
            
            # 统计信号数量
            entry_count = entries.sum()
            exit_count = exits.sum()
            logger.info(f"策略融合完成: 买入信号={entry_count}, 卖出信号={exit_count}")
            
            return entries, exits
        except Exception as e:
            logger.error(f"融合策略失败: {e}")
            return None, None
    
    def get_signal_stats(self):
        """
        获取信号统计信息
        
        Returns:
            dict: 信号统计信息
        """
        if self.entries is None or self.exits is None:
            logger.warning("信号尚未生成")
            return None
        
        try:
            stats = {
                'total_entries': self.entries.sum(),
                'total_exits': self.exits.sum(),
                'entry_rate': self.entries.mean(),
                'exit_rate': self.exits.mean()
            }
            
            # 按Regime统计
            if self.regime is not None:
                stats['trend_entries'] = self.entries[self.regime == 'TREND'].sum()
                stats['trend_exits'] = self.exits[self.regime == 'TREND'].sum()
                stats['range_entries'] = self.entries[self.regime == 'RANGE'].sum()
                stats['range_exits'] = self.exits[self.regime == 'RANGE'].sum()
            
            return stats
        except Exception as e:
            logger.error(f"获取信号统计信息失败: {e}")
            return None
    
    def run(self, regime, fast_ma, slow_ma, rsi, atr, **params):
        """
        运行完整的多策略流程
        
        Args:
            regime: 市场状态序列
            fast_ma: 快线移动平均
            slow_ma: 慢线移动平均
            rsi: RSI指标
            atr: ATR波动率
            **params: 其他参数
        
        Returns:
            tuple: (最终entry信号, 最终exit信号)
        """
        # 生成趋势策略信号
        trend_entry, trend_exit = self.generate_trend_signals(fast_ma, slow_ma)
        
        if trend_entry is None:
            return None, None
        
        # 生成震荡策略信号
        rsi_entry_th = params.get('rsi_entry_threshold', 30)
        rsi_exit_th = params.get('rsi_exit_threshold', 55)
        range_entry, range_exit = self.generate_range_signals(rsi, rsi_entry_th, rsi_exit_th)
        
        if range_entry is None:
            return None, None
        
        # 生成波动过滤信号
        vol_window = params.get('volatility_filter_window', 50)
        vol_filter = self.generate_volatility_filter(atr, vol_window)
        
        # 融合策略
        entries, exits = self.fuse_strategies(
            regime, 
            trend_entry, 
            trend_exit, 
            range_entry, 
            range_exit, 
            vol_filter
        )
        
        # 输出统计信息
        stats = self.get_signal_stats()
        if stats:
            logger.info(f"信号统计: {stats}")
        
        return entries, exits
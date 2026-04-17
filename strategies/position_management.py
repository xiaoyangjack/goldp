import pandas as pd
import numpy as np
from loguru import logger


class PositionManager:
    """
    仓位管理模块
    负责根据波动率目标计算动态仓位
    """
    
    def __init__(self, price):
        """
        初始化仓位管理器
        
        Args:
            price: 价格序列
        """
        self.price = price
        self.returns = price.pct_change()
        self.position_size = None
    
    def calculate_volatility_target_position(self, target_vol=0.15, window=20):
        """
        计算波动率目标仓位
        
        Args:
            target_vol: 年化目标波动率
            window: 滚动窗口大小
        
        Returns:
            pd.Series: 仓位大小序列
        """
        try:
            # 计算滚动年化波动率
            realized_vol = self.returns.rolling(window).std() * np.sqrt(252)
            
            # 计算仓位大小
            position_size = target_vol / realized_vol
            
            # 限制仓位范围
            position_size = position_size.clip(0, 1)
            
            # 处理NaN值
            position_size = position_size.fillna(0)
            
            self.position_size = position_size
            
            logger.info(f"计算波动率目标仓位完成: target_vol={target_vol}, window={window}")
            return position_size
        except Exception as e:
            logger.error(f"计算波动率目标仓位失败: {e}")
            return None
    
    def calculate_fixed_position(self, fixed_size=0.5):
        """
        计算固定仓位
        
        Args:
            fixed_size: 固定仓位大小
        
        Returns:
            pd.Series: 仓位大小序列
        """
        try:
            position_size = pd.Series(fixed_size, index=self.price.index)
            self.position_size = position_size
            
            logger.info(f"计算固定仓位完成: size={fixed_size}")
            return position_size
        except Exception as e:
            logger.error(f"计算固定仓位失败: {e}")
            return None
    
    def get_position_stats(self):
        """
        获取仓位统计信息
        
        Returns:
            dict: 仓位统计信息
        """
        if self.position_size is None:
            logger.warning("仓位尚未计算")
            return None
        
        try:
            stats = {
                'mean_position': self.position_size.mean(),
                'max_position': self.position_size.max(),
                'min_position': self.position_size.min(),
                'std_position': self.position_size.std(),
                'median_position': self.position_size.median()
            }
            
            return stats
        except Exception as e:
            logger.error(f"获取仓位统计信息失败: {e}")
            return None
    
    def plot_position(self):
        """
        绘制仓位图表
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # 价格图表
            ax1.plot(self.price.index, self.price, label='Price')
            ax1.set_title('Price and Position Size')
            ax1.legend()
            
            # 仓位图表
            ax2.plot(self.position_size.index, self.position_size, label='Position Size', color='orange')
            ax2.set_ylim(0, 1.1)
            ax2.set_ylabel('Position Size')
            ax2.legend()
            
            plt.tight_layout()
            plt.savefig('backtest/position_analysis.png')
            plt.close()
            
            logger.info("仓位图表生成成功")
        except Exception as e:
            logger.error(f"绘制仓位图表失败: {e}")
    
    def run(self, method='volatility_target', **params):
        """
        运行仓位管理
        
        Args:
            method: 仓位管理方法 ('volatility_target' 或 'fixed')
            **params: 方法参数
        
        Returns:
            pd.Series: 仓位大小序列
        """
        if method == 'volatility_target':
            target_vol = params.get('target_vol', 0.15)
            window = params.get('window', 20)
            position_size = self.calculate_volatility_target_position(target_vol, window)
        elif method == 'fixed':
            fixed_size = params.get('fixed_size', 0.5)
            position_size = self.calculate_fixed_position(fixed_size)
        else:
            logger.error(f"不支持的仓位管理方法: {method}")
            return None
        
        if position_size is not None:
            # 绘制仓位图表
            self.plot_position()
            
            # 输出统计信息
            stats = self.get_position_stats()
            if stats:
                logger.info(f"仓位统计: {stats}")
        
        return position_size
import pandas as pd
import numpy as np
from loguru import logger


class RegimeIdentifier:
    """
    Regime判定模块
    负责识别市场状态（TREND/RANGE）
    """
    
    def __init__(self, price):
        """
        初始化Regime判定器
        
        Args:
            price: 价格序列
        """
        self.price = price
        self.regime = None
        self.trend_strength = None
        self.threshold = None
    
    def calculate_trend_strength(self, fast_ma, slow_ma, atr):
        """
        计算趋势强度
        
        Args:
            fast_ma: 快线移动平均
            slow_ma: 慢线移动平均
            atr: ATR波动率
        
        Returns:
            pd.Series: 趋势强度序列
        """
        try:
            # 计算均线差的绝对值
            ma_diff = (fast_ma - slow_ma).abs()
            
            # 除以ATR得到趋势强度
            trend_strength = ma_diff / atr
            
            # 处理NaN值
            trend_strength = trend_strength.fillna(0)
            
            self.trend_strength = trend_strength
            
            logger.info("计算趋势强度完成")
            return trend_strength
        except Exception as e:
            logger.error(f"计算趋势强度失败: {e}")
            return None
    
    def identify_regime(self, trend_strength, threshold=None, quantile=0.7):
        """
        识别市场状态
        
        Args:
            trend_strength: 趋势强度序列
            threshold: 手动设置的阈值
            quantile: 自动计算阈值的分位数
        
        Returns:
            pd.Series: 市场状态序列
        """
        try:
            if threshold is None:
                # 自动计算阈值
                threshold = trend_strength.quantile(quantile)
                logger.info(f"自动计算Regime阈值: {threshold:.4f}")
            else:
                logger.info(f"使用手动Regime阈值: {threshold:.4f}")
            
            self.threshold = threshold
            
            # 初始化Regime序列
            regime = pd.Series(index=self.price.index, data='RANGE')
            
            # 根据趋势强度设置状态
            regime[trend_strength > threshold] = 'TREND'
            
            self.regime = regime
            
            # 统计各状态的比例
            trend_count = (regime == 'TREND').sum()
            range_count = (regime == 'RANGE').sum()
            total_count = len(regime)
            
            logger.info(f"Regime识别完成: TREND={trend_count} ({trend_count/total_count:.2%}), RANGE={range_count} ({range_count/total_count:.2%})")
            return regime
        except Exception as e:
            logger.error(f"识别Regime失败: {e}")
            return None
    
    def get_regime_stats(self):
        """
        获取Regime统计信息
        
        Returns:
            dict: Regime统计信息
        """
        if self.regime is None:
            logger.warning("Regime尚未识别")
            return None
        
        try:
            stats = {
                'total_periods': len(self.regime),
                'trend_periods': (self.regime == 'TREND').sum(),
                'range_periods': (self.regime == 'RANGE').sum(),
                'trend_percentage': (self.regime == 'TREND').mean(),
                'range_percentage': (self.regime == 'RANGE').mean(),
                'threshold': self.threshold
            }
            
            return stats
        except Exception as e:
            logger.error(f"获取Regime统计信息失败: {e}")
            return None
    
    def plot_regime(self):
        """
        绘制Regime图表
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # 价格图表
            ax1.plot(self.price.index, self.price, label='Price')
            ax1.set_title('Price and Regime')
            ax1.legend()
            
            # Regime图表
            regime_colors = {'TREND': 'green', 'RANGE': 'red'}
            regime_values = self.regime.map({'TREND': 1, 'RANGE': 0})
            ax2.fill_between(self.regime.index, 0, 1, where=regime_values == 1, color='green', alpha=0.3, label='TREND')
            ax2.fill_between(self.regime.index, 0, 1, where=regime_values == 0, color='red', alpha=0.3, label='RANGE')
            ax2.set_ylim(0, 1)
            ax2.set_yticks([0, 1])
            ax2.set_yticklabels(['RANGE', 'TREND'])
            ax2.legend()
            
            plt.tight_layout()
            plt.savefig('backtest/regime_analysis.png')
            plt.close()
            
            logger.info("Regime图表生成成功")
        except Exception as e:
            logger.error(f"绘制Regime图表失败: {e}")
    
    def run(self, fast_ma, slow_ma, atr, **params):
        """
        运行完整的Regime识别流程
        
        Args:
            fast_ma: 快线移动平均
            slow_ma: 慢线移动平均
            atr: ATR波动率
            **params: 其他参数
        
        Returns:
            pd.Series: 市场状态序列
        """
        threshold = params.get('threshold', None)
        quantile = params.get('quantile', 0.7)
        
        # 计算趋势强度
        trend_strength = self.calculate_trend_strength(fast_ma, slow_ma, atr)
        
        if trend_strength is None:
            return None
        
        # 识别Regime
        regime = self.identify_regime(trend_strength, threshold, quantile)
        
        # 绘制Regime图表
        self.plot_regime()
        
        # 输出统计信息
        stats = self.get_regime_stats()
        if stats:
            logger.info(f"Regime统计: {stats}")
        
        return regime
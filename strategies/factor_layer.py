import pandas as pd
import numpy as np
import vectorbt as vbt
from loguru import logger


class FactorLayer:
    """
    因子计算层
    负责计算各种技术指标和因子
    """
    
    def __init__(self, price):
        """
        初始化因子层
        
        Args:
            price: 价格序列
        """
        self.price = price
        self.returns = price.pct_change()
        self.factors = {}
    
    def calculate_moving_averages(self, fast_window=20, slow_window=60):
        """
        计算移动平均线
        
        Args:
            fast_window: 快线窗口
            slow_window: 慢线窗口
        """
        try:
            fast_ma = vbt.MA.run(self.price, window=fast_window).ma
            slow_ma = vbt.MA.run(self.price, window=slow_window).ma
            
            self.factors['fast_ma'] = fast_ma
            self.factors['slow_ma'] = slow_ma
            
            logger.info(f"计算移动平均线: fast={fast_window}, slow={slow_window}")
            return fast_ma, slow_ma
        except Exception as e:
            logger.error(f"计算移动平均线失败: {e}")
            return None, None
    
    def calculate_rsi(self, window=14):
        """
        计算RSI指标
        
        Args:
            window: 窗口大小
        """
        try:
            rsi = vbt.RSI.run(self.price, window=window).rsi
            self.factors['rsi'] = rsi
            
            logger.info(f"计算RSI指标: window={window}")
            return rsi
        except Exception as e:
            logger.error(f"计算RSI指标失败: {e}")
            return None
    
    def calculate_atr(self, window=14):
        """
        计算ATR波动率
        
        Args:
            window: 窗口大小
        """
        try:
            # 需要高低收数据
            if hasattr(self, 'high') and hasattr(self, 'low'):
                # 确保数据长度一致
                high = self.high
                low = self.low
                close = self.price
                
                # 计算真实波幅
                true_range = pd.DataFrame({
                    'hl': high - low,
                    'hc': abs(high - close.shift(1)),
                    'lc': abs(low - close.shift(1))
                }).max(axis=1)
                
                # 计算ATR
                atr = true_range.rolling(window).mean()
            else:
                # 如果只有收盘价，使用简化计算
                atr = self.price.rolling(window).std() * np.sqrt(252)
            
            self.factors['atr'] = atr
            
            logger.info(f"计算ATR波动率: window={window}")
            return atr
        except Exception as e:
            logger.error(f"计算ATR波动率失败: {e}")
            return None
    
    def calculate_volatility(self, window=20):
        """
        计算收益率波动率
        
        Args:
            window: 窗口大小
        """
        try:
            vol = self.returns.rolling(window).std() * np.sqrt(252)
            self.factors['volatility'] = vol
            
            logger.info(f"计算收益率波动率: window={window}")
            return vol
        except Exception as e:
            logger.error(f"计算收益率波动率失败: {e}")
            return None
    
    def set_ohlcv(self, high, low, close=None):
        """
        设置OHLCV数据
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列（可选）
        """
        self.high = high
        self.low = low
        if close is not None:
            self.price = close
            self.returns = self.price.pct_change()
    
    def get_all_factors(self):
        """
        获取所有计算的因子
        
        Returns:
            dict: 因子字典
        """
        return self.factors
    
    def calculate_all_factors(self, **params):
        """
        计算所有因子
        
        Args:
            **params: 因子参数
        """
        fast_window = params.get('fast_window', 20)
        slow_window = params.get('slow_window', 60)
        rsi_window = params.get('rsi_window', 14)
        atr_window = params.get('atr_window', 14)
        vol_window = params.get('vol_window', 20)
        
        self.calculate_moving_averages(fast_window, slow_window)
        self.calculate_rsi(rsi_window)
        self.calculate_atr(atr_window)
        self.calculate_volatility(vol_window)
        
        logger.info("所有因子计算完成")
        return self.factors
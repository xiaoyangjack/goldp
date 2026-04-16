"""
策略基类
所有策略都继承自这个基类，统一接口
"""
import pandas as pd
from abc import ABC, abstractmethod

# 尝试导入 pandas_ta
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
except ImportError:
    PANDAS_TA_AVAILABLE = False


class BaseStrategy(ABC):
    """
    策略基类
    所有策略都必须实现 generate_signals 方法
    """
    
    def __init__(self, **params):
        """
        初始化策略
        
        Args:
            params: 策略参数
        """
        self.params = params
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> dict:
        """
        生成交易信号
        
        Args:
            df: 包含价格数据的DataFrame，必须包含 'close' 列
        
        Returns:
            dict: 包含 entries 和 exits 的字典
                  entries: 买入信号（布尔数组）
                  exits: 卖出信号（布尔数组）
        """
        pass
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算通用指标
        
        Args:
            df: 原始数据
        
        Returns:
            pd.DataFrame: 包含指标的数据
        """
        # 计算MA
        if 'ma10' not in df.columns:
            df['ma10'] = df['close'].rolling(window=10).mean()
        if 'ma30' not in df.columns:
            df['ma30'] = df['close'].rolling(window=30).mean()
        
        # 计算ATR
        if 'atr' not in df.columns and 'high' in df.columns and 'low' in df.columns:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift(1))
            low_close = abs(df['low'] - df['close'].shift(1))
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['atr'] = true_range.rolling(window=14).mean()
        
        # 使用 pandas_ta 计算更多指标
        if PANDAS_TA_AVAILABLE:
            try:
                # 计算 RSI
                if 'rsi' not in df.columns:
                    df['rsi'] = ta.rsi(df['close'], length=14)
                
                # 计算 MACD
                if 'macd' not in df.columns:
                    macd = ta.macd(df['close'])
                    if not macd.empty:
                        df = df.join(macd)
                
                # 计算 Bollinger Bands
                if 'bb_upper' not in df.columns:
                    bbands = ta.bbands(df['close'])
                    if not bbands.empty:
                        df = df.join(bbands)
            except Exception as e:
                # pandas_ta 计算失败时忽略
                pass
        
        return df
    
    def get_params(self) -> dict:
        """
        获取策略参数
        
        Returns:
            dict: 策略参数
        """
        return self.params
    
    def set_params(self, **params):
        """
        设置策略参数
        
        Args:
            params: 策略参数
        """
        self.params.update(params)
    
    def __str__(self):
        return f"{self.name}({self.params})"

import pandas as pd
import numpy as np
from loguru import logger


class FactorEngine:
    """
    因子引擎 - 计算各种技术指标和因子
    
    接受 DataEngine 输出，计算以下所有因子：
    
    趋势类：
    - SMA双均线
    - MACD
    
    震荡类：
    - RSI
    - 布林带
    
    波动类：
    - ATR
    
    动量类：
    - 20日价格动量
    - 60日价格动量
    
    宏观类：
    - DXY 5日均线
    """
    
    def __init__(self):
        self.factor_data = None
    
    def calculate_all_factors(self, df):
        """
        计算所有因子
        
        Args:
            df: 包含价格数据的DataFrame
        
        Returns:
            pd.DataFrame: 新增所有因子列的DataFrame
        """
        if df is None or len(df) == 0:
            logger.error("数据为空，无法计算因子")
            return None
        
        result_df = df.copy()
        
        # 趋势类因子
        result_df = self._calculate_sma(result_df)
        result_df = self._calculate_macd(result_df)
        
        # 震荡类因子
        result_df = self._calculate_rsi(result_df)
        result_df = self._calculate_bollinger_bands(result_df)
        
        # 波动类因子
        result_df = self._calculate_atr(result_df)
        
        # 动量类因子
        result_df = self._calculate_momentum(result_df)
        
        # 宏观类因子
        if 'dxy_close' in result_df.columns:
            result_df = self._calculate_dxy_factors(result_df)
        
        # 计算市场状态（Regime）
        result_df = self._calculate_regime(result_df)
        
        # 计算扩展因子
        try:
            from core.extended_factors import ExtendedFactors
            extended = ExtendedFactors()
            result_df = extended.calculate_all_extended_factors(result_df)
        except Exception as e:
            logger.warning(f"计算扩展因子失败: {e}")
        
        # 计算因子有效性评分体系
        try:
            from core.factor_effectiveness import FactorEffectiveness
            factor_effectiveness = FactorEffectiveness()
            result_df = factor_effectiveness.calculate_factor_effectiveness(result_df)
        except Exception as e:
            logger.warning(f"计算因子有效性失败: {e}")
        
        self.factor_data = result_df
        logger.info("所有因子计算完成")
        return result_df
    
    def _calculate_sma(self, df, fast_period=20, slow_period=60):
        """
        计算SMA双均线
        
        Args:
            df: 价格数据
            fast_period: 快线周期
            slow_period: 慢线周期
        
        Returns:
            pd.DataFrame: 包含SMA因子的DataFrame
        """
        df = df.copy()
        df['sma_fast'] = df['close'].rolling(window=fast_period).mean()
        df['sma_slow'] = df['close'].rolling(window=slow_period).mean()
        
        # SMA交叉信号
        df['sma_signal'] = 0
        df.loc[df['sma_fast'] > df['sma_slow'], 'sma_signal'] = 1
        df.loc[df['sma_fast'] < df['sma_slow'], 'sma_signal'] = -1
        
        logger.info(f"SMA计算完成: fast={fast_period}, slow={slow_period}")
        return df
    
    def _calculate_macd(self, df, fast_period=12, slow_period=26, signal_period=9):
        """
        计算MACD
        
        Args:
            df: 价格数据
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
        
        Returns:
            pd.DataFrame: 包含MACD因子的DataFrame
        """
        df = df.copy()
        
        # 计算EMA
        df['ema_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线和信号线
        df['macd_line'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd_line'].ewm(span=signal_period, adjust=False).mean()
        df['macd_histogram'] = df['macd_line'] - df['macd_signal']
        
        # MACD信号
        df['macd_signal_flag'] = 0
        df.loc[(df['macd_histogram'] > 0) & (df['macd_histogram'].shift(1) <= 0), 'macd_signal_flag'] = 1
        df.loc[(df['macd_histogram'] < 0) & (df['macd_histogram'].shift(1) >= 0), 'macd_signal_flag'] = -1
        
        logger.info(f"MACD计算完成: fast={fast_period}, slow={slow_period}, signal={signal_period}")
        return df
    
    def _calculate_rsi(self, df, period=14):
        """
        计算RSI
        
        Args:
            df: 价格数据
            period: RSI周期
        
        Returns:
            pd.DataFrame: 包含RSI因子的DataFrame
        """
        df = df.copy()
        
        # 计算价格变化
        delta = df['close'].diff()
        
        # 分离涨跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # 计算RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # RSI超买超卖信号
        df['rsi_signal'] = 0
        df.loc[df['rsi'] < 35, 'rsi_signal'] = 1  # 超卖，买入
        df.loc[df['rsi'] > 65, 'rsi_signal'] = -1  # 超买，卖出
        
        logger.info(f"RSI计算完成: period={period}")
        return df
    
    def _calculate_bollinger_bands(self, df, period=20, std_multiplier=2.0):
        """
        计算布林带
        
        Args:
            df: 价格数据
            period: 周期
            std_multiplier: 标准差倍数
        
        Returns:
            pd.DataFrame: 包含布林带因子的DataFrame
        """
        df = df.copy()
        
        # 计算中轨、上轨、下轨
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        df['bb_std'] = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (std_multiplier * df['bb_std'])
        df['bb_lower'] = df['bb_middle'] - (std_multiplier * df['bb_std'])
        
        # 布林带位置
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # 布林带信号
        df['bb_signal'] = 0
        df.loc[df['bb_position'] < 0.1, 'bb_signal'] = 1  # 下轨附近，买入
        df.loc[df['bb_position'] > 0.9, 'bb_signal'] = -1  # 上轨附近，卖出
        
        logger.info(f"布林带计算完成: period={period}, std={std_multiplier}")
        return df
    
    def _calculate_atr(self, df, period=14):
        """
        计算ATR
        
        Args:
            df: 价格数据
            period: ATR周期
        
        Returns:
            pd.DataFrame: 包含ATR因子的DataFrame
        """
        df = df.copy()
        
        # 计算真实波幅
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # 计算ATR
        df['atr'] = true_range.rolling(window=period).mean()
        
        # ATR百分比
        df['atr_pct'] = df['atr'] / df['close']
        
        logger.info(f"ATR计算完成: period={period}")
        return df
    
    def _calculate_momentum(self, df, periods=[20, 60]):
        """
        计算动量因子
        
        Args:
            df: 价格数据
            periods: 动量周期列表
        
        Returns:
            pd.DataFrame: 包含动量因子的DataFrame
        """
        df = df.copy()
        
        for period in periods:
            # 简单动量
            df[f'momentum_{period}d'] = df['close'] / df['close'].shift(period) - 1
            
            # 动量信号
            df[f'momentum_{period}d_signal'] = 0
            df.loc[df[f'momentum_{period}d'] > 0, f'momentum_{period}d_signal'] = 1
            df.loc[df[f'momentum_{period}d'] < 0, f'momentum_{period}d_signal'] = -1
        
        logger.info(f"动量计算完成: periods={periods}")
        return df
    
    def _calculate_dxy_factors(self, df, period=5):
        """
        计算DXY相关因子
        
        Args:
            df: 价格数据
            period: DXY均线周期
        
        Returns:
            pd.DataFrame: 包含DXY因子的DataFrame
        """
        df = df.copy()
        
        # DXY 5日均线
        df['dxy_ma5'] = df['dxy_close'].rolling(window=period).mean()
        
        # DXY上穿信号（用于宏观过滤）
        df['dxy_cross_up'] = 0
        df.loc[(df['dxy_close'] > df['dxy_ma5']) & (df['dxy_close'].shift(1) <= df['dxy_ma5'].shift(1)), 'dxy_cross_up'] = 1
        
        logger.info(f"DXY因子计算完成: period={period}")
        return df
    
    def _calculate_regime(self, df, fast_period=20, slow_period=60, atr_period=14, quantile=0.7):
        """
        计算市场状态（Regime）
        
        Args:
            df: 价格数据
            fast_period: 快线周期
            slow_period: 慢线周期
            atr_period: ATR周期
            quantile: 趋势强度阈值分位数
        
        Returns:
            pd.DataFrame: 包含Regime的DataFrame
        """
        df = df.copy()
        
        # 计算趋势强度
        trend_strength = (df['sma_fast'] - df['sma_slow']).abs() / df['atr']
        
        # 计算阈值
        TREND_TH = trend_strength.quantile(quantile)
        
        # 分类市场状态
        df['regime'] = 'RANGE'
        df.loc[trend_strength > TREND_TH, 'regime'] = 'TREND'
        
        logger.info(f"Regime计算完成: 阈值={TREND_TH:.4f}, TREND占比={(df['regime'] == 'TREND').mean():.2%}")
        return df
    
    def get_factor_list(self):
        """
        获取因子列表
        
        Returns:
            list: 因子列名列表
        """
        if self.factor_data is None:
            return []
        
        return [col for col in self.factor_data.columns if col not in ['open', 'high', 'low', 'close', 'volume']]
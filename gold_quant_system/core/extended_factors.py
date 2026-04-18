#!/usr/bin/env python3
"""
扩展因子模块
包含基本面、成长、资金流、事件驱动、宏观与行业等因子
"""

import pandas as pd
import numpy as np
from loguru import logger


class ExtendedFactors:
    """扩展因子计算器"""
    
    def __init__(self):
        pass
    
    def calculate_all_extended_factors(self, df):
        """
        计算所有扩展因子
        
        Args:
            df: 包含价格数据的DataFrame
        
        Returns:
            pd.DataFrame: 新增扩展因子列的DataFrame
        """
        if df is None or len(df) == 0:
            logger.error("数据为空，无法计算扩展因子")
            return df
        
        result_df = df.copy()
        
        try:
            result_df = self._calculate_value_factors(result_df)
            result_df = self._calculate_quality_factors(result_df)
            result_df = self._calculate_growth_factors(result_df)
            result_df = self._calculate_money_flow_factors(result_df)
            result_df = self._calculate_macro_factors(result_df)
            result_df = self._calculate_style_factors(result_df)
            
            logger.info("所有扩展因子计算完成")
        except Exception as e:
            logger.error(f"计算扩展因子时出错: {e}")
        
        return result_df
    
    def _calculate_value_factors(self, df):
        """
        计算价值类因子（适用于大宗商品）
        
        对于黄金等大宗商品，我们用价格相对于历史的估值来模拟价值因子
        """
        result_df = df.copy()
        
        try:
            close = result_df['close']
            
            result_df['value_price_to_ma200'] = close / close.rolling(window=200).mean()
            result_df['value_price_to_ma100'] = close / close.rolling(window=100).mean()
            result_df['value_price_to_ma50'] = close / close.rolling(window=50).mean()
            
            result_df['value_price_rank_20d'] = close.rolling(window=20).rank(pct=True)
            result_df['value_price_rank_60d'] = close.rolling(window=60).rank(pct=True)
            result_df['value_price_rank_120d'] = close.rolling(window=120).rank(pct=True)
            
            logger.info("价值因子计算完成")
        except Exception as e:
            logger.error(f"计算价值因子失败: {e}")
        
        return result_df
    
    def _calculate_quality_factors(self, df):
        """
        计算质量类因子（适用于大宗商品）
        
        对于大宗商品，质量因子用波动率、趋势稳定性等指标来模拟
        """
        result_df = df.copy()
        
        try:
            close = result_df['close']
            high = result_df['high']
            low = result_df['low']
            
            returns = close.pct_change()
            
            result_df['quality_volatility_20d'] = returns.rolling(window=20).std()
            result_df['quality_volatility_60d'] = returns.rolling(window=60).std()
            
            result_df['quality_trend_stability'] = (
                close.rolling(window=20).mean().pct_change().abs().rolling(window=20).std()
            )
            
            true_range = pd.concat([high - low, 
                                   (high - close.shift()).abs(), 
                                   (low - close.shift()).abs()], axis=1).max(axis=1)
            result_df['quality_range_stability'] = true_range.rolling(window=20).std()
            
            result_df['quality_gap_risk'] = (result_df['open'] - close.shift()).abs() / close.shift()
            
            logger.info("质量因子计算完成")
        except Exception as e:
            logger.error(f"计算质量因子失败: {e}")
        
        return result_df
    
    def _calculate_growth_factors(self, df):
        """
        计算成长类因子（适用于大宗商品）
        
        对于大宗商品，成长因子用价格动量、加速度等指标来模拟
        """
        result_df = df.copy()
        
        try:
            close = result_df['close']
            
            result_df['growth_momentum_5d'] = close / close.shift(5) - 1
            result_df['growth_momentum_10d'] = close / close.shift(10) - 1
            result_df['growth_momentum_20d'] = close / close.shift(20) - 1
            
            mom5 = result_df['growth_momentum_5d']
            mom10 = result_df['growth_momentum_10d']
            result_df['growth_acceleration'] = mom5 - mom10.shift(5)
            
            result_df['growth_sma_slope_20d'] = (
                close.rolling(window=20).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=True)
            )
            
            result_df['growth_sma_slope_60d'] = (
                close.rolling(window=60).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=True)
            )
            
            logger.info("成长因子计算完成")
        except Exception as e:
            logger.error(f"计算成长因子失败: {e}")
        
        return result_df
    
    def _calculate_money_flow_factors(self, df):
        """
        计算资金流因子（适用于大宗商品）
        """
        result_df = df.copy()
        
        try:
            close = result_df['close']
            high = result_df['high']
            low = result_df['low']
            volume = result_df.get('volume', pd.Series(1, index=result_df.index))
            
            typical_price = (high + low + close) / 3
            money_flow = typical_price * volume
            
            result_df['flow_money_flow'] = money_flow
            
            positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
            negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
            
            result_df['flow_mfi_14d'] = self._calculate_mfi(positive_flow, negative_flow, 14)
            result_df['flow_mfi_7d'] = self._calculate_mfi(positive_flow, negative_flow, 7)
            
            result_df['flow_obv'] = (np.sign(close.diff()) * volume).fillna(0).cumsum()
            result_df['flow_obv_ma_diff'] = (
                result_df['flow_obv'] - result_df['flow_obv'].rolling(window=10).mean()
            )
            
            price_change = close.pct_change()
            result_df['flow_volume_price_corr'] = (
                price_change.rolling(window=20).corr(volume.pct_change())
            )
            
            logger.info("资金流因子计算完成")
        except Exception as e:
            logger.error(f"计算资金流因子失败: {e}")
        
        return result_df
    
    def _calculate_mfi(self, positive_flow, negative_flow, period):
        """计算资金流量指标"""
        pos_sum = positive_flow.rolling(window=period).sum()
        neg_sum = negative_flow.rolling(window=period).sum()
        mfi = 100 - (100 / (1 + pos_sum / neg_sum.replace(0, np.nan)))
        return mfi
    
    def _calculate_macro_factors(self, df):
        """
        计算宏观因子
        """
        result_df = df.copy()
        
        try:
            close = result_df['close']
            
            result_df['macro_day_of_week'] = result_df.index.dayofweek
            result_df['macro_day_of_month'] = result_df.index.day
            result_df['macro_month'] = result_df.index.month
            result_df['macro_quarter'] = result_df.index.quarter
            
            result_df['macro_monthly_seasonality'] = (
                close.groupby(close.index.month).transform('mean') / close.mean()
            )
            
            if 'dxy_close' in result_df.columns:
                dxy = result_df['dxy_close']
                result_df['macro_dxy_momentum_5d'] = dxy / dxy.shift(5) - 1
                result_df['macro_dxy_momentum_20d'] = dxy / dxy.shift(20) - 1
                result_df['macro_gold_dxy_corr_20d'] = (
                    close.pct_change().rolling(window=20).corr(dxy.pct_change())
                )
            
            logger.info("宏观因子计算完成")
        except Exception as e:
            logger.error(f"计算宏观因子失败: {e}")
        
        return result_df
    
    def _calculate_style_factors(self, df):
        """
        计算风格因子
        """
        result_df = df.copy()
        
        try:
            close = result_df['close']
            returns = close.pct_change()
            
            result_df['style_beta_20d'] = returns.rolling(window=20).std() * np.sqrt(252)
            
            result_df['style_illiquidity_20d'] = (
                returns.abs().rolling(window=20).mean() / 
                result_df.get('volume', pd.Series(1, index=result_df.index)).rolling(window=20).mean()
            )
            
            result_df['style_reversal_5d'] = -returns.rolling(window=5).sum()
            result_df['style_reversal_20d'] = -returns.rolling(window=20).sum()
            
            high_minus_low = (result_df['high'] - result_df['low']) / result_df['close']
            result_df['style_volatility'] = high_minus_low.rolling(window=20).mean()
            
            logger.info("风格因子计算完成")
        except Exception as e:
            logger.error(f"计算风格因子失败: {e}")
        
        return result_df

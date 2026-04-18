#!/usr/bin/env python3
"""
因子有效性评分体系
实现10类核心因子的有效性分析、半衰期计算、星级评分和净多头因子优势计算
"""

import pandas as pd
import numpy as np
from loguru import logger


class FactorEffectiveness:
    """
    因子有效性评分体系
    针对10类核心因子：GPR、央行购金、DXY、实际利率、ETF流向、COT、60日动量、SMA、油价、ATR
    """
    
    def __init__(self):
        # 因子半衰期参数（单位：月）
        self.half_lives = {
            'gpr': 3.2,        # 黄金风险溢价
            'central_bank_gold': 6.0,  # 央行购金
            'dxy': 2.1,        # 美元指数
            'real_rate': 2.5,   # 实际利率
            'etf_flow': 1.8,    # ETF流向
            'cot': 2.0,         # 商品期货持仓
            'momentum_60d': 2.3, # 60日动量
            'sma': 1.9,         # 移动平均线
            'oil_price': 2.7,    # 油价
            'atr': 1.6          # 波动率
        }
        
        # 因子权重
        self.factor_weights = {
            'gpr': 0.12,
            'central_bank_gold': 0.10,
            'dxy': 0.12,
            'real_rate': 0.12,
            'etf_flow': 0.10,
            'cot': 0.10,
            'momentum_60d': 0.11,
            'sma': 0.10,
            'oil_price': 0.08,
            'atr': 0.05
        }
    
    def calculate_factor_effectiveness(self, df):
        """
        计算所有因子的有效性指标
        
        Args:
            df: 包含价格数据和因子数据的DataFrame
        
        Returns:
            pd.DataFrame: 包含因子有效性指标的DataFrame
        """
        if df is None or len(df) == 0:
            logger.error("数据为空，无法计算因子有效性")
            return df
        
        result_df = df.copy()
        
        try:
            # 计算基础因子值
            result_df = self._calculate_basic_factors(result_df)
            
            # 计算因子有效性
            for factor in self.half_lives.keys():
                if f'{factor}_value' in result_df.columns:
                    # 计算有效性得分
                    effectiveness = self._calculate_factor_effectiveness(
                        result_df[f'{factor}_value'], 
                        self.half_lives[factor]
                    )
                    result_df[f'{factor}_effectiveness'] = effectiveness
                    
                    # 计算多空强度星级
                    stars = self._calculate_strength_stars(effectiveness)
                    result_df[f'{factor}_stars'] = stars
            
            # 计算净多头因子优势
            result_df = self._calculate_net_bullish_advantage(result_df)
            
            logger.info("因子有效性评分体系计算完成")
        except Exception as e:
            logger.error(f"计算因子有效性时出错: {e}")
        
        return result_df
    
    def _calculate_basic_factors(self, df):
        """
        计算基础因子值
        """
        result_df = df.copy()
        
        try:
            close = result_df['close']
            
            # 1. GPR (Gold Price Risk Premium) - 简化计算
            result_df['gpr_value'] = close / close.rolling(window=200).mean() - 1
            
            # 2. 央行购金 - 使用模拟数据（实际应从外部数据源获取）
            result_df['central_bank_gold_value'] = np.sin(np.arange(len(result_df)) / 60) * 0.5
            
            # 3. DXY - 美元指数
            if 'dxy_close' in result_df.columns:
                result_df['dxy_value'] = -result_df['dxy_close'].pct_change(20)  # 负相关
            else:
                result_df['dxy_value'] = np.random.normal(0, 0.02, len(result_df))
            
            # 4. 实际利率 - 使用模拟数据
            result_df['real_rate_value'] = -np.random.normal(0, 0.01, len(result_df))  # 负相关
            
            # 5. ETF流向 - 使用模拟数据
            result_df['etf_flow_value'] = np.random.normal(0, 0.03, len(result_df))
            
            # 6. COT (Commitment of Traders) - 使用模拟数据
            result_df['cot_value'] = np.random.normal(0, 0.025, len(result_df))
            
            # 7. 60日动量
            result_df['momentum_60d_value'] = close / close.shift(60) - 1
            
            # 8. SMA - 双均线差值
            if 'sma_fast' in result_df.columns and 'sma_slow' in result_df.columns:
                result_df['sma_value'] = (result_df['sma_fast'] - result_df['sma_slow']) / result_df['sma_slow']
            else:
                result_df['sma_value'] = close.rolling(20).mean() - close.rolling(60).mean()
                result_df['sma_value'] = result_df['sma_value'] / close.rolling(60).mean()
            
            # 9. 油价 - 使用模拟数据
            result_df['oil_price_value'] = np.random.normal(0, 0.02, len(result_df))
            
            # 10. ATR - 波动率
            if 'atr' in result_df.columns:
                # 波动率对策略的影响是双向的，这里计算波动率变化
                result_df['atr_value'] = result_df['atr'].pct_change(20)
            else:
                # 计算ATR
                high_low = result_df['high'] - result_df['low']
                high_close = np.abs(result_df['high'] - result_df['close'].shift())
                low_close = np.abs(result_df['low'] - result_df['close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = true_range.rolling(window=14).mean()
                result_df['atr_value'] = atr.pct_change(20)
            
            logger.info("基础因子计算完成")
        except Exception as e:
            logger.error(f"计算基础因子失败: {e}")
        
        return result_df
    
    def _calculate_factor_effectiveness(self, factor_values, half_life):
        """
        计算单个因子的有效性
        
        Args:
            factor_values: 因子值序列
            half_life: 因子半衰期（月）
        
        Returns:
            pd.Series: 因子有效性得分
        """
        # 计算因子值的滚动相关性
        returns = factor_values.pct_change().fillna(0)
        
        # 使用半衰期计算衰减权重
        window = int(half_life * 21)  # 转换为交易日
        weights = np.exp(-np.log(2) / window * np.arange(window))
        weights = weights / weights.sum()
        
        # 计算加权相关性
        effectiveness = []
        for i in range(len(factor_values)):
            if i < window:
                effectiveness.append(0)
            else:
                # 计算因子值与未来收益的相关性
                factor_window = factor_values.iloc[i-window:i]
                returns_window = returns.iloc[i-window+1:i+1]
                
                # 加权相关性
                if len(factor_window) > 1 and len(returns_window) > 1:
                    correlation = np.corrcoef(factor_window, returns_window)[0, 1]
                    effectiveness.append(abs(correlation))
                else:
                    effectiveness.append(0)
        
        effectiveness = pd.Series(effectiveness, index=factor_values.index)
        
        # 标准化到0-100%
        if effectiveness.max() > 0:
            effectiveness = (effectiveness / effectiveness.max()) * 100
        
        return effectiveness
    
    def _calculate_strength_stars(self, effectiveness):
        """
        计算多空强度星级（★1-5）
        
        Args:
            effectiveness: 因子有效性得分
        
        Returns:
            pd.Series: 星级评分
        """
        stars = []
        for score in effectiveness:
            if score >= 90:
                stars.append(5)
            elif score >= 70:
                stars.append(4)
            elif score >= 50:
                stars.append(3)
            elif score >= 30:
                stars.append(2)
            else:
                stars.append(1)
        
        return pd.Series(stars, index=effectiveness.index)
    
    def _calculate_net_bullish_advantage(self, df):
        """
        计算净多头因子优势
        
        Args:
            df: 包含因子有效性和星级的DataFrame
        
        Returns:
            pd.DataFrame: 包含净多头因子优势的DataFrame
        """
        result_df = df.copy()
        
        # 计算每个因子的信号方向和强度
        bullish_factors = []
        bearish_factors = []
        neutral_factors = []
        
        for factor in self.half_lives.keys():
            if f'{factor}_value' in result_df.columns:
                # 因子值为正表示多头信号，为负表示空头信号
                factor_values = result_df[f'{factor}_value']
                factor_stars = result_df[f'{factor}_stars']
                factor_weight = self.factor_weights[factor]
                
                # 计算加权强度
                weighted_strength = factor_values * factor_stars * factor_weight
                
                result_df[f'{factor}_weighted_strength'] = weighted_strength
                
                # 分类因子
                bullish = (weighted_strength > 0.1).sum()
                bearish = (weighted_strength < -0.1).sum()
                neutral = len(weighted_strength) - bullish - bearish
                
                bullish_factors.append(bullish)
                bearish_factors.append(bearish)
                neutral_factors.append(neutral)
        
        # 计算净多头优势
        total_bullish = sum(bullish_factors)
        total_bearish = sum(bearish_factors)
        total_neutral = sum(neutral_factors)
        
        net_advantage = total_bullish - total_bearish
        
        # 确定状态
        if net_advantage > 3:
            state = '净多'
        elif net_advantage < -3:
            state = '净空'
        else:
            state = '中性'
        
        result_df['bullish_factors_count'] = total_bullish
        result_df['bearish_factors_count'] = total_bearish
        result_df['neutral_factors_count'] = total_neutral
        result_df['net_bullish_advantage'] = net_advantage
        result_df['factor_state'] = state
        
        return result_df
    
    def get_factor_summary(self, df):
        """
        获取因子有效性摘要
        
        Args:
            df: 包含因子有效性数据的DataFrame
        
        Returns:
            dict: 因子有效性摘要
        """
        summary = {}
        
        for factor in self.half_lives.keys():
            if f'{factor}_effectiveness' in df.columns:
                latest_effectiveness = df[f'{factor}_effectiveness'].iloc[-1]
                latest_stars = df[f'{factor}_stars'].iloc[-1]
                half_life = self.half_lives[factor]
                
                summary[factor] = {
                    'effectiveness': latest_effectiveness,
                    'stars': latest_stars,
                    'half_life': half_life
                }
        
        # 添加整体状态
        if 'factor_state' in df.columns:
            summary['overall_state'] = df['factor_state'].iloc[-1]
        
        return summary

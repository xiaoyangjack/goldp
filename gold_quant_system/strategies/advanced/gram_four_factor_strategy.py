#!/usr/bin/env python3
"""
GRAM四因子模型策略

基于R、O、E、M四个因子的量化交易策略，包含权重优化和因子冲突处理
"""

import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict, List, Tuple


class GRAMFourFactorStrategy:
    """
    GRAM四因子模型策略
    
    因子定义：
    - R (Return): 收益率因子
    - O (Opportunity): 机会因子
    - E (Economic): 经济因子
    - M (Momentum): 动量因子
    """
    
    def __init__(self):
        """初始化GRAM四因子策略"""
        self.base_weights = {
            'R': 0.40,  # 提升至40%
            'O': 0.25,
            'E': 0.20,
            'M': 0.15
        }
        self.factor_data = None
    
    def calculate_gram_factors(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算GRAM四因子
        
        Args:
            df: 包含价格数据的DataFrame
            
        Returns:
            pd.DataFrame: 包含GRAM因子的DataFrame
        """
        result_df = df.copy()
        
        # 计算R因子 (Return)
        result_df = self._calculate_r_factor(result_df)
        
        # 计算O因子 (Opportunity)
        result_df = self._calculate_o_factor(result_df)
        
        # 计算E因子 (Economic)
        result_df = self._calculate_e_factor(result_df)
        
        # 计算M因子 (Momentum)
        result_df = self._calculate_m_factor(result_df)
        
        # 计算加权得分
        result_df = self._calculate_weighted_score(result_df)
        
        # 生成交易信号
        result_df = self._generate_signals(result_df)
        
        self.factor_data = result_df
        logger.info("GRAM四因子计算完成")
        return result_df
    
    def _calculate_r_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算R因子 (收益率因子)
        """
        result_df = df.copy()
        
        # 计算不同周期的收益率
        result_df['r_1d'] = result_df['close'].pct_change(1)
        result_df['r_5d'] = result_df['close'].pct_change(5)
        result_df['r_20d'] = result_df['close'].pct_change(20)
        result_df['r_60d'] = result_df['close'].pct_change(60)
        
        # 综合收益率因子
        result_df['r_factor'] = (
            0.4 * result_df['r_5d'] +
            0.3 * result_df['r_20d'] +
            0.3 * result_df['r_60d']
        )
        
        # 标准化
        result_df['r_factor_norm'] = self._normalize_factor(result_df['r_factor'])
        
        return result_df
    
    def _calculate_o_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算O因子 (机会因子)，增加双维度权重修正系数
        """
        result_df = df.copy()
        
        # 计算波动率
        result_df['volatility_20d'] = result_df['close'].rolling(window=20).std()
        
        # 计算价格位置
        result_df['price_position'] = (
            (result_df['close'] - result_df['close'].rolling(window=20).min()) /
            (result_df['close'].rolling(window=20).max() - result_df['close'].rolling(window=20).min())
        )
        
        # 双维度权重修正系数
        result_df['o_weight_adjustment'] = 1.0 + (
            0.5 * (result_df['volatility_20d'] / result_df['volatility_20d'].rolling(window=60).mean()) +
            0.5 * abs(result_df['price_position'] - 0.5)
        )
        
        # 综合机会因子
        result_df['o_factor'] = (
            0.6 * result_df['volatility_20d'] +
            0.4 * result_df['price_position']
        ) * result_df['o_weight_adjustment']
        
        # 标准化
        result_df['o_factor_norm'] = self._normalize_factor(result_df['o_factor'])
        
        return result_df
    
    def _calculate_e_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算E因子 (经济因子)，叠加复合评分维度
        """
        result_df = df.copy()
        
        # 计算经济因子基础指标
        if 'dxy_close' in result_df.columns:
            result_df['dxy_change'] = result_df['dxy_close'].pct_change(1)
            result_df['dxy_ma5'] = result_df['dxy_close'].rolling(window=5).mean()
            result_df['dxy_trend'] = np.where(
                result_df['dxy_ma5'] > result_df['dxy_ma5'].shift(1), 1, -1
            )
        else:
            # 如果没有DXY数据，使用默认值
            result_df['dxy_trend'] = 0
        
        # 复合评分维度
        result_df['e_complex_score'] = (
            0.7 * (-result_df.get('dxy_trend', 0)) +  # DXY与黄金负相关
            0.3 * result_df['close'].rolling(window=60).corr(result_df.get('dxy_close', result_df['close']))
        )
        
        # 综合经济因子
        result_df['e_factor'] = result_df['e_complex_score']
        
        # 标准化
        result_df['e_factor_norm'] = self._normalize_factor(result_df['e_factor'])
        
        return result_df
    
    def _calculate_m_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算M因子 (动量因子)，加入修正项
        """
        result_df = df.copy()
        
        # 计算基础动量
        result_df['momentum_20d'] = result_df['close'].pct_change(20)
        result_df['momentum_60d'] = result_df['close'].pct_change(60)
        
        # 加入修正项（考虑波动率和趋势）
        result_df['m_adjustment'] = 1.0 + (
            0.3 * (result_df['close'].rolling(window=20).std() / result_df['close'].rolling(window=60).std()) +
            0.7 * np.where(result_df['close'] > result_df['close'].rolling(window=50).mean(), 1, -1)
        )
        
        # 综合动量因子
        result_df['m_factor'] = (
            0.6 * result_df['momentum_20d'] +
            0.4 * result_df['momentum_60d']
        ) * result_df['m_adjustment']
        
        # 标准化
        result_df['m_factor_norm'] = self._normalize_factor(result_df['m_factor'])
        
        return result_df
    
    def _normalize_factor(self, factor_series: pd.Series) -> pd.Series:
        """
        标准化因子
        """
        mean = factor_series.rolling(window=60).mean()
        std = factor_series.rolling(window=60).std()
        return (factor_series - mean) / std
    
    def _calculate_weighted_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算加权得分
        """
        result_df = df.copy()
        
        # 应用权重
        result_df['weighted_score'] = (
            self.base_weights['R'] * result_df['r_factor_norm'] +
            self.base_weights['O'] * result_df['o_factor_norm'] +
            self.base_weights['E'] * result_df['e_factor_norm'] +
            self.base_weights['M'] * result_df['m_factor_norm']
        )
        
        return result_df
    
    def _generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号，包含因子冲突处理
        """
        result_df = df.copy()
        
        # 计算各因子信号
        result_df['r_signal'] = np.where(result_df['r_factor_norm'] > 0.5, 1, 0)
        result_df['e_signal'] = np.where(result_df['e_factor_norm'] > 0.5, 1, 0)
        result_df['o_signal'] = np.where(result_df['o_factor_norm'] < -0.5, -1, 0)
        result_df['m_signal'] = np.where(result_df['m_factor_norm'] < -0.5, -1, 0)
        
        # 因子冲突处理
        def resolve_conflict(row):
            # R/E因子多头信号与O/M因子短期压制信号冲突
            if (row['r_signal'] == 1 or row['e_signal'] == 1) and (row['o_signal'] == -1 or row['m_signal'] == -1):
                return 0.5  # 半仓观望/分批建仓
            elif row['weighted_score'] > 0.5:
                return 1  # 多头
            elif row['weighted_score'] < -0.5:
                return -1  # 空头
            else:
                return 0  # 观望
        
        result_df['signal'] = result_df.apply(resolve_conflict, axis=1)
        
        return result_df
    
    def get_factor_weights(self) -> Dict[str, float]:
        """
        获取因子权重
        """
        return self.base_weights
    
    def get_factor_contribution(self) -> pd.DataFrame:
        """
        获取因子贡献度
        """
        if self.factor_data is None:
            logger.error("因子数据未计算")
            return pd.DataFrame()
        
        contribution = pd.DataFrame()
        contribution['R_contribution'] = self.base_weights['R'] * self.factor_data['r_factor_norm']
        contribution['O_contribution'] = self.base_weights['O'] * self.factor_data['o_factor_norm']
        contribution['E_contribution'] = self.base_weights['E'] * self.factor_data['e_factor_norm']
        contribution['M_contribution'] = self.base_weights['M'] * self.factor_data['m_factor_norm']
        contribution['total_score'] = self.factor_data['weighted_score']
        
        return contribution

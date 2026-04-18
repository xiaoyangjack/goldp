#!/usr/bin/env python3
"""
监控指标引擎 - 实现8类监控指标的实时监控与触发

包括：
1. CME降息概率（突破40% → O因子权重从-5%修正为+8%）
2. DXY 5日/20日均线（5日线下穿20日线 → 触发做多信号）
3. GLD/IAU ETF周度流向（连续2周净流出 → 触发信号B减仓规则）
4. CFTC COT净多仓（超历史90百分位 → 反转预警）
5. GPR指数（单月回落>20% → R因子权重下调15%）
6. WTI原油价格（跌破$100 → 触发R因子减弱警报）
7. ATR(14日)（用于动态止损）
8. SMA20/SMA60（死叉 → 触发信号B减仓规则）
"""

import pandas as pd
import numpy as np
import yfinance as yf
from loguru import logger
from typing import Dict, List, Tuple, Optional


class MonitoringEngine:
    """
    监控指标引擎
    """
    
    def __init__(self):
        """初始化监控指标引擎"""
        self.base_weights = {
            'R': 0.40,
            'O': 0.25,
            'E': 0.20,
            'M': 0.15
        }
        self.current_weights = self.base_weights.copy()
        self.signals = {}
    
    def calculate_monitoring_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有监控指标
        
        Args:
            df: 包含价格数据的DataFrame
            
        Returns:
            pd.DataFrame: 包含监控指标的DataFrame
        """
        result_df = df.copy()
        
        # 1. 计算DXY 5日/20日均线
        result_df = self._calculate_dxy_ma_cross(result_df)
        
        # 2. 计算SMA20/SMA60（死叉）
        result_df = self._calculate_sma_cross(result_df)
        
        # 3. 计算ATR(14日)
        result_df = self._calculate_atr(result_df)
        
        # 4. 计算其他需要外部数据的指标（模拟数据）
        result_df = self._calculate_external_indicators(result_df)
        
        # 5. 计算权重调整
        result_df = self._calculate_weight_adjustments(result_df)
        
        # 6. 生成触发信号
        result_df = self._generate_trigger_signals(result_df)
        
        return result_df
    
    def _calculate_dxy_ma_cross(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算DXY 5日/20日均线交叉
        """
        result_df = df.copy()
        
        if 'dxy_close' in result_df.columns:
            # 计算DXY的5日和20日均线
            result_df['dxy_ma5'] = result_df['dxy_close'].rolling(window=5).mean()
            result_df['dxy_ma20'] = result_df['dxy_close'].rolling(window=20).mean()
            
            # 5日线下穿20日线（黄金做多信号）
            result_df['dxy_cross_down'] = (
                (result_df['dxy_ma5'] < result_df['dxy_ma20']) & 
                (result_df['dxy_ma5'].shift(1) >= result_df['dxy_ma20'].shift(1))
            ).astype(int)
        else:
            # 如果没有DXY数据，使用默认值
            result_df['dxy_cross_down'] = 0
        
        return result_df
    
    def _calculate_sma_cross(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算SMA20/SMA60死叉
        """
        result_df = df.copy()
        
        # 计算SMA20和SMA60
        result_df['sma20'] = result_df['close'].rolling(window=20).mean()
        result_df['sma60'] = result_df['close'].rolling(window=60).mean()
        
        # 死叉（触发信号B减仓规则）
        result_df['sma_death_cross'] = (
            (result_df['sma20'] < result_df['sma60']) & 
            (result_df['sma20'].shift(1) >= result_df['sma60'].shift(1))
        ).astype(int)
        
        return result_df
    
    def _calculate_atr(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算ATR(14日)用于动态止损
        """
        result_df = df.copy()
        
        # 计算真实波动范围
        result_df['tr'] = np.maximum(
            result_df['high'] - result_df['low'],
            np.maximum(
                abs(result_df['high'] - result_df['close'].shift(1)),
                abs(result_df['low'] - result_df['close'].shift(1))
            )
        )
        
        # 计算ATR(14日)
        result_df['atr14'] = result_df['tr'].rolling(window=14).mean()
        
        return result_df
    
    def _calculate_external_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算需要外部数据的指标（使用模拟数据）
        """
        result_df = df.copy()
        
        # 1. CME降息概率（模拟数据）
        result_df['cme_rate_cut_prob'] = np.random.uniform(0, 100, len(result_df))
        
        # 2. GLD/IAU ETF周度流向（模拟数据）
        result_df['gld_iau_flow'] = np.random.uniform(-100, 100, len(result_df))
        
        # 3. CFTC COT净多仓（模拟数据）
        result_df['cftc_cot_net_long'] = np.random.uniform(0, 100000, len(result_df))
        
        # 4. GPR指数（模拟数据）
        result_df['gpr_index'] = np.random.uniform(0, 100, len(result_df))
        
        # 5. WTI原油价格（模拟数据）
        result_df['wti_price'] = np.random.uniform(80, 120, len(result_df))
        
        return result_df
    
    def _calculate_weight_adjustments(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算权重调整
        """
        result_df = df.copy()
        
        # 初始化权重调整列
        result_df['r_weight_adj'] = 0.0
        result_df['o_weight_adj'] = 0.0
        
        # 1. CME降息概率（突破40% → O因子权重从-5%修正为+8%）
        result_df.loc[result_df['cme_rate_cut_prob'] > 40, 'o_weight_adj'] = 0.13  # 从-5%到+8%，调整13%
        
        # 2. GPR指数（单月回落>20% → R因子权重下调15%）
        gpr_change = result_df['gpr_index'].pct_change(20)  # 约1个月
        result_df.loc[gpr_change < -0.2, 'r_weight_adj'] = -0.15
        
        # 3. WTI原油价格（跌破$100 → 触发R因子减弱警报）
        result_df.loc[result_df['wti_price'] < 100, 'r_weight_adj'] -= 0.1
        
        return result_df
    
    def _generate_trigger_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成触发信号
        """
        result_df = df.copy()
        
        # 初始化信号列
        result_df['buy_signal'] = 0
        result_df['sell_signal'] = 0
        result_df['alert_signal'] = 0
        
        # 1. DXY 5日线下穿20日线 → 触发做多信号
        result_df.loc[result_df['dxy_cross_down'] == 1, 'buy_signal'] = 1
        
        # 2. SMA20/SMA60死叉 → 触发信号B减仓规则
        result_df.loc[result_df['sma_death_cross'] == 1, 'sell_signal'] = 1
        
        # 3. GLD/IAU ETF连续2周净流出 → 触发信号B减仓规则
        gld_iau_flow_weekly = result_df['gld_iau_flow'].resample('W').sum()
        consecutive_outflow = (gld_iau_flow_weekly < 0).rolling(window=2).sum() == 2
        consecutive_outflow_daily = consecutive_outflow.reindex(result_df.index, method='ffill').fillna(False)
        result_df.loc[consecutive_outflow_daily, 'sell_signal'] = 1
        
        # 4. CFTC COT净多仓超历史90百分位 → 反转预警
        cot_90th = result_df['cftc_cot_net_long'].rolling(window=252).quantile(0.9)
        result_df.loc[result_df['cftc_cot_net_long'] > cot_90th, 'alert_signal'] = 1
        
        return result_df
    
    def get_adjusted_weights(self, row: pd.Series) -> Dict[str, float]:
        """
        获取调整后的权重
        
        Args:
            row: 包含权重调整信息的行
            
        Returns:
            Dict[str, float]: 调整后的权重
        """
        adjusted_weights = self.base_weights.copy()
        
        # 应用R因子权重调整
        adjusted_weights['R'] = max(0, adjusted_weights['R'] + row.get('r_weight_adj', 0))
        
        # 应用O因子权重调整
        adjusted_weights['O'] = max(0, adjusted_weights['O'] + row.get('o_weight_adj', 0))
        
        # 重新归一化权重
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for key in adjusted_weights:
                adjusted_weights[key] /= total_weight
        
        return adjusted_weights
    
    def get_trigger_signals(self, df: pd.DataFrame) -> Dict[str, List]:
        """
        获取触发信号
        
        Args:
            df: 包含监控指标的DataFrame
            
        Returns:
            Dict[str, List]: 触发信号字典
        """
        signals = {
            'buy_signals': df[df['buy_signal'] == 1].index.tolist(),
            'sell_signals': df[df['sell_signal'] == 1].index.tolist(),
            'alert_signals': df[df['alert_signal'] == 1].index.tolist()
        }
        
        return signals
    
    def integrate_with_vectorbt(self, df: pd.DataFrame, price_col: str = 'close') -> Dict:
        """
        与VectorBT集成，生成回测信号
        
        Args:
            df: 包含监控指标的DataFrame
            price_col: 价格列名
            
        Returns:
            Dict: 包含VectorBT回测所需的信号
        """
        # 生成VectorBT回测信号
        entries = df['buy_signal'] == 1
        exits = df['sell_signal'] == 1
        
        # 计算动态仓位大小
        position_size = np.ones(len(df))
        
        # 基于ATR设置动态止损
        if 'atr14' in df.columns:
            atr = df['atr14']
        else:
            atr = np.zeros(len(df))
        
        return {
            'entries': entries,
            'exits': exits,
            'position_size': position_size,
            'atr': atr
        }

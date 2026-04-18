#!/usr/bin/env python3
"""
独立测试GRAM四因子模型策略
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime


class GRAMFourFactorStrategy:
    """
    GRAM四因子模型策略
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
        print("GRAM四因子计算完成")
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
    
    def get_factor_weights(self):
        """
        获取因子权重
        """
        return self.base_weights
    
    def get_factor_contribution(self):
        """
        获取因子贡献度
        """
        if self.factor_data is None:
            print("因子数据未计算")
            return pd.DataFrame()
        
        contribution = pd.DataFrame()
        contribution['R_contribution'] = self.base_weights['R'] * self.factor_data['r_factor_norm']
        contribution['O_contribution'] = self.base_weights['O'] * self.factor_data['o_factor_norm']
        contribution['E_contribution'] = self.base_weights['E'] * self.factor_data['e_factor_norm']
        contribution['M_contribution'] = self.base_weights['M'] * self.factor_data['m_factor_norm']
        contribution['total_score'] = self.factor_data['weighted_score']
        
        return contribution


def get_gold_data(start_date='2020-01-01', end_date='2026-04-18'):
    """
    获取黄金和DXY数据
    """
    print(f"获取黄金数据: {start_date} 到 {end_date}")
    
    # 获取黄金期货数据
    gold_data = yf.download('GC=F', start=start_date, end=end_date)
    
    # 获取DXY数据
    dxy_data = yf.download('DX-Y.NYB', start=start_date, end=end_date)
    
    # 合并数据
    data = gold_data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    data.columns = ['open', 'high', 'low', 'close', 'volume']
    data['dxy_close'] = dxy_data['Close']
    
    # 填充缺失值
    data = data.ffill().bfill()
    
    print(f"数据获取完成，共 {len(data)} 条记录")
    return data


def calculate_returns(data, signal):
    """
    计算策略收益率
    """
    returns = data['close'].pct_change()
    strategy_returns = returns * signal.shift(1)  # 信号滞后一天
    return strategy_returns


def main():
    """
    主函数
    """
    try:
        # 获取数据
        data = get_gold_data()
        
        # 初始化GRAM策略
        gram_strategy = GRAMFourFactorStrategy()
        
        # 计算GRAM因子
        factor_data = gram_strategy.calculate_gram_factors(data)
        
        # 验证数据完整性
        if factor_data is None or len(factor_data) == 0:
            print("因子数据计算失败")
            return
        
        # 打印因子权重
        print(f"GRAM因子权重: {gram_strategy.get_factor_weights()}")
        
        # 计算策略收益
        strategy_returns = calculate_returns(factor_data, factor_data['signal'])
        
        # 计算回测指标
        total_return = (1 + strategy_returns).prod() - 1
        annualized_return = (1 + total_return) ** (252 / len(strategy_returns)) - 1
        max_drawdown = (1 - (1 + strategy_returns).cumprod() / (1 + strategy_returns).cumprod().cummax()).max()
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
        
        # 打印回测结果
        print("\n回测结果:")
        print(f"总收益率: {total_return * 100:.2f}%")
        print(f"年化收益率: {annualized_return * 100:.2f}%")
        print(f"最大回撤: {max_drawdown * 100:.2f}%")
        print(f"夏普比率: {sharpe_ratio:.2f}")
        
        # 分析近12个月不同象限下的因子收益归因
        print("\n近12个月因子收益归因分析:")
        
        # 筛选近12个月数据
        recent_data = factor_data.tail(252)  # 约12个月的交易日
        
        # 计算不同象限的收益
        quadrants = {
            'R+O+': (recent_data['r_factor_norm'] > 0) & (recent_data['o_factor_norm'] > 0),
            'R+O-': (recent_data['r_factor_norm'] > 0) & (recent_data['o_factor_norm'] <= 0),
            'R-O+': (recent_data['r_factor_norm'] <= 0) & (recent_data['o_factor_norm'] > 0),
            'R-O-': (recent_data['r_factor_norm'] <= 0) & (recent_data['o_factor_norm'] <= 0)
        }
        
        for quadrant, mask in quadrants.items():
            if mask.any():
                quadrant_returns = recent_data.loc[mask, 'close'].pct_change().dropna()
                avg_return = quadrant_returns.mean() * 252 * 100  # 年化收益率
                print(f"象限 {quadrant}: 平均年化收益率 = {avg_return:.2f}%")
        
        # 因子贡献度分析
        print("\n因子贡献度分析:")
        contribution = gram_strategy.get_factor_contribution()
        if not contribution.empty:
            recent_contribution = contribution.tail(252)
            for factor in ['R_contribution', 'O_contribution', 'E_contribution', 'M_contribution']:
                avg_contribution = recent_contribution[factor].mean()
                print(f"{factor}: 平均贡献 = {avg_contribution:.4f}")
        
        # 验证GRAM净驱动合计的年化解释力
        print("\n验证GRAM净驱动合计的年化解释力:")
        
        # 计算策略收益与因子得分的相关性
        factor_scores = factor_data['weighted_score']
        correlation = strategy_returns.corr(factor_scores.shift(1))  # 信号滞后一天
        
        print(f"策略收益与因子得分的相关性: {correlation:.4f}")
        
        # 计算年化解释力（R²）
        r_squared = correlation ** 2
        print(f"年化解释力 (R²): {r_squared * 100:.2f}%")
        
        # 绘制回测结果
        print("\n生成回测分析图表...")
        
        # 绘制净值曲线
        plt.figure(figsize=(12, 6))
        plt.plot((1 + strategy_returns).cumprod(), label='策略净值')
        plt.plot((1 + data['close'].pct_change()).cumprod(), label='基准净值')
        plt.title('GRAM四因子模型回测结果')
        plt.xlabel('日期')
        plt.ylabel('净值')
        plt.legend()
        plt.savefig('gram_strategy_backtest.png')
        print("回测图表已保存为 gram_strategy_backtest.png")
        
        # 保存因子数据
        factor_data.to_csv('gram_factor_data.csv')
        print("因子数据已保存为 gram_factor_data.csv")
        
        print("\nGRAM四因子模型测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

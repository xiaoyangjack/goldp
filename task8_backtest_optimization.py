#!/usr/bin/env python3
"""
Task 8: 回测与参数调优
基于VectorBT完成回测验证和参数调优
"""

import pandas as pd
import numpy as np
import yfinance as yf
import vectorbt as vbt
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class GRAMFourFactorStrategy:
    """
    GRAM四因子模型策略
    """
    
    def __init__(self, weights=None):
        """初始化GRAM四因子策略"""
        if weights is None:
            self.base_weights = {
                'R': 0.40,  # 提升至40%
                'O': 0.25,
                'E': 0.20,
                'M': 0.15
            }
        else:
            self.base_weights = weights
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
    
    def _generate_signals(self, df: pd.DataFrame, batch_buy_range=None) -> pd.DataFrame:
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
                # 检查是否在分批建仓区间
                if batch_buy_range and batch_buy_range[0] <= row['close'] <= batch_buy_range[1]:
                    return 0.5  # 半仓观望/分批建仓
                else:
                    return 0  # 观望
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
            return pd.DataFrame()
        
        contribution = pd.DataFrame()
        contribution['R_contribution'] = self.base_weights['R'] * self.factor_data['r_factor_norm']
        contribution['O_contribution'] = self.base_weights['O'] * self.factor_data['o_factor_norm']
        contribution['E_contribution'] = self.base_weights['E'] * self.factor_data['e_factor_norm']
        contribution['M_contribution'] = self.base_weights['M'] * self.factor_data['m_factor_norm']
        contribution['total_score'] = self.factor_data['weighted_score']
        
        return contribution


def get_gold_data(start_date, end_date):
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


def backtest_with_vectorbt(data, signals, atr_multiplier=1.5, fees=0.001, slippage=0.0005):
    """
    使用VectorBT进行回测
    """
    # 计算ATR
    high = data['high']
    low = data['low']
    close = data['close']
    atr = vbt.ATR.run(high, low, close, window=14).atr
    
    # 准备回测信号
    entries = signals == 1
    exits = signals == -1
    short_entries = signals == -1
    short_exits = signals == 1
    
    # 创建VectorBT回测
    portfolio = vbt.Portfolio.from_signals(
        close,
        entries=entries,
        exits=exits,
        short_entries=short_entries,
        short_exits=short_exits,
        size=np.where(signals == 0.5, 0.5, 1.0),  # 半仓观望/分批建仓
        freq='B',
        fees=fees,
        slippage=slippage,
        sl_stop=atr_multiplier * atr,  # ATR止损
        sl_trail=True  # 移动止损
    )
    
    return portfolio


def grid_optimization(data, param_grid):
    """
    网格调优
    """
    results = []
    
    for atr_multiplier in param_grid['atr_multiplier']:
        for batch_buy_min in param_grid['batch_buy_range_min']:
            for batch_buy_max in param_grid['batch_buy_range_max']:
                if batch_buy_min >= batch_buy_max:
                    continue
                
                # 初始化GRAM策略
                gram_strategy = GRAMFourFactorStrategy()
                
                # 计算因子和信号
                batch_buy_range = (batch_buy_min, batch_buy_max)
                factor_data = gram_strategy.calculate_gram_factors(data)
                signals = gram_strategy._generate_signals(factor_data, batch_buy_range)
                
                # 回测
                portfolio = backtest_with_vectorbt(data, signals['signal'], atr_multiplier)
                
                # 记录结果
                result = {
                    'atr_multiplier': atr_multiplier,
                    'batch_buy_min': batch_buy_min,
                    'batch_buy_max': batch_buy_max,
                    'total_return': portfolio.total_return(),
                    'annualized_return': portfolio.annualized_return(),
                    'max_drawdown': portfolio.max_drawdown(),
                    'sharpe_ratio': portfolio.sharpe_ratio(),
                    'win_rate': portfolio.win_rate(),
                    'profit_factor': portfolio.profit_factor(),
                    'total_trades': portfolio.total_trades(),
                    'avg_win_loss_ratio': portfolio.avg_win_loss_ratio()
                }
                results.append(result)
                
                print(f"参数组合: ATR={atr_multiplier}, 建仓区间={batch_buy_min}-{batch_buy_max}")
                print(f"  总收益率: {result['total_return'] * 100:.2f}%")
                print(f"  年化收益率: {result['annualized_return'] * 100:.2f}%")
                print(f"  最大回撤: {result['max_drawdown'] * 100:.2f}%")
                print(f"  夏普比率: {result['sharpe_ratio']:.2f}")
                print(f"  胜率: {result['win_rate'] * 100:.2f}%")
                print(f"  盈亏比: {result['avg_win_loss_ratio']:.2f}")
    
    return pd.DataFrame(results)


def compare_weight_adjustment(data):
    """
    比较权重调整前后的性能
    """
    # 原始权重
    original_weights = {'R': 0.25, 'O': 0.25, 'E': 0.25, 'M': 0.25}
    # 新权重
    new_weights = {'R': 0.40, 'O': 0.25, 'E': 0.20, 'M': 0.15}
    
    # 使用原始权重回测
    original_strategy = GRAMFourFactorStrategy(original_weights)
    original_factor_data = original_strategy.calculate_gram_factors(data)
    original_portfolio = backtest_with_vectorbt(data, original_factor_data['signal'])
    
    # 使用新权重回测
    new_strategy = GRAMFourFactorStrategy(new_weights)
    new_factor_data = new_strategy.calculate_gram_factors(data)
    new_portfolio = backtest_with_vectorbt(data, new_factor_data['signal'])
    
    # 打印对比结果
    print("\n权重调整前后对比:")
    print("原始权重 (各25%):")
    print(f"  总收益率: {original_portfolio.total_return() * 100:.2f}%")
    print(f"  年化收益率: {original_portfolio.annualized_return() * 100:.2f}%")
    print(f"  最大回撤: {original_portfolio.max_drawdown() * 100:.2f}%")
    print(f"  夏普比率: {original_portfolio.sharpe_ratio():.2f}")
    print(f"  胜率: {original_portfolio.win_rate() * 100:.2f}%")
    print(f"  盈亏比: {original_portfolio.avg_win_loss_ratio():.2f}")
    
    print("\n新权重 (R:40%, O:25%, E:20%, M:15%):")
    print(f"  总收益率: {new_portfolio.total_return() * 100:.2f}%")
    print(f"  年化收益率: {new_portfolio.annualized_return() * 100:.2f}%")
    print(f"  最大回撤: {new_portfolio.max_drawdown() * 100:.2f}%")
    print(f"  夏普比率: {new_portfolio.sharpe_ratio():.2f}")
    print(f"  胜率: {new_portfolio.win_rate() * 100:.2f}%")
    print(f"  盈亏比: {new_portfolio.avg_win_loss_ratio():.2f}")


def analyze_event_signals(data, signals):
    """
    分析事件信号触发的胜率/盈亏比
    """
    # 计算ATR
    high = data['high']
    low = data['low']
    close = data['close']
    atr = vbt.ATR.run(high, low, close, window=14).atr
    
    # 准备回测信号
    entries = signals == 1
    exits = signals == -1
    short_entries = signals == -1
    short_exits = signals == 1
    
    # 创建VectorBT回测
    portfolio = vbt.Portfolio.from_signals(
        close,
        entries=entries,
        exits=exits,
        short_entries=short_entries,
        short_exits=short_exits,
        size=np.where(signals == 0.5, 0.5, 1.0),
        freq='B',
        fees=0.001,
        slippage=0.0005,
        sl_stop=1.5 * atr,
        sl_trail=True
    )
    
    # 分析交易
    trades = portfolio.trades
    if not trades.empty:
        print("\n事件信号触发分析:")
        print(f"总交易次数: {len(trades)}")
        print(f"盈利交易次数: {len(trades[trades['return'] > 0])}")
        print(f"亏损交易次数: {len(trades[trades['return'] < 0])}")
        print(f"胜率: {portfolio.win_rate() * 100:.2f}%")
        print(f"盈亏比: {portfolio.avg_win_loss_ratio():.2f}")
        print(f"平均盈利: {trades[trades['return'] > 0]['return'].mean() * 100:.2f}%")
        print(f"平均亏损: {trades[trades['return'] < 0]['return'].mean() * 100:.2f}%")


def main():
    """
    主函数
    """
    try:
        # 计算近12个月的日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # 获取数据
        data = get_gold_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        # 1. 比较权重调整前后的性能
        compare_weight_adjustment(data)
        
        # 2. 分析事件信号触发的胜率/盈亏比
        gram_strategy = GRAMFourFactorStrategy()
        factor_data = gram_strategy.calculate_gram_factors(data)
        analyze_event_signals(data, factor_data['signal'])
        
        # 3. 网格调优
        print("\n开始网格调优...")
        param_grid = {
            'atr_multiplier': [1.0, 1.2, 1.5, 1.8, 2.0],
            'batch_buy_range_min': [4600, 4650, 4700],
            'batch_buy_range_max': [4720, 4750, 4800]
        }
        
        optimization_results = grid_optimization(data, param_grid)
        
        # 4. 找出最优参数组合
        print("\n最优参数组合:")
        # 综合考虑夏普比率和最大回撤
        optimization_results['score'] = optimization_results['sharpe_ratio'] - optimization_results['max_drawdown']
        best_params = optimization_results.sort_values('score', ascending=False).iloc[0]
        
        print(f"ATR止损系数: {best_params['atr_multiplier']}")
        print(f"分批建仓区间: ${best_params['batch_buy_min']} - ${best_params['batch_buy_max']}")
        print(f"总收益率: {best_params['total_return'] * 100:.2f}%")
        print(f"年化收益率: {best_params['annualized_return'] * 100:.2f}%")
        print(f"最大回撤: {best_params['max_drawdown'] * 100:.2f}%")
        print(f"夏普比率: {best_params['sharpe_ratio']:.2f}")
        print(f"胜率: {best_params['win_rate'] * 100:.2f}%")
        print(f"盈亏比: {best_params['avg_win_loss_ratio']:.2f}")
        
        # 5. 验证最优参数组合
        print("\n验证最优参数组合...")
        best_gram_strategy = GRAMFourFactorStrategy()
        best_factor_data = best_gram_strategy.calculate_gram_factors(data)
        best_signals = best_gram_strategy._generate_signals(
            best_factor_data, 
            (best_params['batch_buy_min'], best_params['batch_buy_max'])
        )
        best_portfolio = backtest_with_vectorbt(
            data, 
            best_signals['signal'], 
            best_params['atr_multiplier']
        )
        
        print("\n验证结果:")
        print(f"总收益率: {best_portfolio.total_return() * 100:.2f}%")
        print(f"年化收益率: {best_portfolio.annualized_return() * 100:.2f}%")
        print(f"最大回撤: {best_portfolio.max_drawdown() * 100:.2f}%")
        print(f"夏普比率: {best_portfolio.sharpe_ratio():.2f}")
        print(f"胜率: {best_portfolio.win_rate() * 100:.2f}%")
        print(f"盈亏比: {best_portfolio.avg_win_loss_ratio():.2f}")
        
        # 6. 保存结果
        optimization_results.to_csv('grid_optimization_results.csv', index=False)
        print("\n网格调优结果已保存为 grid_optimization_results.csv")
        
        # 7. 绘制回测结果
        print("\n生成回测分析图表...")
        
        # 绘制净值曲线
        plt.figure(figsize=(12, 6))
        plt.plot((1 + best_portfolio.returns()).cumprod(), label='策略净值')
        plt.plot((1 + data['close'].pct_change()).cumprod(), label='基准净值')
        plt.title('GRAM四因子模型回测结果 (最优参数)')
        plt.xlabel('日期')
        plt.ylabel('净值')
        plt.legend()
        plt.savefig('gram_strategy_backtest_optimal.png')
        print("回测图表已保存为 gram_strategy_backtest_optimal.png")
        
        print("\nTask 8: 回测与参数调优完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

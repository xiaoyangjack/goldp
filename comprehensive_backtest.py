#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合回测框架
集成主流回测方法和因子，使用真实数据
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

# 配置日志
log_file = os.getenv('LOG_FILE', 'logs/comprehensive_backtest.log')
os.makedirs('logs', exist_ok=True)
logger.add(
    log_file,
    rotation=os.getenv('LOG_ROTATION', '10 MB'),
    retention=os.getenv('LOG_RETENTION', '7 days'),
    level=os.getenv('LOG_LEVEL', 'INFO')
)

class ComprehensiveBacktest:
    """综合回测框架"""
    
    def __init__(self):
        self.data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
        self.factor_path = os.getenv('FACTOR_PATH', 'data/macro_factors_merged.csv')
        self.results_path = os.getenv('RESULTS_PATH', 'backtest/comprehensive_results')
        os.makedirs(self.results_path, exist_ok=True)
    
    def load_data(self):
        """加载数据"""
        try:
            # 加载黄金数据
            gold_df = pd.read_csv(self.data_path)
            gold_df['date'] = pd.to_datetime(gold_df['date'])
            gold_df = gold_df.sort_values('date')
            
            # 加载因子数据
            if os.path.exists(self.factor_path):
                factor_df = pd.read_csv(self.factor_path)
                factor_df['date'] = pd.to_datetime(factor_df['date'])
                # 合并数据
                df = gold_df.merge(factor_df, on='date', how='left')
            else:
                df = gold_df
            
            logger.info(f"数据加载成功，共 {len(df)} 条")
            return df
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            raise
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        # 移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA40'] = df['close'].rolling(window=40).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 波动率
        df['Volatility'] = df['close'].rolling(window=20).std()
        
        # 计算收益率
        df['Return'] = df['close'].pct_change()
        
        return df
    
    def run_ma_strategy(self, df, fast_window=20, slow_window=40):
        """运行MA策略"""
        df['Position'] = 0
        df.loc[df['MA' + str(fast_window)] > df['MA' + str(slow_window)], 'Position'] = 1
        df.loc[df['MA' + str(fast_window)] < df['MA' + str(slow_window)], 'Position'] = -1
        
        # 计算策略收益率
        df['Strategy_Return'] = df['Position'].shift(1) * df['Return']
        df['Cumulative_Return'] = (1 + df['Strategy_Return']).cumprod()
        
        # 计算回测指标
        total_return = (df['Cumulative_Return'].iloc[-1] - 1) * 100
        annual_return = ((1 + total_return/100) ** (252/len(df)) - 1) * 100
        sharpe_ratio = np.sqrt(252) * df['Strategy_Return'].mean() / df['Strategy_Return'].std()
        max_drawdown = ((df['Cumulative_Return'] / df['Cumulative_Return'].cummax()) - 1).min() * 100
        win_rate = (df['Strategy_Return'] > 0).sum() / len(df['Strategy_Return'].dropna()) * 100
        
        return {
            'strategy': 'MA',
            'parameters': {'fast_window': fast_window, 'slow_window': slow_window},
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'data': df
        }
    
    def run_macd_strategy(self, df):
        """运行MACD策略"""
        df['Position'] = 0
        df.loc[df['MACD'] > df['Signal'], 'Position'] = 1
        df.loc[df['MACD'] < df['Signal'], 'Position'] = -1
        
        # 计算策略收益率
        df['Strategy_Return'] = df['Position'].shift(1) * df['Return']
        df['Cumulative_Return'] = (1 + df['Strategy_Return']).cumprod()
        
        # 计算回测指标
        total_return = (df['Cumulative_Return'].iloc[-1] - 1) * 100
        annual_return = ((1 + total_return/100) ** (252/len(df)) - 1) * 100
        sharpe_ratio = np.sqrt(252) * df['Strategy_Return'].mean() / df['Strategy_Return'].std()
        max_drawdown = ((df['Cumulative_Return'] / df['Cumulative_Return'].cummax()) - 1).min() * 100
        win_rate = (df['Strategy_Return'] > 0).sum() / len(df['Strategy_Return'].dropna()) * 100
        
        return {
            'strategy': 'MACD',
            'parameters': {},
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'data': df
        }
    
    def run_rsi_strategy(self, df, overbought=70, oversold=30):
        """运行RSI策略"""
        df['Position'] = 0
        df.loc[df['RSI'] < oversold, 'Position'] = 1
        df.loc[df['RSI'] > overbought, 'Position'] = -1
        
        # 计算策略收益率
        df['Strategy_Return'] = df['Position'].shift(1) * df['Return']
        df['Cumulative_Return'] = (1 + df['Strategy_Return']).cumprod()
        
        # 计算回测指标
        total_return = (df['Cumulative_Return'].iloc[-1] - 1) * 100
        annual_return = ((1 + total_return/100) ** (252/len(df)) - 1) * 100
        sharpe_ratio = np.sqrt(252) * df['Strategy_Return'].mean() / df['Strategy_Return'].std()
        max_drawdown = ((df['Cumulative_Return'] / df['Cumulative_Return'].cummax()) - 1).min() * 100
        win_rate = (df['Strategy_Return'] > 0).sum() / len(df['Strategy_Return'].dropna()) * 100
        
        return {
            'strategy': 'RSI',
            'parameters': {'overbought': overbought, 'oversold': oversold},
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'data': df
        }
    
    def run_factor_strategy(self, df):
        """运行因子策略"""
        if 'ag99_close' not in df.columns:
            logger.warning("白银价格因子不可用，跳过因子策略")
            return None
        
        # 基于白银价格与黄金价格的相关性
        df['Position'] = 0
        # 当白银价格上涨超过2%时，买入黄金
        df.loc[df['ag99_close'].pct_change() > 0.02, 'Position'] = 1
        # 当白银价格下跌超过2%时，卖出黄金
        df.loc[df['ag99_close'].pct_change() < -0.02, 'Position'] = -1
        
        # 计算策略收益率
        df['Strategy_Return'] = df['Position'].shift(1) * df['Return']
        df['Cumulative_Return'] = (1 + df['Strategy_Return']).cumprod()
        
        # 计算回测指标
        total_return = (df['Cumulative_Return'].iloc[-1] - 1) * 100
        annual_return = ((1 + total_return/100) ** (252/len(df)) - 1) * 100
        sharpe_ratio = np.sqrt(252) * df['Strategy_Return'].mean() / df['Strategy_Return'].std()
        max_drawdown = ((df['Cumulative_Return'] / df['Cumulative_Return'].cummax()) - 1).min() * 100
        win_rate = (df['Strategy_Return'] > 0).sum() / len(df['Strategy_Return'].dropna()) * 100
        
        return {
            'strategy': 'Factor',
            'parameters': {'factor': 'ag99_close'}, 
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'data': df
        }
    
    def run_all_strategies(self):
        """运行所有策略"""
        try:
            # 加载数据
            df = self.load_data()
            
            # 计算指标
            df = self.calculate_indicators(df)
            
            # 运行各种策略
            strategies = []
            
            # MA策略
            ma_result = self.run_ma_strategy(df)
            strategies.append(ma_result)
            
            # MACD策略
            macd_result = self.run_macd_strategy(df)
            strategies.append(macd_result)
            
            # RSI策略
            rsi_result = self.run_rsi_strategy(df)
            strategies.append(rsi_result)
            
            # 因子策略
            factor_result = self.run_factor_strategy(df)
            if factor_result:
                strategies.append(factor_result)
            
            # 保存结果
            self.save_results(strategies)
            
            # 分析结果
            self.analyze_results(strategies)
            
            return strategies
        except Exception as e:
            logger.error(f"运行回测失败: {e}")
            raise
    
    def save_results(self, strategies):
        """保存回测结果"""
        for result in strategies:
            # 保存策略数据
            data_path = os.path.join(self.results_path, f"{result['strategy']}_strategy_data.csv")
            result['data'].to_csv(data_path, index=False)
            
            # 保存策略指标
            metrics_path = os.path.join(self.results_path, f"{result['strategy']}_metrics.json")
            import json
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'strategy': result['strategy'],
                    'parameters': result['parameters'],
                    'total_return': result['total_return'],
                    'annual_return': result['annual_return'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'max_drawdown': result['max_drawdown'],
                    'win_rate': result['win_rate']
                }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"回测结果保存到: {self.results_path}")
    
    def analyze_results(self, strategies):
        """分析回测结果"""
        logger.info("=== 回测结果分析 ===")
        
        for result in strategies:
            logger.info(f"\n策略: {result['strategy']}")
            logger.info(f"参数: {result['parameters']}")
            logger.info(f"总收益率: {result['total_return']:.2f}%")
            logger.info(f"年化收益率: {result['annual_return']:.2f}%")
            logger.info(f"夏普比率: {result['sharpe_ratio']:.2f}")
            logger.info(f"最大回撤: {result['max_drawdown']:.2f}%")
            logger.info(f"胜率: {result['win_rate']:.2f}%")
        
        # 找出最佳策略
        best_strategy = max(strategies, key=lambda x: x['sharpe_ratio'])
        logger.info(f"\n=== 最佳策略 ===")
        logger.info(f"策略: {best_strategy['strategy']}")
        logger.info(f"夏普比率: {best_strategy['sharpe_ratio']:.2f}")
        logger.info(f"总收益率: {best_strategy['total_return']:.2f}%")
        logger.info(f"最大回撤: {best_strategy['max_drawdown']:.2f}%")
    
    def real_time_monitoring(self):
        """实时监测"""
        try:
            # 加载最新数据
            df = self.load_data()
            latest_data = df.iloc[-1]
            
            logger.info("=== 实时监测 ===")
            logger.info(f"最新日期: {latest_data['date']}")
            logger.info(f"最新价格: {latest_data['close']:.2f}")
            
            # 计算技术指标
            df = self.calculate_indicators(df)
            latest_indicators = df.iloc[-1]
            
            logger.info(f"MA5: {latest_indicators['MA5']:.2f}")
            logger.info(f"MA20: {latest_indicators['MA20']:.2f}")
            logger.info(f"MACD: {latest_indicators['MACD']:.4f}")
            logger.info(f"Signal: {latest_indicators['Signal']:.4f}")
            logger.info(f"RSI: {latest_indicators['RSI']:.2f}")
            
            # 生成交易信号
            signals = {}
            
            # MA信号
            if latest_indicators['MA5'] > latest_indicators['MA20']:
                signals['MA'] = '买入'
            else:
                signals['MA'] = '卖出'
            
            # MACD信号
            if latest_indicators['MACD'] > latest_indicators['Signal']:
                signals['MACD'] = '买入'
            else:
                signals['MACD'] = '卖出'
            
            # RSI信号
            if latest_indicators['RSI'] < 30:
                signals['RSI'] = '买入'
            elif latest_indicators['RSI'] > 70:
                signals['RSI'] = '卖出'
            else:
                signals['RSI'] = '中性'
            
            logger.info(f"交易信号: {signals}")
            
            return {
                'price': latest_data['close'],
                'date': latest_data['date'],
                'indicators': {
                    'MA5': latest_indicators['MA5'],
                    'MA20': latest_indicators['MA20'],
                    'MACD': latest_indicators['MACD'],
                    'Signal': latest_indicators['Signal'],
                    'RSI': latest_indicators['RSI']
                },
                'signals': signals
            }
        except Exception as e:
            logger.error(f"实时监测失败: {e}")
            raise

if __name__ == "__main__":
    backtest = ComprehensiveBacktest()
    
    # 运行回测
    logger.info("=== 开始综合回测 ===")
    results = backtest.run_all_strategies()
    
    # 实时监测
    logger.info("\n=== 开始实时监测 ===")
    monitoring = backtest.real_time_monitoring()
    
    logger.info("=== 回测完成 ===")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时回测与监控系统
支持：
1. 实时金价监控
2. 多策略实时回测
3. 策略切换
4. 缓存管理
5. 实时新闻监控
"""
import os
import time
import json
import threading
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

# 配置日志
os.makedirs('logs', exist_ok=True)
logger.add('logs/real_time_system.log', rotation='10 MB', retention='7 days')

class RealTimeBacktestSystem:
    """实时回测系统"""
    
    def __init__(self):
        self.data_dir = 'data'
        self.results_dir = 'backtest/real_time_results'
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.current_strategy = 'MA'  # 默认策略
        self.strategies = ['MA', 'MACD', 'RSI', 'Factor']
        self.monitoring = False
        self.monitor_thread = None
        
        # 策略配置
        self.strategy_configs = {
            'MA': {'fast_window': 5, 'slow_window': 20},
            'MACD': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
            'RSI': {'period': 14, 'overbought': 70, 'oversold': 30},
            'Factor': {'lookback': 5}
        }
        
        # 缓存状态
        self.cache_status = {}
        self.last_update = {}
    
    def load_gold_data(self, force_refresh=False):
        """加载黄金数据（带缓存）"""
        filepath = os.path.join(self.data_dir, 'gold_au9999_verified.csv')
        
        # 检查缓存
        if not force_refresh and os.path.exists(filepath):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            age = (datetime.now() - mtime).total_seconds() / 60
            
            if age < 60:  # 1小时内的缓存
                logger.info(f"使用缓存数据（{age:.1f}分钟前）")
                df = pd.read_csv(filepath)
                df['date'] = pd.to_datetime(df['date'])
                self.cache_status['gold_data'] = 'cached'
                self.last_update['gold_data'] = mtime.isoformat()
                return df
        
        # 尝试刷新数据
        try:
            import akshare as ak
            df = ak.spot_hist_sge(symbol="Au99.99")
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            logger.info(f"数据已刷新，最新日期: {df['date'].max()}")
            self.cache_status['gold_data'] = 'refreshed'
            self.last_update['gold_data'] = datetime.now().isoformat()
            return df
        except Exception as e:
            logger.warning(f"刷新数据失败，使用缓存: {e}")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df['date'] = pd.to_datetime(df['date'])
                self.cache_status['gold_data'] = 'fallback'
                return df
            raise
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        df = df.copy()
        
        # MA
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA40'] = df['close'].rolling(window=40).mean()
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Histogram'] = df['MACD'] - df['Signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 收益率
        df['Return'] = df['close'].pct_change()
        
        return df
    
    def generate_signals(self, df, strategy_name):
        """生成交易信号"""
        df = df.copy()
        df['Position'] = 0
        df['Signal'] = 'neutral'
        
        if strategy_name == 'MA':
            config = self.strategy_configs['MA']
            fast_col = f"MA{config['fast_window']}"
            slow_col = f"MA{config['slow_window']}"
            
            df.loc[df[fast_col] > df[slow_col], 'Position'] = 1
            df.loc[df[fast_col] < df[slow_col], 'Position'] = -1
            
        elif strategy_name == 'MACD':
            df.loc[df['MACD'] > df['Signal'], 'Position'] = 1
            df.loc[df['MACD'] < df['Signal'], 'Position'] = -1
            
        elif strategy_name == 'RSI':
            config = self.strategy_configs['RSI']
            df.loc[df['RSI'] < config['oversold'], 'Position'] = 1
            df.loc[df['RSI'] > config['overbought'], 'Position'] = -1
            
        elif strategy_name == 'Factor':
            try:
                factors_df = self.load_factors()
                if 'ag99_close' in factors_df.columns:
                    df = df.merge(factors_df[['date', 'ag99_close']], on='date', how='left')
                    df['ag_return'] = df['ag99_close'].pct_change()
                    df.loc[df['ag_return'] > 0.01, 'Position'] = 1
                    df.loc[df['ag_return'] < -0.01, 'Position'] = -1
            except Exception as e:
                logger.warning(f"因子策略失败: {e}")
        
        # 转换为信号文本
        df.loc[df['Position'] == 1, 'Signal'] = 'buy'
        df.loc[df['Position'] == -1, 'Signal'] = 'sell'
        
        return df
    
    def load_factors(self):
        """加载因子数据"""
        filepath = os.path.join(self.data_dir, 'macro_factors_merged.csv')
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            return df
        return pd.DataFrame()
    
    def backtest_strategy(self, df, strategy_name):
        """回测策略"""
        df = self.generate_signals(df, strategy_name)
        
        # 计算策略收益
        df['Strategy_Return'] = df['Position'].shift(1) * df['Return']
        df['Cumulative_Return'] = (1 + df['Strategy_Return']).cumprod()
        df['Benchmark_Return'] = (1 + df['Return']).cumprod()
        
        # 计算绩效指标
        if len(df) > 100:
            total_return = (df['Cumulative_Return'].iloc[-1] - 1) * 100
            annual_return = ((1 + total_return/100) ** (252/len(df)) - 1) * 100
            
            strategy_returns = df['Strategy_Return'].dropna()
            if len(strategy_returns) > 0 and strategy_returns.std() > 0:
                sharpe_ratio = np.sqrt(252) * strategy_returns.mean() / strategy_returns.std()
            else:
                sharpe_ratio = 0
            
            max_drawdown = ((df['Cumulative_Return'] / df['Cumulative_Return'].cummax()) - 1).min() * 100
            win_rate = (strategy_returns > 0).sum() / len(strategy_returns) * 100 if len(strategy_returns) > 0 else 0
        else:
            total_return = annual_return = sharpe_ratio = max_drawdown = win_rate = 0
        
        return {
            'strategy': strategy_name,
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'data': df
        }
    
    def switch_strategy(self, strategy_name):
        """切换策略"""
        if strategy_name in self.strategies:
            self.current_strategy = strategy_name
            logger.info(f"策略已切换为: {strategy_name}")
            return True
        else:
            logger.warning(f"无效的策略: {strategy_name}")
            return False
    
    def get_current_market_status(self):
        """获取当前市场状态"""
        try:
            df = self.load_gold_data(force_refresh=False)
            df = self.calculate_indicators(df)
            latest = df.iloc[-1]
            
            # 获取所有策略的信号
            signals = {}
            for strategy in self.strategies:
                try:
                    df_with_signals = self.generate_signals(df.tail(100), strategy)
                    signals[strategy] = df_with_signals.iloc[-1]['Signal']
                except:
                    signals[strategy] = 'error'
            
            return {
                'timestamp': datetime.now().isoformat(),
                'price': float(latest['close']),
                'date': latest['date'].isoformat(),
                'indicators': {
                    'MA5': float(latest['MA5']) if pd.notna(latest['MA5']) else None,
                    'MA20': float(latest['MA20']) if pd.notna(latest['MA20']) else None,
                    'MACD': float(latest['MACD']) if pd.notna(latest['MACD']) else None,
                    'RSI': float(latest['RSI']) if pd.notna(latest['RSI']) else None
                },
                'signals': signals,
                'current_strategy': self.current_strategy,
                'cache_status': self.cache_status,
                'last_update': self.last_update
            }
        except Exception as e:
            logger.error(f"获取市场状态失败: {e}")
            return {'error': str(e)}
    
    def run_full_backtest(self):
        """运行完整回测"""
        logger.info("开始完整回测...")
        
        df = self.load_gold_data(force_refresh=False)
        df = self.calculate_indicators(df)
        
        results = {}
        for strategy in self.strategies:
            try:
                result = self.backtest_strategy(df, strategy)
                results[strategy] = {k: v for k, v in result.items() if k != 'data'}
                
                # 保存详细数据
                result['data'].to_csv(
                    os.path.join(self.results_dir, f"{strategy}_backtest.csv"),
                    index=False
                )
            except Exception as e:
                logger.error(f"策略 {strategy} 回测失败: {e}")
                results[strategy] = {'error': str(e)}
        
        # 保存结果摘要
        with open(os.path.join(self.results_dir, 'backtest_summary.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info("完整回测完成")
        return results
    
    def start_monitoring(self, interval=300):
        """启动监控"""
        if self.monitoring:
            logger.warning("监控已在运行中")
            return False
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    status = self.get_current_market_status()
                    logger.info(f"监控更新: {json.dumps(status, ensure_ascii=False)}")
                    
                    # 保存监控记录
                    monitor_file = os.path.join(self.results_dir, 'monitor_log.jsonl')
                    with open(monitor_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(status, ensure_ascii=False) + '\n')
                    
                except Exception as e:
                    logger.error(f"监控循环错误: {e}")
                
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"监控已启动，间隔 {interval} 秒")
        return True
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("监控已停止")
        return True


# 全局实例
rt_system = RealTimeBacktestSystem()

if __name__ == "__main__":
    import sys
    
    print("=== 实时回测与监控系统 ===")
    print()
    
    system = RealTimeBacktestSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'status':
            print("获取当前市场状态...")
            status = system.get_current_market_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
        
        elif command == 'backtest':
            print("运行完整回测...")
            results = system.run_full_backtest()
            print("\n回测结果:")
            for strategy, result in results.items():
                print(f"\n{strategy}:")
                if 'error' not in result:
                    print(f"  总收益率: {result['total_return']:.2f}%")
                    print(f"  夏普比率: {result['sharpe_ratio']:.2f}")
                    print(f"  最大回撤: {result['max_drawdown']:.2f}%")
        
        elif command == 'switch':
            if len(sys.argv) > 2:
                strategy = sys.argv[2]
                if system.switch_strategy(strategy):
                    print(f"策略已切换为: {strategy}")
        
        elif command == 'monitor':
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            print(f"启动监控（间隔 {interval} 秒）...")
            system.start_monitoring(interval)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n停止监控...")
                system.stop_monitoring()
    
    else:
        print("使用方法:")
        print("  python real_time_backtest_system.py status     - 获取当前状态")
        print("  python real_time_backtest_system.py backtest   - 运行完整回测")
        print("  python real_time_backtest_system.py switch <策略名> - 切换策略")
        print("  python real_time_backtest_system.py monitor [秒] - 启动监控")
        print()
        print("可用策略:", system.strategies)
        print("\n获取当前状态示例:")
        status = system.get_current_market_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

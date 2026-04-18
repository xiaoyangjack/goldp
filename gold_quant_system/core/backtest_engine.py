import pandas as pd
import numpy as np
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed


class BacktestEngine:
    """
    策略回测器 - 执行策略回测并生成结果
    
    支持以下5种策略：
    1. SMA双均线
    2. RSI均值回归
    3. MACD动量
    4. 布林带突破
    5. 多因子合成
    
    通用风控：
    - 动态止损：入场价 - atr_multiplier × ATR
    - 波动率仓位缩放
    - 手续费计算
    """
    
    def __init__(self, initial_cash=100000, commission=0.0002):
        """
        初始化回测引擎
        
        Args:
            initial_cash: 初始资金
            commission: 手续费率
        """
        self.initial_cash = initial_cash
        self.commission = commission
    
    def run_all_strategies(self, df, params=None):
        """
        运行所有策略回测
        
        Args:
            df: 包含因子的数据
            params: 策略参数
        
        Returns:
            dict: 各策略回测结果
        """
        if params is None:
            params = self._get_default_params()
        
        results = {}
        strategies = params.get('strategies', ['sma', 'rsi', 'macd', 'bb', 'multi', 'regime'])
        
        # 定义策略映射
        strategy_map = {
            'sma': self._run_sma_strategy,
            'rsi': self._run_rsi_strategy,
            'macd': self._run_macd_strategy,
            'bb': self._run_bb_strategy,
            'multi': self._run_multi_factor_strategy,
            'regime': self._run_regime_strategy
        }
        
        # 使用线程池并行执行策略
        with ThreadPoolExecutor(max_workers=min(6, len(strategies))) as executor:
            # 提交任务
            future_to_strategy = {}
            for strategy in strategies:
                if strategy in strategy_map:
                    future = executor.submit(strategy_map[strategy], df, params)
                    future_to_strategy[future] = strategy
            
            # 收集结果
            for future in as_completed(future_to_strategy):
                strategy = future_to_strategy[future]
                try:
                    result = future.result()
                    results[strategy] = result
                except Exception as e:
                    logger.error(f"策略 {strategy} 回测失败: {e}")
                    results[strategy] = None
        
        return results
    
    def _get_default_params(self):
        """
        获取默认参数
        """
        return {
            'strategies': ['sma', 'rsi', 'macd', 'bb', 'multi', 'regime'],
            
            # SMA
            'sma_fast': 20,
            'sma_slow': 60,
            
            # RSI
            'rsi_period': 14,
            'rsi_overbought': 65,
            'rsi_oversold': 35,
            
            # MACD
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            
            # 布林带
            'bb_period': 20,
            'bb_std': 2.0,
            
            # 风控
            'atr_period': 14,
            'atr_multiplier': 1.5,
            'target_vol': 0.01,
            'use_vol_sizing': True,
            
            # 宏观
            'use_dxy_filter': False,
            
            # 多因子
            'multi_factor_threshold': 2,
            
            # Regime
            'regime_quantile': 0.7,
        }
    
    def _run_sma_strategy(self, df, params):
        """
        运行SMA双均线策略
        """
        df = df.copy()
        
        # 生成入场出场信号
        df['entry'] = (df['sma_fast'] > df['sma_slow']) & (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1))
        df['exit'] = (df['sma_fast'] < df['sma_slow']) & (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1))
        
        return self._execute_backtest(df, params, 'sma')
    
    def _run_rsi_strategy(self, df, params):
        """
        运行RSI均值回归策略
        """
        df = df.copy()
        
        rsi_overbought = params.get('rsi_overbought', 65)
        rsi_oversold = params.get('rsi_oversold', 35)
        
        df['entry'] = (df['rsi'] < rsi_oversold) & (df['rsi'].shift(1) >= rsi_oversold)
        df['exit'] = (df['rsi'] > rsi_overbought) & (df['rsi'].shift(1) <= rsi_overbought)
        
        return self._execute_backtest(df, params, 'rsi')
    
    def _run_macd_strategy(self, df, params):
        """
        运行MACD动量策略
        """
        df = df.copy()
        
        df['entry'] = (df['macd_histogram'] > 0) & (df['macd_histogram'].shift(1) <= 0)
        df['exit'] = (df['macd_histogram'] < 0) & (df['macd_histogram'].shift(1) >= 0)
        
        return self._execute_backtest(df, params, 'macd')
    
    def _run_bb_strategy(self, df, params):
        """
        运行布林带突破策略
        """
        df = df.copy()
        
        df['entry'] = (df['bb_position'] < 0.1) & (df['bb_position'].shift(1) >= 0.1)
        df['exit'] = (df['bb_position'] > 0.9) & (df['bb_position'].shift(1) <= 0.9)
        
        return self._execute_backtest(df, params, 'bb')
    
    def _run_multi_factor_strategy(self, df, params):
        """
        运行多因子合成策略
        """
        df = df.copy()
        
        threshold = params.get('multi_factor_threshold', 2)
        
        # 计算因子得分
        df['score'] = (
            (df['sma_signal'] == 1).astype(int) +
            (df['rsi_signal'] == 1).astype(int) +
            (df['macd_signal_flag'] == 1).astype(int)
        )
        
        df['entry'] = df['score'] >= threshold
        df['exit'] = df['score'] == 0
        
        return self._execute_backtest(df, params, 'multi')
    
    def _run_regime_strategy(self, df, params):
        """
        运行基于Regime的多策略融合
        """
        df = df.copy()
        
        # 趋势策略信号（SMA）
        trend_entry = (df['sma_fast'] > df['sma_slow']) & (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1))
        trend_exit = (df['sma_fast'] < df['sma_slow']) & (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1))
        
        # 震荡策略信号（RSI）
        rsi_overbought = params.get('rsi_overbought', 65)
        rsi_oversold = params.get('rsi_oversold', 35)
        range_entry = (df['rsi'] < rsi_oversold) & (df['rsi'].shift(1) >= rsi_oversold)
        range_exit = (df['rsi'] > rsi_overbought) & (df['rsi'].shift(1) <= rsi_overbought)
        
        # 波动过滤
        vol_filter = df['atr'] < df['atr'].rolling(50).mean()
        
        # 根据Regime选择策略
        df['entry'] = False
        df['exit'] = False
        
        # TREND状态使用趋势策略
        df.loc[df['regime'] == 'TREND', 'entry'] = trend_entry & vol_filter
        df.loc[df['regime'] == 'TREND', 'exit'] = trend_exit
        
        # RANGE状态使用震荡策略
        df.loc[df['regime'] == 'RANGE', 'entry'] = range_entry & vol_filter
        df.loc[df['regime'] == 'RANGE', 'exit'] = range_exit
        
        return self._execute_backtest(df, params, 'regime')
    
    def _execute_backtest(self, df, params, strategy_name):
        """
        执行回测核心逻辑（向量化实现）
        """
        df = df.copy()
        n = len(df)
        
        # 初始资金
        cash = np.zeros(n)
        cash[0] = self.initial_cash
        
        # 持仓
        position = np.zeros(n)
        
        # 净值
        portfolio_value = np.zeros(n)
        portfolio_value[0] = self.initial_cash
        
        # 交易记录
        trades = []
        
        # ATR止损
        atr_multiplier = params.get('atr_multiplier', 1.5)
        use_dxy_filter = params.get('use_dxy_filter', False)
        
        # 向量化计算信号
        entry_signals = df['entry'].values
        exit_signals = df['exit'].values
        prices = df['close'].values
        
        # DXY过滤信号
        dxy_filter = np.zeros(n, dtype=bool)
        if use_dxy_filter and 'dxy_cross_up' in df.columns:
            dxy_filter = df['dxy_cross_up'].values == 1
        
        # ATR值
        atr = df['atr'].values if 'atr' in df.columns else np.zeros(n)
        atr_pct = df['atr_pct'].values if 'atr_pct' in df.columns else np.zeros(n)
        
        # 进入回测循环
        in_position = False
        entry_price = 0
        stop_loss = 0
        
        for i in range(1, n):
            # 前一天的净值
            cash[i] = cash[i-1]
            position[i] = position[i-1]
            
            # 当前价格
            current_price = prices[i]
            
            # DXY过滤
            if use_dxy_filter and dxy_filter[i] and in_position:
                # DXY上穿，平仓
                trades.append({
                    'date': df.index[i],
                    'type': 'exit',
                    'price': current_price,
                    'size': position[i-1],
                    'reason': 'dxy_filter'
                })
                
                # 计算收益（含手续费）
                proceeds = position[i-1] * current_price * (1 - self.commission)
                cash[i] += proceeds
                position[i] = 0
                in_position = False
                continue
            
            # 止损检查
            if in_position and current_price <= stop_loss:
                # 止损平仓
                trades.append({
                    'date': df.index[i],
                    'type': 'exit',
                    'price': current_price,
                    'size': position[i-1],
                    'reason': 'stop_loss'
                })
                
                proceeds = position[i-1] * current_price * (1 - self.commission)
                cash[i] += proceeds
                position[i] = 0
                in_position = False
                continue
            
            # 出场信号
            if in_position and exit_signals[i]:
                trades.append({
                    'date': df.index[i],
                    'type': 'exit',
                    'price': current_price,
                    'size': position[i-1],
                    'reason': 'signal'
                })
                
                proceeds = position[i-1] * current_price * (1 - self.commission)
                cash[i] += proceeds
                position[i] = 0
                in_position = False
                continue
            
            # 入场信号
            if not in_position and entry_signals[i]:
                # 计算仓位大小
                if params.get('use_vol_sizing', True):
                    target_vol = params.get('target_vol', 0.01)
                    if atr_pct[i] > 0:
                        position_size = (self.initial_cash * target_vol) / (atr_pct[i] * current_price)
                    else:
                        position_size = self.initial_cash * 0.5 / current_price
                else:
                    position_size = self.initial_cash * 0.5 / current_price
                
                position_size = min(position_size, cash[i] / (current_price * (1 + self.commission)))
                position_size = np.floor(position_size)
                
                if position_size > 0:
                    trades.append({
                        'date': df.index[i],
                        'type': 'entry',
                        'price': current_price,
                        'size': position_size,
                        'reason': 'signal'
                    })
                    
                    cost = position_size * current_price * (1 + self.commission)
                    cash[i] -= cost
                    position[i] = position_size
                    in_position = True
                    entry_price = current_price
                    stop_loss = entry_price - atr_multiplier * atr[i]
            
            # 计算净值
            portfolio_value[i] = cash[i] + position[i] * current_price
        
        # 生成统计信息
        stats = self._calculate_stats(portfolio_value, trades, df['close'])
        
        return {
            'portfolio_values': pd.Series(portfolio_value, index=df.index),
            'trades': trades,
            'stats': stats
        }
    
    def _calculate_stats(self, portfolio_values, trades, prices):
        """
        计算绩效指标
        """
        if isinstance(portfolio_values, np.ndarray):
            portfolio_values = pd.Series(portfolio_values)
        
        total_return = (portfolio_values.iloc[-1] - self.initial_cash) / self.initial_cash
        
        # 年化收益
        n_days = len(portfolio_values)
        ann_return = (1 + total_return) ** (252 / n_days) - 1
        
        # 夏普比率
        daily_returns = portfolio_values.pct_change().dropna()
        sharpe = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0
        
        # 最大回撤
        rolling_max = portfolio_values.cummax()
        drawdown = (portfolio_values - rolling_max) / rolling_max
        max_dd = drawdown.min()
        
        # 胜率
        n_trades = len([t for t in trades if t['type'] == 'exit'])
        win_rate = 0
        if n_trades > 0:
            win_trades = len([t for i, t in enumerate(trades) 
                            if t['type'] == 'exit' and 
                            i > 0 and trades[i-1]['type'] == 'entry' and
                            t['price'] > trades[i-1]['price']])
            win_rate = win_trades / n_trades if n_trades > 0 else 0
        
        return {
            'total_return': float(total_return),
            'ann_return': float(ann_return),
            'sharpe': float(sharpe),
            'max_dd': float(max_dd),
            'win_rate': float(win_rate),
            'n_trades': n_trades
        }
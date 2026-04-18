import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import yfinance as yf
from datetime import datetime

class AIHIFundamentalQuantStrategy:
    def __init__(self):
        self.model = None
        self.factor_weights = None
    
    def fetch_stock_data(self, symbol, start_date, end_date):
        """获取股票数据"""
        try:
            # 尝试从yfinance获取数据
            data = yf.download(symbol, start=start_date, end=end_date)
            if len(data) > 0:
                data.columns = data.columns.str.lower()
                # 确保必要的列存在
                if 'close' not in data.columns:
                    return pd.DataFrame()
                if 'high' not in data.columns:
                    data['high'] = data['close'] * 1.01
                if 'low' not in data.columns:
                    data['low'] = data['close'] * 0.99
                if 'volume' not in data.columns:
                    data['volume'] = 1000000
                return data
            else:
                # 生成模拟数据
                return self._generate_simulation_data(start_date, end_date)
        except Exception as e:
            # 生成模拟数据
            return self._generate_simulation_data(start_date, end_date)
    
    def _generate_simulation_data(self, start_date, end_date):
        """生成模拟数据"""
        # 创建日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n_days = len(dates)
        
        # GBM参数
        mu = 0.08  # 年化期望收益率
        sigma = 0.2  # 年化波动率
        dt = 1/252  # 日度时间步长
        
        # 生成价格路径
        np.random.seed(42)
        initial_price = 100.0
        
        # 几何布朗运动
        W = np.cumsum(np.random.normal(0, 1, n_days)) * np.sqrt(dt)
        t = np.arange(n_days) * dt
        price = initial_price * np.exp((mu - 0.5 * sigma**2) * t + sigma * W)
        
        # 构建DataFrame
        df = pd.DataFrame({
            'close': price,
            'high': price * (1 + np.random.uniform(0, 0.02, n_days)),
            'low': price * (1 - np.random.uniform(0, 0.02, n_days)),
            'open': price * (1 + np.random.uniform(-0.01, 0.01, n_days)),
            'volume': np.random.randint(100000, 1000000, n_days)
        }, index=dates)
        
        return df
    
    def load_config(self):
        """加载策略配置"""
        return {
            'value_factors': ['pe', 'pb', 'ps', 'pcf', 'ev_ebitda'],
            'quality_factors': ['roa', 'roe', 'profit_margin', 'asset_turnover', 'debt_to_equity'],
            'growth_factors': ['revenue_growth', 'earnings_growth', 'eps_growth', 'cash_flow_growth'],
            'analyst_factors': ['target_price', 'rating', 'earnings_estimate'],
            'ai_config': {
                'model_type': 'random_forest',
                'n_estimators': 100,
                'max_depth': 6,
                'random_state': 42
            },
            'strategy_config': {
                'holding_period': 20,
                'rebalance_frequency': 'monthly',
                'max_position': 0.05,
                'min_position': 0.005,
                'transaction_cost': 0.0003
            }
        }
    
    def calculate_value_factors(self, data):
        """计算价值因子"""
        factors = {}
        factors['pe'] = data['close'] / data['eps']
        factors['pb'] = data['close'] / data['book_value_per_share']
        factors['ps'] = data['close'] / data['sales_per_share']
        factors['pcf'] = data['close'] / data['cash_flow_per_share']
        factors['ev_ebitda'] = (data['market_cap'] + data['total_debt'] - data['cash']) / data['ebitda']
        return factors
    
    def calculate_quality_factors(self, data):
        """计算质量因子"""
        factors = {}
        factors['roa'] = data['net_profit'] / data['total_assets']
        factors['roe'] = data['net_profit'] / data['total_equity']
        factors['profit_margin'] = data['net_profit'] / data['revenue']
        factors['asset_turnover'] = data['revenue'] / data['total_assets']
        factors['debt_to_equity'] = data['total_debt'] / data['total_equity']
        return factors
    
    def calculate_growth_factors(self, data):
        """计算成长因子"""
        factors = {}
        factors['revenue_growth'] = data['revenue'].pct_change(4)
        factors['earnings_growth'] = data['net_profit'].pct_change(4)
        factors['eps_growth'] = data['eps'].pct_change(4)
        factors['cash_flow_growth'] = data['operating_cash_flow'].pct_change(4)
        return factors
    
    def calculate_analyst_factors(self, data):
        """计算分析师预期因子"""
        factors = {}
        factors['target_price'] = data['target_price'] / data['close'] - 1
        factors['rating'] = data['analyst_rating']
        factors['earnings_estimate'] = data['earnings_estimate'] / data['eps'] - 1
        return factors
    
    def calculate_all_factors(self, data):
        """计算所有因子"""
        factors = {}
        factors.update(self.calculate_value_factors(data))
        factors.update(self.calculate_quality_factors(data))
        factors.update(self.calculate_growth_factors(data))
        factors.update(self.calculate_analyst_factors(data))
        return factors
    
    def prepare_training_data(self, data):
        """准备训练数据"""
        # 计算因子
        factors = self.calculate_all_factors(data)
        factor_df = pd.DataFrame(factors)
        
        # 计算目标变量（未来收益率）
        data['future_return'] = data['close'].pct_change(20).shift(-20)
        
        # 合并因子和目标变量
        training_data = pd.concat([factor_df, data['future_return']], axis=1)
        
        # 移除缺失值
        training_data = training_data.dropna()
        
        return training_data
    
    def train_ai_model(self, training_data):
        """训练AI模型"""
        X = training_data.drop('future_return', axis=1)
        y = training_data['future_return']
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 训练模型
        config = self.load_config()
        self.model = RandomForestRegressor(
            n_estimators=config['ai_config']['n_estimators'],
            max_depth=config['ai_config']['max_depth'],
            random_state=config['ai_config']['random_state']
        )
        self.model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Model MSE: {mse}")
        
        # 获取特征重要性
        feature_importance = self.model.feature_importances_
        self.factor_weights = dict(zip(X.columns, feature_importance))
        print("Factor Weights:")
        for factor, weight in sorted(self.factor_weights.items(), key=lambda x: x[1], reverse=True):
            print(f"{factor}: {weight:.4f}")
    
    def dynamic_factor_weighting(self, market_regime):
        """动态因子加权"""
        # 根据市场状态调整因子权重
        if market_regime == 'bull':
            # 牛市中增加成长因子权重
            weight_adjustment = {
                'revenue_growth': 1.2,
                'earnings_growth': 1.2,
                'eps_growth': 1.2
            }
        elif market_regime == 'bear':
            # 熊市中增加价值和质量因子权重
            weight_adjustment = {
                'pe': 1.2,
                'pb': 1.2,
                'roa': 1.2,
                'roe': 1.2
            }
        else:
            # 震荡市保持均衡权重
            weight_adjustment = {}
        
        # 应用权重调整
        adjusted_weights = {}
        for factor, weight in self.factor_weights.items():
            adjusted_weights[factor] = weight * weight_adjustment.get(factor, 1.0)
        
        # 归一化权重
        total_weight = sum(adjusted_weights.values())
        normalized_weights = {k: v / total_weight for k, v in adjusted_weights.items()}
        
        return normalized_weights
    
    def generate_signals(self, data):
        """生成交易信号"""
        # 计算因子
        factors = self.calculate_all_factors(data)
        factor_df = pd.DataFrame(factors)
        
        # 预测未来收益率
        if self.model is not None:
            predictions = self.model.predict(factor_df)
            data['predicted_return'] = predictions
        else:
            # 如果模型未训练，使用等权因子得分
            data['predicted_return'] = factor_df.mean(axis=1)
        
        # 生成信号：排名前20%的股票买入，后20%的股票卖出
        data['signal'] = 0
        top_20_percent = data['predicted_return'].quantile(0.8)
        bottom_20_percent = data['predicted_return'].quantile(0.2)
        data.loc[data['predicted_return'] > top_20_percent, 'signal'] = 1
        data.loc[data['predicted_return'] < bottom_20_percent, 'signal'] = -1
        
        return data
    
    def risk_control(self, portfolio, risk_params):
        """风险控制"""
        # 限制单个股票仓位
        portfolio = portfolio[portfolio <= risk_params['max_position']]
        portfolio = portfolio[portfolio >= risk_params['min_position']]
        
        # 归一化仓位
        if portfolio.sum() > 0:
            portfolio = portfolio / portfolio.sum()
        
        return portfolio
    
    def backtest(self, data, start_date, end_date):
        """回测策略"""
        # 准备训练数据
        training_data = self.prepare_training_data(data)
        
        # 训练AI模型
        self.train_ai_model(training_data)
        
        # 生成信号
        data_with_signals = self.generate_signals(data)
        
        # 转换信号格式以适应BacktestEngine
        data_with_signals['entry'] = data_with_signals['signal'] == 1
        data_with_signals['exit'] = data_with_signals['signal'] == -1
        
        # 计算ATR指标（BacktestEngine需要）
        data_with_signals['high'] = data_with_signals.get('high', data_with_signals['close'] * 1.01)
        data_with_signals['low'] = data_with_signals.get('low', data_with_signals['close'] * 0.99)
        data_with_signals['atr'] = data_with_signals[['high', 'low', 'close']].apply(
            lambda row: max(row['high'] - row['low'], 
                           abs(row['high'] - row['close']), 
                           abs(row['low'] - row['close'])), axis=1
        )
        data_with_signals['atr'] = data_with_signals['atr'].rolling(14).mean()
        data_with_signals['atr_pct'] = data_with_signals['atr'] / data_with_signals['close']
        
        # 运行回测
        params = {
            'strategies': ['multi'],  # 使用多因子策略框架
            'multi_factor_threshold': 1,
            'use_vol_sizing': True,
            'target_vol': 0.01,
            'atr_multiplier': 1.5
        }
        
        # 由于BacktestEngine的_execute_backtest方法是私有的，我们需要创建一个简单的回测逻辑
        # 这里实现一个简化的回测逻辑
        def simple_backtest(df, initial_cash=100000, commission=0.0003):
            n = len(df)
            cash = np.zeros(n)
            cash[0] = initial_cash
            position = np.zeros(n)
            portfolio_value = np.zeros(n)
            portfolio_value[0] = initial_cash
            trades = []
            in_position = False
            
            for i in range(1, n):
                cash[i] = cash[i-1]
                position[i] = position[i-1]
                current_price = df['close'].iloc[i]
                
                # 出场信号
                if in_position and df['exit'].iloc[i]:
                    trades.append({
                        'date': df.index[i],
                        'type': 'exit',
                        'price': current_price,
                        'size': position[i-1],
                        'reason': 'signal'
                    })
                    proceeds = position[i-1] * current_price * (1 - commission)
                    cash[i] += proceeds
                    position[i] = 0
                    in_position = False
                    continue
                
                # 入场信号
                if not in_position and df['entry'].iloc[i]:
                    position_size = cash[i] * 0.5 / (current_price * (1 + commission))
                    position_size = np.floor(position_size)
                    
                    if position_size > 0:
                        trades.append({
                            'date': df.index[i],
                            'type': 'entry',
                            'price': current_price,
                            'size': position_size,
                            'reason': 'signal'
                        })
                        cost = position_size * current_price * (1 + commission)
                        cash[i] -= cost
                        position[i] = position_size
                        in_position = True
                
                # 计算净值
                portfolio_value[i] = cash[i] + position[i] * current_price
            
            # 计算统计信息
            total_return = (portfolio_value[-1] - initial_cash) / initial_cash
            n_days = len(portfolio_value)
            ann_return = (1 + total_return) ** (252 / n_days) - 1
            daily_returns = pd.Series(portfolio_value).pct_change().dropna()
            sharpe = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0
            rolling_max = pd.Series(portfolio_value).cummax()
            drawdown = (pd.Series(portfolio_value) - rolling_max) / rolling_max
            max_dd = drawdown.min()
            n_trades = len([t for t in trades if t['type'] == 'exit'])
            win_rate = 0
            if n_trades > 0:
                win_trades = len([t for i, t in enumerate(trades) 
                                if t['type'] == 'exit' and 
                                i > 0 and trades[i-1]['type'] == 'entry' and
                                t['price'] > trades[i-1]['price']])
                win_rate = win_trades / n_trades if n_trades > 0 else 0
            
            stats = {
                'total_return': float(total_return),
                'ann_return': float(ann_return),
                'sharpe': float(sharpe),
                'max_dd': float(max_dd),
                'win_rate': float(win_rate),
                'n_trades': n_trades
            }
            
            return {
                'portfolio_values': pd.Series(portfolio_value, index=df.index),
                'trades': trades,
                'stats': stats
            }
        
        # 运行简化的回测
        results = simple_backtest(
            data_with_signals,
            commission=self.load_config()['strategy_config']['transaction_cost']
        )
        
        return results
    
    def generate_fake_fundamental_data(self, data):
        """生成模拟基本面数据"""
        # 生成基本的基本面数据
        data['eps'] = np.random.uniform(0.5, 5.0, len(data))
        data['book_value_per_share'] = np.random.uniform(5.0, 50.0, len(data))
        data['sales_per_share'] = np.random.uniform(10.0, 100.0, len(data))
        data['cash_flow_per_share'] = np.random.uniform(1.0, 10.0, len(data))
        data['market_cap'] = data['close'] * 10000000
        data['total_debt'] = np.random.uniform(100000000, 1000000000, len(data))
        data['cash'] = np.random.uniform(50000000, 500000000, len(data))
        data['ebitda'] = np.random.uniform(50000000, 500000000, len(data))
        data['net_profit'] = np.random.uniform(20000000, 200000000, len(data))
        data['total_assets'] = np.random.uniform(500000000, 5000000000, len(data))
        data['total_equity'] = np.random.uniform(200000000, 2000000000, len(data))
        data['revenue'] = np.random.uniform(100000000, 1000000000, len(data))
        data['operating_cash_flow'] = np.random.uniform(30000000, 300000000, len(data))
        data['target_price'] = data['close'] * np.random.uniform(0.8, 1.2, len(data))
        data['analyst_rating'] = np.random.uniform(1.0, 5.0, len(data))
        data['earnings_estimate'] = data['eps'] * np.random.uniform(0.9, 1.1, len(data))
        return data
    
    def run_strategy(self, symbols, start_date, end_date):
        """运行策略"""
        # 获取数据
        all_data = {}
        for symbol in symbols:
            # 使用fetch_stock_data获取股票数据
            data = self.fetch_stock_data(symbol, start_date, end_date)
            if not data.empty:
                # 生成模拟基本面数据
                data = self.generate_fake_fundamental_data(data)
                all_data[symbol] = data
        
        # 对每个股票运行策略
        results = {}
        for symbol, data in all_data.items():
            try:
                result = self.backtest(data, start_date, end_date)
                results[symbol] = result
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
        
        return results
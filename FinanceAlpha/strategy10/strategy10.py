# 策略10：另类数据驱动的事件驱动量化策略

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class AlternativeDataDrivenStrategy:
    """另类数据驱动的事件驱动量化策略"""
    
    def __init__(self):
        """初始化策略"""
        self.data_dir = 'data/'
        os.makedirs(self.data_dir, exist_ok=True)
        self.strategies = {
            'sentiment_forecast': self._sentiment_forecast_strategy,
            'event_driven': self._event_driven_strategy,
            'sector_rotation': self._sector_rotation_strategy
        }
    
    def _fetch_supply_chain_data(self, ticker, start_date, end_date):
        """获取供应链数据"""
        # 模拟数据获取
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        data = {
            'date': dates,
            'supplier_delivery_time': np.random.normal(15, 3, len(dates)),
            'inventory_level': np.random.normal(100, 20, len(dates)),
            'production_rate': np.random.normal(50, 10, len(dates))
        }
        df = pd.DataFrame(data)
        return df
    
    def _fetch_ecommerce_data(self, category, start_date, end_date):
        """获取电商与消费数据"""
        # 模拟数据获取
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        data = {
            'date': dates,
            'sales': np.random.normal(1000, 200, len(dates)),
            'units_sold': np.random.normal(500, 100, len(dates)),
            'customer_sentiment': np.random.normal(4, 0.5, len(dates))
        }
        df = pd.DataFrame(data)
        return df
    
    def _fetch_satellite_data(self, region, start_date, end_date):
        """获取卫星遥感数据"""
        # 模拟数据获取
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        data = {
            'date': dates,
            'activity_level': np.random.normal(0.5, 0.1, len(dates)),
            'storage_volume': np.random.normal(10000, 2000, len(dates))
        }
        df = pd.DataFrame(data)
        return df
    
    def _fetch_fund_flow_data(self, ticker, start_date, end_date):
        """获取资金流数据"""
        # 模拟数据获取
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        data = {
            'date': dates,
            'inflow': np.random.normal(1000000, 200000, len(dates)),
            'outflow': np.random.normal(900000, 180000, len(dates)),
            'net_flow': np.random.normal(100000, 50000, len(dates))
        }
        df = pd.DataFrame(data)
        return df
    
    def _fetch_insider_activity_data(self, ticker, start_date, end_date):
        """获取高管与股东行为数据"""
        # 模拟数据获取
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        data = {
            'date': dates,
            'transaction_type': np.random.choice(['BUY', 'SELL'], len(dates)),
            'amount': np.random.normal(100000, 20000, len(dates)),
            'insider_count': np.random.randint(1, 5, len(dates))
        }
        df = pd.DataFrame(data)
        return df
    
    def _clean_data(self, df):
        """清洗数据"""
        # 去除重复值
        df = df.drop_duplicates()
        # 填充缺失值
        df = df.fillna(method='ffill').fillna(method='bfill')
        # 标准化数值列
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != 'date':
                df[col] = (df[col] - df[col].mean()) / df[col].std()
        return df
    
    def _feature_engineering(self, df):
        """特征工程"""
        # 添加滞后特征
        for lag in [1, 3, 5]:
            for col in df.select_dtypes(include=[np.number]).columns:
                if col != 'date':
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        # 添加滚动特征
        for window in [7, 14, 30]:
            for col in df.select_dtypes(include=[np.number]).columns:
                if col != 'date':
                    df[f'{col}_ma_{window}'] = df[col].rolling(window=window).mean()
                    df[f'{col}_std_{window}'] = df[col].rolling(window=window).std()
        
        # 添加动量特征
        for col in df.select_dtypes(include=[np.number]).columns:
            if col != 'date':
                df[f'{col}_momentum'] = df[col] - df[col].shift(5)
        
        return df.dropna()
    
    def _sentiment_forecast_strategy(self, ticker, start_date, end_date):
        """景气度提前预判策略"""
        # 获取数据
        sc_data = self._fetch_supply_chain_data(ticker, start_date, end_date)
        ec_data = self._fetch_ecommerce_data('electronics', start_date, end_date)
        ff_data = self._fetch_fund_flow_data(ticker, start_date, end_date)
        
        # 合并数据
        if not sc_data.empty and not ec_data.empty and not ff_data.empty:
            df = pd.merge(sc_data, ec_data, on='date', how='inner')
            df = pd.merge(df, ff_data, on='date', how='inner')
            
            # 添加价格数据（模拟）
            df['close'] = 100 + np.cumsum(np.random.normal(0, 1, len(df)))
            
            # 特征工程
            df = self._feature_engineering(df)
            
            # 生成标签
            df['target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
            df = df.dropna()
            
            if len(df) > 10:
                # 训练模型
                X = df.drop(['date', 'target', 'close'], axis=1)
                y = df['target']
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model = RandomForestClassifier(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                
                # 预测
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # 生成信号
                latest_features = X.iloc[-1].values.reshape(1, -1)
                prediction = model.predict(latest_features)[0]
                confidence = model.predict_proba(latest_features)[0][prediction]
                
                if confidence > 0.7:
                    if prediction == 1:
                        return 'BUY', confidence
                    else:
                        return 'SELL', confidence
        
        return 'HOLD', 0
    
    def _event_driven_strategy(self, ticker, start_date, end_date):
        """短线事件驱动策略"""
        # 获取内幕交易数据
        ia_data = self._fetch_insider_activity_data(ticker, start_date, end_date)
        
        if not ia_data.empty:
            # 分析内幕交易
            buy_transactions = ia_data[ia_data['transaction_type'] == 'BUY']
            sell_transactions = ia_data[ia_data['transaction_type'] == 'SELL']
            
            # 计算净买入
            net_buy = buy_transactions['amount'].sum() - sell_transactions['amount'].sum()
            
            # 分析交易频率
            buy_count = len(buy_transactions)
            sell_count = len(sell_transactions)
            
            # 生成信号
            if buy_count > sell_count and net_buy > 0:
                return 'BUY', buy_count / (buy_count + sell_count)
            elif sell_count > buy_count and net_buy < 0:
                return 'SELL', sell_count / (buy_count + sell_count)
        
        return 'HOLD', 0
    
    def _sector_rotation_strategy(self, start_date, end_date):
        """行业轮动策略"""
        sectors = ['tech', 'finance', 'healthcare', 'consumer']
        sector_scores = {}
        
        # 分析每个行业
        for sector in sectors:
            # 获取电商数据
            ec_data = self._fetch_ecommerce_data(sector, start_date, end_date)
            
            if not ec_data.empty:
                # 计算行业景气度得分
                sales_growth = (ec_data['sales'].iloc[-1] - ec_data['sales'].iloc[0]) / ec_data['sales'].iloc[0]
                sentiment_score = ec_data['customer_sentiment'].mean()
                
                # 综合得分
                score = 0.6 * sales_growth + 0.4 * sentiment_score
                sector_scores[sector] = score
        
        # 选择得分最高的行业
        if sector_scores:
            best_sector = max(sector_scores, key=sector_scores.get)
            return best_sector, sector_scores[best_sector]
        
        return None, 0
    
    def generate_signals(self, ticker):
        """生成信号"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        signals = {}
        
        # 运行景气度提前预判策略
        sf_signal, sf_confidence = self._sentiment_forecast_strategy(ticker, start_date, end_date)
        signals['sentiment_forecast'] = {'signal': sf_signal, 'confidence': sf_confidence}
        
        # 运行短线事件驱动策略
        ed_signal, ed_confidence = self._event_driven_strategy(ticker, start_date, end_date)
        signals['event_driven'] = {'signal': ed_signal, 'confidence': ed_confidence}
        
        # 运行行业轮动策略
        sr_sector, sr_score = self._sector_rotation_strategy(start_date, end_date)
        signals['sector_rotation'] = {'sector': sr_sector, 'score': sr_score}
        
        # 计算综合信号
        buy_count = 0
        sell_count = 0
        total_confidence = 0
        
        for strategy, result in signals.items():
            if strategy in ['sentiment_forecast', 'event_driven']:
                if result['signal'] == 'BUY':
                    buy_count += 1
                    total_confidence += result['confidence']
                elif result['signal'] == 'SELL':
                    sell_count += 1
                    total_confidence += result['confidence']
        
        if buy_count > sell_count and total_confidence > 1.0:
            combined_signal = 'BUY'
            combined_confidence = total_confidence / (buy_count + sell_count)
        elif sell_count > buy_count and total_confidence > 1.0:
            combined_signal = 'SELL'
            combined_confidence = total_confidence / (buy_count + sell_count)
        else:
            combined_signal = 'HOLD'
            combined_confidence = 0
        
        signals['combined'] = {'signal': combined_signal, 'confidence': combined_confidence}
        
        return signals
    
    def backtest(self, ticker, start_date, end_date):
        """回测策略"""
        # 生成回测日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        
        # 初始化回测结果
        results = pd.DataFrame(index=dates, columns=['price', 'signal', 'position', 'cash', 'portfolio_value'])
        
        # 初始值
        initial_capital = 1000000
        results['cash'] = initial_capital
        results['position'] = 0
        results['portfolio_value'] = initial_capital
        
        # 模拟回测
        for i, date in enumerate(dates):
            # 生成价格数据（模拟）
            if i == 0:
                price = 100
            else:
                price = results.loc[dates[i-1], 'price'] + np.random.normal(0, 1)
            results.loc[date, 'price'] = price
            
            # 生成信号
            if i > 0:
                signal_data = self.generate_signals(ticker)
                signal = signal_data['combined']['signal']
                results.loc[date, 'signal'] = signal
                
                # 执行交易
                if signal == 'BUY' and results.loc[date, 'position'] == 0:
                    # 买入
                    shares = results.loc[dates[i-1], 'cash'] // price
                    results.loc[date, 'position'] = shares
                    results.loc[date, 'cash'] = results.loc[dates[i-1], 'cash'] - shares * price
                elif signal == 'SELL' and results.loc[date, 'position'] > 0:
                    # 卖出
                    results.loc[date, 'cash'] = results.loc[dates[i-1], 'cash'] + results.loc[dates[i-1], 'position'] * price
                    results.loc[date, 'position'] = 0
                else:
                    # 保持不变
                    results.loc[date, 'position'] = results.loc[dates[i-1], 'position']
                    results.loc[date, 'cash'] = results.loc[dates[i-1], 'cash']
            
            # 计算 portfolio value
            if results.loc[date, 'position'] > 0:
                results.loc[date, 'portfolio_value'] = results.loc[date, 'cash'] + results.loc[date, 'position'] * price
            else:
                results.loc[date, 'portfolio_value'] = results.loc[date, 'cash']
        
        # 计算性能指标
        performance = self._calculate_performance(results)
        
        return results, performance
    
    def _calculate_performance(self, results):
        """计算性能指标"""
        # 计算收益率
        returns = results['portfolio_value'].pct_change().dropna()
        
        # 计算累计收益率
        cumulative_return = (results['portfolio_value'].iloc[-1] / results['portfolio_value'].iloc[0]) - 1
        
        # 计算年化收益率
        days = (results.index[-1] - results.index[0]).days
        annual_return = (1 + cumulative_return) ** (365 / days) - 1
        
        # 计算波动率
        annual_volatility = returns.std() * np.sqrt(252)
        
        # 计算夏普比率
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        
        # 计算最大回撤
        portfolio_value = results['portfolio_value']
        rolling_max = portfolio_value.cummax()
        drawdown = (portfolio_value - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        performance = {
            'cumulative_return': cumulative_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
        
        return performance
    
    def run_strategy(self, ticker):
        """运行策略"""
        print(f"Running Alternative Data Driven Strategy for {ticker}...")
        signals = self.generate_signals(ticker)
        
        print("\nStrategy Results:")
        print(f"Sentiment Forecast: {signals['sentiment_forecast']['signal']} (Confidence: {signals['sentiment_forecast']['confidence']:.2f})")
        print(f"Event Driven: {signals['event_driven']['signal']} (Confidence: {signals['event_driven']['confidence']:.2f})")
        print(f"Sector Rotation: {signals['sector_rotation']['sector']} (Score: {signals['sector_rotation']['score']:.2f})")
        print(f"\nCombined Signal: {signals['combined']['signal']} (Confidence: {signals['combined']['confidence']:.2f})")
        
        return signals
    
    def run_backtest(self, ticker, start_date, end_date):
        """运行回测"""
        print(f"Running backtest for {ticker} from {start_date} to {end_date}...")
        results, performance = self.backtest(ticker, start_date, end_date)
        
        print("\nBacktest Performance:")
        print(f"Cumulative Return: {performance['cumulative_return']:.2%}")
        print(f"Annual Return: {performance['annual_return']:.2%}")
        print(f"Annual Volatility: {performance['annual_volatility']:.2%}")
        print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {performance['max_drawdown']:.2%}")
        
        return results, performance
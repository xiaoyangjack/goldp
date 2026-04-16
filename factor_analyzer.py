"""
因子分析模块
功能：
- 因子相关性分析
- 因子重要性评估
- 因子组合优化
- 回测分析
"""
import os
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from loguru import logger

class FactorAnalyzer:
    """因子分析器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_data(self, file_path=None):
        """加载数据"""
        if file_path is None:
            file_path = os.path.join(self.data_dir, 'macro_factors_merged.csv')
        
        if not os.path.exists(file_path):
            logger.error(f"数据文件不存在: {file_path}")
            return None
        
        try:
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            logger.info(f"加载数据成功，共 {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return None
    
    def calculate_returns(self, df, price_col='gold_close', period=1):
        """计算收益率"""
        df = df.copy()
        df[f'return_{period}d'] = df[price_col].pct_change(period) * 100
        return df.dropna()
    
    def factor_correlation(self, df, target_col='return_1d'):
        """计算因子相关性"""
        # 选择因子列
        factor_cols = [col for col in df.columns if col not in ['date', 'gold_close', 'return_1d', 'return_5d', 'return_10d']]
        
        # 计算相关性
        correlations = {}
        for col in factor_cols:
            if col in df.columns:
                corr = df[target_col].corr(df[col])
                correlations[col] = corr
        
        # 按相关性绝对值排序
        sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        return sorted_correlations
    
    def factor_importance(self, df, target_col='return_1d'):
        """评估因子重要性"""
        # 选择因子列
        factor_cols = [col for col in df.columns if col not in ['date', 'gold_close', 'return_1d', 'return_5d', 'return_10d']]
        
        # 准备数据
        X = df[factor_cols].dropna()
        y = df.loc[X.index, target_col]
        
        if len(X) < 20:
            logger.warning("数据量不足，无法进行因子重要性评估")
            return []
        
        # 拆分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # 训练随机森林模型
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 预测
        y_pred = model.predict(X_test)
        
        # 评估模型
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        logger.info(f"模型评估: R² = {r2:.4f}, MSE = {mse:.4f}")
        
        # 获取特征重要性
        importances = list(zip(factor_cols, model.feature_importances_))
        importances.sort(key=lambda x: x[1], reverse=True)
        
        return importances
    
    def factor_analysis(self, file_path=None):
        """综合因子分析"""
        # 加载数据
        df = self.load_data(file_path)
        if df is None:
            return None
        
        # 计算收益率
        df = self.calculate_returns(df)
        df = self.calculate_returns(df, period=5)
        df = self.calculate_returns(df, period=10)
        
        # 计算因子相关性
        corr_1d = self.factor_correlation(df, 'return_1d')
        corr_5d = self.factor_correlation(df, 'return_5d')
        corr_10d = self.factor_correlation(df, 'return_10d')
        
        # 评估因子重要性
        importance_1d = self.factor_importance(df, 'return_1d')
        
        # 生成分析报告
        analysis = {
            'data_info': {
                'rows': len(df),
                'date_range': f"{df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}"
            },
            'correlation': {
                '1d_return': corr_1d,
                '5d_return': corr_5d,
                '10d_return': corr_10d
            },
            'importance': {
                '1d_return': importance_1d
            },
            'key_factors': self._identify_key_factors(corr_1d, importance_1d)
        }
        
        return analysis
    
    def _identify_key_factors(self, correlations, importances, top_n=5):
        """识别关键因子"""
        # 综合相关性和重要性
        corr_dict = dict(correlations)
        imp_dict = dict(importances)
        
        # 计算综合得分
        factors = set(corr_dict.keys()) | set(imp_dict.keys())
        scores = {}
        
        for factor in factors:
            corr_score = abs(corr_dict.get(factor, 0))
            imp_score = imp_dict.get(factor, 0)
            # 综合得分 = 相关性权重0.6 + 重要性权重0.4
            scores[factor] = 0.6 * corr_score + 0.4 * imp_score
        
        # 排序并返回前N个因子
        sorted_factors = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return sorted_factors
    
    def backtest_with_factors(self, df, key_factors, strategy='ma_crossover', params=None):
        """基于因子的回测"""
        if params is None:
            params = {
                'fast_ma': 10,
                'slow_ma': 30,
                'signal_threshold': 0.5,
                'atr_threshold': 35,
                'stop_loss': 5
            }
        
        # 计算指标
        df = df.copy()
        df['ma_fast'] = df['gold_close'].rolling(window=params['fast_ma']).mean()
        df['ma_slow'] = df['gold_close'].rolling(window=params['slow_ma']).mean()
        df['ma_diff'] = df['ma_fast'] - df['ma_slow']
        
        # 生成信号
        df['signal'] = 'WATCH'
        df.loc[df['ma_diff'] > params['signal_threshold'], 'signal'] = 'BUY'
        df.loc[df['ma_diff'] < -params['signal_threshold'], 'signal'] = 'SELL'
        
        # 回测
        initial_cash = 100000
        cash = initial_cash
        position = 0
        entry_price = 0
        equity_curve = [initial_cash]
        trades = []
        
        for i in range(1, len(df)):
            price = df['gold_close'].iloc[i]
            signal = df['signal'].iloc[i]
            
            # 执行交易
            if signal == 'BUY' and position == 0:
                # 买入
                position = cash / price
                entry_price = price
                cash = 0
                trades.append({
                    'date': df['date'].iloc[i],
                    'type': 'BUY',
                    'price': price,
                    'size': position
                })
            elif signal == 'SELL' and position > 0:
                # 卖出
                cash = position * price
                pnl = cash - (position * entry_price)
                trades.append({
                    'date': df['date'].iloc[i],
                    'type': 'SELL',
                    'price': price,
                    'size': position,
                    'pnl': pnl
                })
                position = 0
                entry_price = 0
            
            # 计算当前权益
            current_equity = cash + (position * price)
            equity_curve.append(current_equity)
        
        # 计算回测指标
        final_equity = equity_curve[-1]
        total_return = (final_equity - initial_cash) / initial_cash * 100
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)
        
        # 计算胜率
        win_trades = [t for t in trades if t.get('pnl', 0) > 0]
        win_rate = len(win_trades) / len(trades) * 100 if trades else 0
        
        return {
            'metrics': {
                'initial_cash': initial_cash,
                'final_equity': final_equity,
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'total_trades': len(trades),
                'win_rate': win_rate
            },
            'equity_curve': equity_curve,
            'trades': trades
        }
    
    def _calculate_max_drawdown(self, equity_curve):
        """计算最大回撤"""
        if len(equity_curve) < 2:
            return 0
        
        peak = equity_curve[0]
        max_dd = 0
        
        for value in equity_curve[1:]:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, equity_curve, risk_free_rate=0.02):
        """计算夏普比率"""
        if len(equity_curve) < 2:
            return 0
        
        # 计算日收益率
        returns = []
        for i in range(1, len(equity_curve)):
            daily_return = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(daily_return)
        
        if not returns:
            return 0
        
        # 计算年化收益率和波动率
        avg_return = np.mean(returns) * 252
        std_return = np.std(returns) * np.sqrt(252)
        
        if std_return == 0:
            return 0
        
        # 计算夏普比率
        sharpe = (avg_return - risk_free_rate) / std_return
        return sharpe

# 全局实例
factor_analyzer = FactorAnalyzer()
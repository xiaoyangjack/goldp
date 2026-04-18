import numpy as np
import pandas as pd
from .iv_surface_model import IVSurfaceFitter
from .gamma_squeeze_predictor import GammaSqueezePredictor

class ODTEArbStrategy:
    def __init__(self):
        self.iv_fitter = IVSurfaceFitter()
        self.gamma_predictor = GammaSqueezePredictor()
        self.gamma_predictor.set_iv_fitter(self.iv_fitter)
        self.arb_opportunities = []
    
    def identify_arb_opportunities(self, option_chain, underlying_price, time_to_expiry):
        """识别0DTE期权的套利机会"""
        opportunities = []
        
        # 拟合IV曲面
        self.iv_fitter.fit_surface(option_chain)
        
        # 分析每个期权的定价
        for _, option in option_chain.iterrows():
            strike = option['strike']
            market_iv = option['implied_volatility']
            option_type = option['option_type']
            
            # 预测合理的IV
            predicted_iv = self.gamma_predictor.predict_iv_for_strike(
                strike, underlying_price, time_to_expiry
            )
            
            # 计算IV偏差
            iv_diff = market_iv - predicted_iv
            iv_diff_pct = iv_diff / predicted_iv if predicted_iv > 0 else 0
            
            # 识别套利机会
            if abs(iv_diff_pct) > 0.05:  # 5%的IV偏差
                opportunity = {
                    'strike': strike,
                    'option_type': option_type,
                    'market_iv': market_iv,
                    'predicted_iv': predicted_iv,
                    'iv_diff_pct': iv_diff_pct,
                    'arb_strategy': self.determine_arb_strategy(iv_diff_pct, option_type),
                    'potential_profit': self.calculate_potential_profit(iv_diff_pct, option)
                }
                opportunities.append(opportunity)
        
        # 按潜在收益排序
        opportunities.sort(key=lambda x: abs(x['potential_profit']), reverse=True)
        self.arb_opportunities = opportunities
        
        return opportunities
    
    def determine_arb_strategy(self, iv_diff_pct, option_type):
        """确定套利策略类型"""
        if iv_diff_pct > 0:
            # 市场IV过高，应该卖出期权
            return f'sell_{option_type}'
        else:
            # 市场IV过低，应该买入期权
            return f'buy_{option_type}'
    
    def calculate_potential_profit(self, iv_diff_pct, option):
        """计算潜在收益"""
        # 基于IV偏差和期权价格计算潜在收益
        option_price = option['last_price']
        potential_profit = option_price * abs(iv_diff_pct)
        
        return potential_profit
    
    def generate_arb_portfolio(self, opportunities, max_positions=5):
        """生成套利投资组合"""
        portfolio = []
        total_investment = 0
        
        # 选择最佳的套利机会
        for opportunity in opportunities[:max_positions]:
            # 计算头寸大小
            position_size = min(10000, int(opportunity['potential_profit'] * 100))
            investment = position_size * opportunity['market_iv'] * 100
            
            portfolio_item = {
                'strike': opportunity['strike'],
                'option_type': opportunity['option_type'],
                'strategy': opportunity['arb_strategy'],
                'position_size': position_size,
                'investment': investment,
                'potential_profit': opportunity['potential_profit'] * position_size
            }
            
            portfolio.append(portfolio_item)
            total_investment += investment
        
        return {
            'portfolio': portfolio,
            'total_investment': total_investment,
            'expected_return': sum(item['potential_profit'] for item in portfolio) / total_investment if total_investment > 0 else 0
        }
    
    def backtest_arb_strategy(self, historical_data):
        """回测套利策略"""
        results = []
        
        for date, data in historical_data.items():
            option_chain = data['option_chain']
            underlying_price = data['underlying_price']
            time_to_expiry = data['time_to_expiry']
            
            # 识别套利机会
            opportunities = self.identify_arb_opportunities(
                option_chain, underlying_price, time_to_expiry
            )
            
            # 生成投资组合
            portfolio = self.generate_arb_portfolio(opportunities)
            
            # 计算实际收益（模拟）
            actual_return = self.simulate_actual_return(portfolio, data['next_day_data'])
            
            results.append({
                'date': date,
                'opportunities_found': len(opportunities),
                'total_investment': portfolio['total_investment'],
                'expected_return': portfolio['expected_return'],
                'actual_return': actual_return
            })
        
        return pd.DataFrame(results)
    
    def simulate_actual_return(self, portfolio, next_day_data):
        """模拟实际收益"""
        # 简化的收益模拟
        total_profit = 0
        
        for item in portfolio['portfolio']:
            # 假设期权价格变化基于IV变化
            iv_change = np.random.normal(0, 0.02)  # 模拟IV变化
            profit = item['position_size'] * item['market_iv'] * iv_change
            total_profit += profit
        
        return total_profit / portfolio['total_investment'] if portfolio['total_investment'] > 0 else 0
    
    def set_iv_fitter(self, iv_fitter):
        """设置IV曲面拟合器"""
        self.iv_fitter = iv_fitter
        self.gamma_predictor.set_iv_fitter(iv_fitter)
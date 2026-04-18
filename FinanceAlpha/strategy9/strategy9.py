import numpy as np
import pandas as pd
import logging
from .iv_surface_model import IVSurfaceFitter
from .gamma_squeeze_predictor import GammaSqueezePredictor
from .dynamic_hedging_strategy import DynamicHedgingStrategy
from .odte_arb_strategy import ODTEArbStrategy

class Strategy9:
    def __init__(self):
        self.iv_fitter = IVSurfaceFitter()
        self.gamma_predictor = GammaSqueezePredictor()
        self.hedging_strategy = DynamicHedgingStrategy()
        self.arb_strategy = ODTEArbStrategy()
        
        # 初始化组件之间的关联
        self.gamma_predictor.set_iv_fitter(self.iv_fitter)
        self.hedging_strategy.set_gamma_predictor(self.gamma_predictor)
        self.arb_strategy.set_iv_fitter(self.iv_fitter)
        
        # 配置日志
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('Strategy9')
    
    def run_strategy(self, option_chain, underlying_price, time_to_expiry):
        """运行完整策略"""
        self.logger.info(f"Running Strategy9 for 0DTE options with underlying price: {underlying_price}")
        
        # 1. 拟合IV曲面
        self.logger.info("Fitting IV surface...")
        self.iv_fitter.fit_surface(option_chain)
        
        # 2. 预测Gamma挤压
        self.logger.info("Predicting gamma squeeze...")
        squeeze_prediction = self.gamma_predictor.predict_gamma_squeeze(
            option_chain, underlying_price, time_to_expiry
        )
        
        # 3. 生成动态对冲策略
        self.logger.info("Generating dynamic hedging strategy...")
        hedging_result = self.hedging_strategy.generate_hedging_strategy(
            option_chain, underlying_price, time_to_expiry
        )
        
        # 4. 识别套利机会
        self.logger.info("Identifying arbitrage opportunities...")
        arb_opportunities = self.arb_strategy.identify_arb_opportunities(
            option_chain, underlying_price, time_to_expiry
        )
        
        # 5. 生成套利投资组合
        self.logger.info("Generating arbitrage portfolio...")
        arb_portfolio = self.arb_strategy.generate_arb_portfolio(arb_opportunities)
        
        # 6. 整合策略结果
        strategy_result = {
            'iv_surface_model': 'Neural Network',
            'gamma_squeeze_prediction': squeeze_prediction,
            'dynamic_hedging_strategy': hedging_result,
            'arbitrage_opportunities': arb_opportunities,
            'arbitrage_portfolio': arb_portfolio,
            'risk_metrics': self.calculate_overall_risk(squeeze_prediction, arb_portfolio)
        }
        
        self.logger.info("Strategy9 execution completed")
        return strategy_result
    
    def calculate_overall_risk(self, squeeze_prediction, arb_portfolio):
        """计算整体风险指标"""
        gamma_risk = squeeze_prediction['max_gamma'] * 10000
        squeeze_risk = squeeze_prediction['squeeze_probability'] * 100
        portfolio_risk = arb_portfolio['total_investment'] * 0.01  # 假设1%的基础风险
        
        overall_risk = {
            'gamma_risk': gamma_risk,
            'squeeze_risk': squeeze_risk,
            'portfolio_risk': portfolio_risk,
            'total_risk': gamma_risk + squeeze_risk + portfolio_risk,
            'risk_score': self.calculate_risk_score(gamma_risk, squeeze_risk, portfolio_risk)
        }
        
        return overall_risk
    
    def calculate_risk_score(self, gamma_risk, squeeze_risk, portfolio_risk):
        """计算风险评分"""
        # 归一化风险值
        gamma_score = min(100, gamma_risk / 100)
        squeeze_score = squeeze_risk
        portfolio_score = min(100, portfolio_risk / 10000)
        
        # 加权平均
        total_score = (gamma_score * 0.4 + squeeze_score * 0.4 + portfolio_score * 0.2)
        
        return total_score
    
    def backtest_strategy(self, historical_data):
        """回测策略"""
        self.logger.info("Starting backtest for Strategy9...")
        
        results = []
        
        for date, data in historical_data.items():
            try:
                option_chain = data['option_chain']
                underlying_price = data['underlying_price']
                time_to_expiry = data['time_to_expiry']
                
                # 运行策略
                strategy_result = self.run_strategy(
                    option_chain, underlying_price, time_to_expiry
                )
                
                # 计算实际收益（模拟）
                actual_return = self.simulate_actual_return(strategy_result, data['next_day_data'])
                
                results.append({
                    'date': date,
                    'squeeze_probability': strategy_result['gamma_squeeze_prediction']['squeeze_probability'],
                    'opportunities_found': len(strategy_result['arbitrage_opportunities']),
                    'total_investment': strategy_result['arbitrage_portfolio']['total_investment'],
                    'expected_return': strategy_result['arbitrage_portfolio']['expected_return'],
                    'actual_return': actual_return,
                    'risk_score': strategy_result['risk_metrics']['risk_score']
                })
                
                self.logger.info(f"Backtest for {date}: Return = {actual_return:.4f}, Risk Score = {strategy_result['risk_metrics']['risk_score']:.2f}")
                
            except Exception as e:
                self.logger.error(f"Error in backtest for {date}: {str(e)}")
                continue
        
        backtest_results = pd.DataFrame(results)
        
        # 计算回测统计指标
        stats = self.calculate_backtest_stats(backtest_results)
        
        self.logger.info("Backtest completed")
        return {
            'results': backtest_results,
            'stats': stats
        }
    
    def simulate_actual_return(self, strategy_result, next_day_data):
        """模拟实际收益"""
        # 简化的收益模拟
        total_profit = 0
        
        # 模拟套利收益
        for item in strategy_result['arbitrage_portfolio']['portfolio']:
            # 假设期权价格变化基于IV变化
            iv_change = np.random.normal(0, 0.02)  # 模拟IV变化
            profit = item['position_size'] * item['market_iv'] * iv_change
            total_profit += profit
        
        # 模拟对冲收益
        hedge_ratio = strategy_result['dynamic_hedging_strategy']['hedge_ratio']
        underlying_change = np.random.normal(0, 0.01)  # 模拟标的价格变化
        hedge_profit = -hedge_ratio * underlying_change * 10000  # 假设对冲头寸
        total_profit += hedge_profit
        
        total_investment = strategy_result['arbitrage_portfolio']['total_investment']
        return total_profit / total_investment if total_investment > 0 else 0
    
    def calculate_backtest_stats(self, backtest_results):
        """计算回测统计指标"""
        if len(backtest_results) == 0:
            return {}
        
        stats = {
            'total_days': len(backtest_results),
            'average_daily_return': backtest_results['actual_return'].mean(),
            'cumulative_return': (1 + backtest_results['actual_return']).prod() - 1,
            'sharpe_ratio': backtest_results['actual_return'].mean() / backtest_results['actual_return'].std() * np.sqrt(252),
            'max_drawdown': self.calculate_max_drawdown(backtest_results['actual_return']),
            'win_rate': (backtest_results['actual_return'] > 0).mean(),
            'average_risk_score': backtest_results['risk_score'].mean()
        }
        
        return stats
    
    def calculate_max_drawdown(self, returns):
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative / peak) - 1
        return drawdown.min()
    
    def set_risk_parameters(self, risk_params):
        """设置风险参数"""
        self.hedging_strategy.set_risk_parameters(risk_params)
        self.logger.info(f"Updated risk parameters: {risk_params}")
    
    def get_strategy_summary(self, strategy_result):
        """获取策略摘要"""
        summary = {
            'gamma_squeeze_probability': strategy_result['gamma_squeeze_prediction']['squeeze_probability'],
            'gamma_peak_strike': strategy_result['gamma_squeeze_prediction']['gamma_peak_strike'],
            'hedge_ratio': strategy_result['dynamic_hedging_strategy']['hedge_ratio'],
            'arbitrage_opportunities': len(strategy_result['arbitrage_opportunities']),
            'total_investment': strategy_result['arbitrage_portfolio']['total_investment'],
            'expected_return': strategy_result['arbitrage_portfolio']['expected_return'],
            'risk_score': strategy_result['risk_metrics']['risk_score']
        }
        
        return summary
import numpy as np
import pandas as pd
from .gamma_squeeze_predictor import GammaSqueezePredictor

class DynamicHedgingStrategy:
    def __init__(self):
        self.gamma_predictor = GammaSqueezePredictor()
        self.positions = {}
        self.risk_parameters = {
            'max_position_size': 1000000,  # 最大持仓规模
            'max_gamma_exposure': 10000,  # 最大Gamma暴露
            'max_vega_exposure': 50000,  # 最大Vega暴露
            'hedge_frequency': 0.1,  # 对冲频率（小时）
            'stop_loss': 0.02,  # 止损比例
            'take_profit': 0.05  # 止盈比例
        }
    
    def generate_hedging_strategy(self, option_chain, underlying_price, time_to_expiry):
        """生成动态对冲策略"""
        # 预测Gamma挤压
        squeeze_prediction = self.gamma_predictor.predict_gamma_squeeze(
            option_chain, underlying_price, time_to_expiry
        )
        
        # 计算最优对冲比率
        hedge_ratio = self.calculate_hedge_ratio(squeeze_prediction, underlying_price)
        
        # 生成对冲策略
        strategy = {
            'hedge_ratio': hedge_ratio,
            'gamma_squeeze_prediction': squeeze_prediction,
            'hedging_actions': self.generate_hedging_actions(squeeze_prediction, underlying_price),
            'risk_management': self.calculate_risk_metrics(squeeze_prediction)
        }
        
        return strategy
    
    def calculate_hedge_ratio(self, squeeze_prediction, underlying_price):
        """计算最优对冲比率"""
        gamma_peak_strike = squeeze_prediction['gamma_peak_strike']
        max_gamma = squeeze_prediction['max_gamma']
        
        # 基于Gamma峰值计算对冲比率
        moneyness = gamma_peak_strike / underlying_price
        
        # 非线性对冲比率计算
        if moneyness > 1.05:
            # 价外期权，对冲比率较低
            hedge_ratio = 0.3 * (1 - (moneyness - 1.05) / 0.1)
        elif moneyness < 0.95:
            # 价内期权，对冲比率较高
            hedge_ratio = 0.8 * (1 - (0.95 - moneyness) / 0.1)
        else:
            # 平值期权，对冲比率最高
            hedge_ratio = 0.6
        
        # 考虑Gamma大小调整对冲比率
        hedge_ratio = min(1.0, hedge_ratio * (1 + max_gamma * 1000))
        
        return hedge_ratio
    
    def generate_hedging_actions(self, squeeze_prediction, underlying_price):
        """生成具体的对冲操作"""
        actions = []
        
        # 基于Gamma挤压预测生成对冲操作
        gamma_peak_strike = squeeze_prediction['gamma_peak_strike']
        critical_strikes = squeeze_prediction['critical_strikes']
        squeeze_prob = squeeze_prediction['squeeze_probability']
        
        # 如果挤压概率高，增加对冲频率和强度
        if squeeze_prob > 0.7:
            # 高概率挤压，采取更积极的对冲策略
            actions.append({
                'action': 'increase_hedge_frequency',
                'frequency': self.risk_parameters['hedge_frequency'] / 2,
                'reason': 'High gamma squeeze probability'
            })
        
        # 针对临界行权价区域进行对冲
        for strike in critical_strikes:
            moneyness = strike / underlying_price
            actions.append({
                'action': 'hedge_strike',
                'strike': strike,
                'moneyness': moneyness,
                'weight': abs(gamma_peak_strike - strike) / gamma_peak_strike
            })
        
        return actions
    
    def calculate_risk_metrics(self, squeeze_prediction):
        """计算风险指标"""
        max_gamma = squeeze_prediction['max_gamma']
        squeeze_prob = squeeze_prediction['squeeze_probability']
        
        # 计算各种风险指标
        risk_metrics = {
            'gamma_risk': max_gamma * 10000,  # 缩放后的Gamma风险
            'squeeze_risk': squeeze_prob * 100,  # 挤压风险百分比
            'VaR': self.calculate_value_at_risk(squeeze_prediction),
            'margin_requirement': self.calculate_margin_requirement(squeeze_prediction)
        }
        
        return risk_metrics
    
    def calculate_value_at_risk(self, squeeze_prediction):
        """计算风险价值"""
        implied_move = squeeze_prediction['implied_move']
        squeeze_prob = squeeze_prediction['squeeze_probability']
        
        # 基于隐含波动和挤压概率计算VaR
        var = implied_move * (1 + squeeze_prob * 2)
        
        return var
    
    def calculate_margin_requirement(self, squeeze_prediction):
        """计算保证金要求"""
        squeeze_prob = squeeze_prediction['squeeze_probability']
        max_gamma = squeeze_prediction['max_gamma']
        
        # 基于挤压概率和Gamma大小计算保证金要求
        margin = 0.1 * (1 + squeeze_prob * 3) * (1 + max_gamma * 10000)
        
        return margin
    
    def update_positions(self, new_positions):
        """更新持仓"""
        self.positions.update(new_positions)
    
    def set_risk_parameters(self, risk_params):
        """设置风险参数"""
        self.risk_parameters.update(risk_params)
    
    def set_gamma_predictor(self, gamma_predictor):
        """设置Gamma预测器"""
        self.gamma_predictor = gamma_predictor
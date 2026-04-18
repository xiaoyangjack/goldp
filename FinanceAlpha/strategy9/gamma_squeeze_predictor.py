import numpy as np
import pandas as pd
from scipy.stats import norm
from .iv_surface_model import IVSurfaceFitter

class GammaSqueezePredictor:
    def __init__(self):
        self.iv_fitter = None
    
    def calculate_greeks(self, S, K, T, r, sigma, option_type='call'):
        """计算期权的Greeks"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == 'call':
            delta = norm.cdf(d1)
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = - (S * sigma * norm.pdf(d1)) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
            vega = S * np.sqrt(T) * norm.pdf(d1)
        else:
            delta = norm.cdf(d1) - 1
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = - (S * sigma * norm.pdf(d1)) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
            vega = S * np.sqrt(T) * norm.pdf(d1)
        
        return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega}
    
    def predict_gamma_squeeze(self, option_chain, underlying_price, time_to_expiry):
        """预测Gamma挤压临界点"""
        # 计算每个期权的Gamma
        gamma_values = []
        strikes = []
        
        for _, option in option_chain.iterrows():
            strike = option['strike']
            iv = option['implied_volatility']
            
            greeks = self.calculate_greeks(
                S=underlying_price,
                K=strike,
                T=time_to_expiry / 365.0,
                r=0.05,  # 无风险利率
                sigma=iv,
                option_type=option['option_type']
            )
            
            gamma_values.append(greeks['gamma'])
            strikes.append(strike)
        
        # 找到Gamma峰值对应的行权价
        gamma_array = np.array(gamma_values)
        strike_array = np.array(strikes)
        
        # 计算Gamma加权平均行权价
        gamma_weighted_strike = np.sum(gamma_array * strike_array) / np.sum(gamma_array)
        
        # 识别Gamma挤压临界点
        gamma_peak_index = np.argmax(gamma_array)
        gamma_peak_strike = strike_array[gamma_peak_index]
        max_gamma = gamma_array[gamma_peak_index]
        
        # 计算Gamma挤压的临界区域
        gamma_threshold = max_gamma * 0.7  # 70%的最大Gamma作为阈值
        critical_strikes = strike_array[gamma_array >= gamma_threshold]
        
        # 预测可能的价格波动范围
        implied_move = iv * underlying_price * np.sqrt(time_to_expiry / 365.0)
        
        return {
            'gamma_peak_strike': gamma_peak_strike,
            'gamma_weighted_strike': gamma_weighted_strike,
            'max_gamma': max_gamma,
            'critical_strikes': critical_strikes,
            'implied_move': implied_move,
            'squeeze_probability': self.calculate_squeeze_probability(gamma_array, time_to_expiry)
        }
    
    def calculate_squeeze_probability(self, gamma_array, time_to_expiry):
        """计算Gamma挤压的概率"""
        # 基于Gamma分布和剩余时间计算挤压概率
        avg_gamma = np.mean(gamma_array)
        max_gamma = np.max(gamma_array)
        gamma_concentration = max_gamma / avg_gamma if avg_gamma > 0 else 0
        
        # 时间衰减因子
        time_factor = np.exp(-5 * time_to_expiry / 365.0)  # 时间越短，挤压概率越高
        
        # 计算挤压概率
        squeeze_prob = min(1.0, gamma_concentration * 0.1 * time_factor)
        
        return squeeze_prob
    
    def set_iv_fitter(self, iv_fitter):
        """设置IV曲面拟合器"""
        self.iv_fitter = iv_fitter
    
    def predict_iv_for_strike(self, strike, underlying_price, time_to_expiry):
        """预测特定行权价的隐含波动率"""
        if not self.iv_fitter:
            raise ValueError("IV surface fitter not set")
        
        moneyness = strike / underlying_price
        return self.iv_fitter.predict_iv(moneyness, time_to_expiry, underlying_price)
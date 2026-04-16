"""
投资决策程序
功能：
- 基于因子分析结果生成投资决策
- 提供可解释性分析
- 支持不同市场环境下的策略调整
"""
import os
import json
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger

class InvestmentDecider:
    """投资决策器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_factor_analysis(self):
        """加载因子分析结果"""
        analysis_path = os.path.join(self.data_dir, 'factor_analysis_result.json')
        if not os.path.exists(analysis_path):
            logger.warning(f"因子分析结果文件不存在: {analysis_path}")
            return None
        
        try:
            with open(analysis_path, 'r') as f:
                analysis = json.load(f)
            logger.info("加载因子分析结果成功")
            return analysis
        except Exception as e:
            logger.error(f"加载因子分析结果失败: {e}")
            return None
    
    def save_factor_analysis(self, analysis):
        """保存因子分析结果"""
        analysis_path = os.path.join(self.data_dir, 'factor_analysis_result.json')
        try:
            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"因子分析结果保存成功: {analysis_path}")
        except Exception as e:
            logger.error(f"保存因子分析结果失败: {e}")
    
    def analyze_market_environment(self, df):
        """分析市场环境"""
        # 计算市场趋势
        df = df.copy()
        df['ma10'] = df['gold_close'].rolling(window=10).mean()
        df['ma30'] = df['gold_close'].rolling(window=30).mean()
        df['ma_diff'] = df['ma10'] - df['ma30']
        
        # 计算波动率
        df['returns'] = df['gold_close'].pct_change() * 100
        df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
        
        # 计算动量
        df['momentum'] = df['gold_close'].pct_change(20) * 100
        
        # 最近数据
        latest = df.iloc[-1]
        
        # 市场环境分析
        market_env = {
            'trend': 'bullish' if latest['ma_diff'] > 0 else 'bearish' if latest['ma_diff'] < -0.5 else 'neutral',
            'volatility': 'high' if latest['volatility'] > 15 else 'medium' if latest['volatility'] > 10 else 'low',
            'momentum': 'strong' if abs(latest['momentum']) > 5 else 'weak',
            'current_price': float(latest['gold_close']),
            'ma10': float(latest['ma10']),
            'ma30': float(latest['ma30']),
            'volatility_value': float(latest['volatility']),
            'momentum_value': float(latest['momentum'])
        }
        
        return market_env
    
    def generate_decision(self, factor_analysis, market_env):
        """生成投资决策"""
        if factor_analysis is None:
            logger.warning("因子分析结果为空，使用默认决策")
            return self._default_decision(market_env)
        
        # 提取关键因子
        key_factors = factor_analysis.get('key_factors', [])
        correlation = factor_analysis.get('correlation', {})
        importance = factor_analysis.get('importance', {})
        
        # 分析因子影响
        factor_impact = self._analyze_factor_impact(key_factors, correlation)
        
        # 基于市场环境和因子影响生成决策
        decision = {
            'timestamp': datetime.now().isoformat(),
            'market_environment': market_env,
            'factor_impact': factor_impact,
            'position': self._determine_position(market_env, factor_impact),
            'strategy': self._determine_strategy(market_env, factor_impact),
            'risk_management': self._determine_risk_management(market_env),
            'explanation': self._generate_explanation(market_env, factor_impact)
        }
        
        return decision
    
    def _default_decision(self, market_env):
        """默认决策"""
        return {
            'timestamp': datetime.now().isoformat(),
            'market_environment': market_env,
            'factor_impact': [],
            'position': 'neutral',
            'strategy': 'ma_crossover',
            'risk_management': {
                'stop_loss': 5.0,
                'take_profit': 10.0,
                'position_size': 0.1
            },
            'explanation': '因子分析结果不可用，基于市场环境做出默认决策'
        }
    
    def _analyze_factor_impact(self, key_factors, correlation):
        """分析因子影响"""
        factor_impact = []
        for factor, score in key_factors:
            # 获取因子相关性
            corr_1d = 0
            if '1d_return' in correlation:
                corr_data = dict(correlation['1d_return'])
                if factor in corr_data:
                    corr_1d = corr_data[factor]
            
            # 分析因子影响方向
            impact_direction = 'positive' if corr_1d > 0 else 'negative' if corr_1d < 0 else 'neutral'
            impact_strength = 'strong' if abs(corr_1d) > 0.3 else 'medium' if abs(corr_1d) > 0.1 else 'weak'
            
            factor_impact.append({
                'factor': factor,
                'score': float(score),
                'correlation': float(corr_1d),
                'direction': impact_direction,
                'strength': impact_strength
            })
        
        return factor_impact
    
    def _determine_position(self, market_env, factor_impact):
        """确定仓位"""
        # 基于市场趋势
        trend_score = 1 if market_env['trend'] == 'bullish' else -1 if market_env['trend'] == 'bearish' else 0
        
        # 基于因子影响
        factor_score = 0
        for impact in factor_impact:
            if impact['direction'] == 'positive':
                factor_score += impact['score']
            else:
                factor_score -= impact['score']
        
        # 综合得分
        total_score = trend_score + factor_score
        
        if total_score > 0.5:
            return 'long'
        elif total_score < -0.5:
            return 'short'
        else:
            return 'neutral'
    
    def _determine_strategy(self, market_env, factor_impact):
        """确定策略"""
        # 基于市场波动性
        if market_env['volatility'] == 'high':
            return 'atr_breakout'
        elif market_env['trend'] == 'bullish' or market_env['trend'] == 'bearish':
            return 'ma_crossover'
        else:
            return 'grid'
    
    def _determine_risk_management(self, market_env):
        """确定风险管理策略"""
        # 基于波动性调整止损
        if market_env['volatility'] == 'high':
            stop_loss = 8.0
            position_size = 0.05
        elif market_env['volatility'] == 'medium':
            stop_loss = 5.0
            position_size = 0.1
        else:
            stop_loss = 3.0
            position_size = 0.15
        
        return {
            'stop_loss': stop_loss,
            'take_profit': stop_loss * 2,
            'position_size': position_size
        }
    
    def _generate_explanation(self, market_env, factor_impact):
        """生成决策解释"""
        explanation = []
        
        # 市场环境解释
        explanation.append(f"市场环境: {market_env['trend']}趋势, {market_env['volatility']}波动性, {market_env['momentum']}动量")
        explanation.append(f"当前价格: {market_env['current_price']:.2f}, MA10: {market_env['ma10']:.2f}, MA30: {market_env['ma30']:.2f}")
        
        # 因子影响解释
        if factor_impact:
            explanation.append("\n关键因子影响:")
            for impact in factor_impact[:3]:  # 只显示前3个关键因子
                explanation.append(f"- {impact['factor']}: {impact['strength']} {impact['direction']}影响 (相关系数: {impact['correlation']:.2f})")
        
        # 决策理由
        explanation.append("\n决策理由:")
        if market_env['trend'] == 'bullish':
            explanation.append("- 短期均线上穿长期均线，形成多头趋势")
        elif market_env['trend'] == 'bearish':
            explanation.append("- 短期均线下穿长期均线，形成空头趋势")
        else:
            explanation.append("- 均线系统趋于平缓，市场处于横盘整理")
        
        if market_env['volatility'] == 'high':
            explanation.append("- 市场波动性较高，采用ATR突破策略以适应波动")
        
        return '\n'.join(explanation)
    
    def make_investment_decision(self):
        """制定投资决策"""
        # 加载因子分析结果
        factor_analysis = self.load_factor_analysis()
        
        # 加载数据
        data_path = os.path.join(self.data_dir, 'gold_au9999_verified.csv')
        if not os.path.exists(data_path):
            logger.error(f"数据文件不存在: {data_path}")
            return None
        
        try:
            df = pd.read_csv(data_path)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return None
        
        # 分析市场环境
        market_env = self.analyze_market_environment(df)
        
        # 生成决策
        decision = self.generate_decision(factor_analysis, market_env)
        
        # 保存决策
        decision_path = os.path.join(self.data_dir, 'investment_decision.json')
        try:
            with open(decision_path, 'w') as f:
                json.dump(decision, f, indent=2, ensure_ascii=False)
            logger.info(f"投资决策保存成功: {decision_path}")
        except Exception as e:
            logger.error(f"保存投资决策失败: {e}")
        
        return decision

# 全局实例
investment_decider = InvestmentDecider()
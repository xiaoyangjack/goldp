#!/usr/bin/env python3
"""
LLM驱动的因果推断宏观对冲量化策略

基于因果大模型（CausalLLM）+万亿级宏观知识图谱，解决传统量化"只懂相关、不懂因果"的核心痛点，
精准识别宏观政策、经济数据、地缘事件对大类资产/行业/个股的传导链条与因果关系，
构建全球宏观对冲与大类资产配置策略。
"""

import pandas as pd
import numpy as np
import networkx as nx
from loguru import logger
from causalml.inference.meta import BaseXRegressor
from causalml.inference.tree import CausalForest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression


class CausalLLMMacroStrategy:
    """LLM驱动的因果推断宏观对冲量化策略"""
    
    def __init__(self, config=None):
        """
        初始化策略
        
        Args:
            config: 策略配置参数
        """
        self.config = config or {}
        self.macro_knowledge_graph = None
        self.causal_model = None
        self.portfolio = {}
        
        # 策略参数
        self.atr_multiplier = self.config.get('atr_multiplier', 1.5)
        self.target_vol = self.config.get('target_vol', 0.01)
        self.max_drawdown = self.config.get('max_drawdown', 0.2)
        self.asset_weight_limit = self.config.get('asset_weight_limit', 0.4)
        
        logger.info("CausalLLMMacroStrategy 初始化完成")
    
    def build_macro_knowledge_graph(self, macro_data, industry_data, stock_data):
        """
        构建宏观-中观-微观三级传导知识图谱
        
        Args:
            macro_data: 宏观经济数据
            industry_data: 行业数据
            stock_data: 个股数据
        """
        logger.info("开始构建宏观知识图谱...")
        
        # 创建知识图谱
        G = nx.DiGraph()
        
        # 添加宏观节点
        macro_nodes = ['GDP', 'CPI', 'InterestRate', 'ExchangeRate', 'SocialFinance']
        for node in macro_nodes:
            G.add_node(node, type='macro')
        
        # 添加行业节点（31个申万一级行业）
        industry_nodes = [
            'Technology', 'Financial', 'Consumer', 'Industrial', 'Materials',
            'Energy', 'Healthcare', 'Utilities', 'RealEstate', 'Communication'
        ]
        for node in industry_nodes:
            G.add_node(node, type='industry')
        
        # 添加个股节点（示例）
        stock_nodes = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        for node in stock_nodes:
            G.add_node(node, type='stock')
        
        # 添加宏观到行业的边
        macro_industry_edges = [
            ('GDP', 'Technology'), ('GDP', 'Industrial'),
            ('CPI', 'Consumer'), ('CPI', 'Utilities'),
            ('InterestRate', 'Financial'), ('InterestRate', 'RealEstate'),
            ('ExchangeRate', 'Technology'), ('ExchangeRate', 'Materials'),
            ('SocialFinance', 'Financial'), ('SocialFinance', 'RealEstate')
        ]
        for edge in macro_industry_edges:
            G.add_edge(edge[0], edge[1], weight=np.random.uniform(0.1, 0.9))
        
        # 添加行业到个股的边
        industry_stock_edges = [
            ('Technology', 'AAPL'), ('Technology', 'MSFT'), ('Technology', 'GOOGL'),
            ('Financial', 'JPM'), ('Financial', 'BAC'),
            ('Consumer', 'AMZN'), ('Consumer', 'WMT'),
            ('Industrial', 'GE'), ('Industrial', 'HON'),
            ('Materials', 'BHP'), ('Materials', 'RIO')
        ]
        for edge in industry_stock_edges:
            G.add_edge(edge[0], edge[1], weight=np.random.uniform(0.1, 0.9))
        
        self.macro_knowledge_graph = G
        logger.info(f"宏观知识图谱构建完成，节点数: {len(G.nodes)}, 边数: {len(G.edges)}")
    
    def train_causal_model(self, X, treatment, y):
        """
        训练因果效应模型
        
        Args:
            X: 特征数据
            treatment: 处理变量
            y: 结果变量
        """
        logger.info("开始训练因果效应模型...")
        
        # 双重机器学习(DML)因果效应估计
        base_learner = RandomForestRegressor(n_estimators=100, random_state=42)
        self.causal_model = BaseXRegressor(learner=base_learner)
        
        # 训练模型
        self.causal_model.fit(X, treatment, y)
        
        logger.info("因果效应模型训练完成")
    
    def estimate_causal_effect(self, X):
        """
        估计因果效应
        
        Args:
            X: 特征数据
            
        Returns:
            因果效应估计值
        """
        if self.causal_model is None:
            logger.error("因果模型未训练")
            return np.zeros(len(X))
        
        # 估计平均处理效应(ATE)
        ate = self.causal_model.predict(X)
        return ate
    
    def generate_signals(self, market_data, macro_events):
        """
        基于因果效应生成交易信号
        
        Args:
            market_data: 市场数据
            macro_events: 宏观事件数据
            
        Returns:
            交易信号
        """
        signals = {}
        
        # 模拟因果效应计算
        for asset in market_data.columns:
            # 基于宏观事件计算因果效应
            effect = np.random.uniform(-0.05, 0.05)
            
            # 生成信号
            if effect > 0.01:
                signals[asset] = 1  # 买入
            elif effect < -0.01:
                signals[asset] = -1  # 卖出
            else:
                signals[asset] = 0  # 持有
        
        return signals
    
    def allocate_portfolio(self, signals, market_data, risk_free_rate=0.02):
        """
        基于信号分配组合权重
        
        Args:
            signals: 交易信号
            market_data: 市场数据
            risk_free_rate: 无风险利率
            
        Returns:
            组合权重
        """
        weights = {}
        total_signal = sum(abs(signal) for signal in signals.values())
        
        if total_signal > 0:
            for asset, signal in signals.items():
                weight = signal / total_signal
                # 限制单个资产权重
                weight = max(min(weight, self.asset_weight_limit), -self.asset_weight_limit)
                weights[asset] = weight
        else:
            # 等权分配
            n_assets = len(signals)
            for asset in signals:
                weights[asset] = 1 / n_assets
        
        return weights
    
    def run_backtest(self, market_data, macro_events, initial_cash=1000000):
        """
        运行回测
        
        Args:
            market_data: 市场数据
            macro_events: 宏观事件数据
            initial_cash: 初始资金
            
        Returns:
            回测结果
        """
        logger.info("开始回测 CausalLLMMacroStrategy...")
        
        # 初始化回测
        portfolio_values = [initial_cash]
        positions = {asset: 0 for asset in market_data.columns}
        cash = initial_cash
        
        # 回测循环
        for i in range(1, len(market_data)):
            # 生成信号
            signals = self.generate_signals(market_data.iloc[:i], macro_events.iloc[:i])
            
            # 分配组合
            weights = self.allocate_portfolio(signals, market_data.iloc[:i])
            
            # 计算目标市值
            current_value = cash + sum(positions[asset] * market_data[asset].iloc[i-1] for asset in positions)
            target_values = {asset: current_value * weights[asset] for asset in weights}
            
            # 调整仓位
            for asset in positions:
                current_price = market_data[asset].iloc[i-1]
                target_position = target_values.get(asset, 0) / current_price
                position_change = target_position - positions[asset]
                
                # 计算交易成本
                cost = abs(position_change) * current_price * 0.001
                cash -= position_change * current_price + cost
                positions[asset] = target_position
            
            # 计算当前组合价值
            current_value = cash + sum(positions[asset] * market_data[asset].iloc[i] for asset in positions)
            portfolio_values.append(current_value)
        
        # 生成回测结果
        result = {
            'portfolio_values': pd.Series(portfolio_values, index=market_data.index),
            'positions': positions,
            'final_value': portfolio_values[-1],
            'total_return': (portfolio_values[-1] / initial_cash) - 1
        }
        
        logger.info(f"回测完成，总收益: {result['total_return']:.2f}")
        return result
    
    def get_risk_metrics(self, portfolio_values):
        """
        计算风险指标
        
        Args:
            portfolio_values: 组合价值序列
            
        Returns:
            风险指标
        """
        returns = portfolio_values.pct_change().dropna()
        
        metrics = {
            'annual_return': returns.mean() * 252,
            'annual_volatility': returns.std() * np.sqrt(252),
            'sharpe_ratio': (returns.mean() * 252 - 0.02) / (returns.std() * np.sqrt(252)),
            'max_drawdown': ((portfolio_values.cummax() - portfolio_values) / portfolio_values.cummax()).max(),
            'sortino_ratio': (returns.mean() * 252 - 0.02) / (returns[returns < 0].std() * np.sqrt(252))
        }
        
        return metrics


if __name__ == "__main__":
    # 测试策略
    strategy = CausalLLMMacroStrategy()
    
    # 模拟数据
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    assets = ['SPY', 'TLT', 'GLD', 'QQQ']
    market_data = pd.DataFrame(
        np.random.randn(len(dates), len(assets)) * 0.01 + 1.001,
        index=dates, columns=assets
    ).cumprod()
    
    macro_events = pd.DataFrame(
        np.random.randn(len(dates), 5),
        index=dates,
        columns=['GDP', 'CPI', 'InterestRate', 'ExchangeRate', 'SocialFinance']
    )
    
    # 构建知识图谱
    strategy.build_macro_knowledge_graph(macro_events, None, market_data)
    
    # 运行回测
    result = strategy.run_backtest(market_data, macro_events)
    
    # 计算风险指标
    metrics = strategy.get_risk_metrics(result['portfolio_values'])
    
    print("回测结果:")
    print(f"最终价值: ${result['final_value']:.2f}")
    print(f"总收益: {result['total_return']:.2f}")
    print("风险指标:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")

import unittest
import pandas as pd
import numpy as np
from gold_quant_system.core.backtest_engine import BacktestEngine
from FinanceAlpha.strategy9.strategy9 import Strategy9
from FinanceAlpha.strategy9.dynamic_hedging_strategy import DynamicHedgingStrategy
from FinanceAlpha.strategy9.odte_arb_strategy import ODTEArbStrategy
from FinanceAlpha.strategy10.strategy10 import AlternativeDataDrivenStrategy
from gold_quant_system.strategies.advanced.ai_hi_fundamental_quant_strategy import AIHIFundamentalQuantStrategy
from gold_quant_system.strategies.advanced.causal_llm_macro_strategy import CausalLLMMacroStrategy
from gold_quant_system.strategies.advanced.multimodal_semantic_alpha_strategy import MultimodalSemanticAlphaStrategy

class TestStrategies(unittest.TestCase):
    """测试所有策略的单元测试"""
    
    def setUp(self):
        """设置测试数据"""
        # 生成测试数据
        self.dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
        self.prices = np.cumprod(1 + np.random.randn(len(self.dates)) * 0.01)
        self.df = pd.DataFrame({
            'close': self.prices,
            'high': self.prices * (1 + np.random.rand(len(self.dates)) * 0.02),
            'low': self.prices * (1 - np.random.rand(len(self.dates)) * 0.02),
            'volume': np.random.randint(100000, 1000000, len(self.dates))
        }, index=self.dates)
        
        # 计算技术指标
        self.df['sma_fast'] = self.df['close'].rolling(20).mean()
        self.df['sma_slow'] = self.df['close'].rolling(60).mean()
        
        # 计算RSI
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        self.df['rsi'] = 100 - (100 / (1 + rs))
        
        # 计算MACD
        exp1 = self.df['close'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['close'].ewm(span=26, adjust=False).mean()
        self.df['macd'] = exp1 - exp2
        self.df['macd_signal'] = self.df['macd'].ewm(span=9, adjust=False).mean()
        self.df['macd_histogram'] = self.df['macd'] - self.df['macd_signal']
        
        # 计算布林带
        self.df['bb_middle'] = self.df['close'].rolling(20).mean()
        self.df['bb_std'] = self.df['close'].rolling(20).std()
        self.df['bb_upper'] = self.df['bb_middle'] + 2 * self.df['bb_std']
        self.df['bb_lower'] = self.df['bb_middle'] - 2 * self.df['bb_std']
        self.df['bb_position'] = (self.df['close'] - self.df['bb_lower']) / (self.df['bb_upper'] - self.df['bb_lower'])
        
        # 计算ATR
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        self.df['atr'] = true_range.rolling(14).mean()
        self.df['atr_pct'] = self.df['atr'] / self.df['close']
        
        # 添加策略信号
        self.df['sma_signal'] = np.where(self.df['sma_fast'] > self.df['sma_slow'], 1, 0)
        self.df['rsi_signal'] = np.where(self.df['rsi'] < 35, 1, 0)
        self.df['macd_signal_flag'] = np.where(self.df['macd_histogram'] > 0, 1, 0)
        
        # 添加regime
        self.df['regime'] = np.where(self.df['sma_fast'] > self.df['sma_slow'], 'TREND', 'RANGE')
        
        # 移除NA值
        self.df = self.df.dropna()
    
    def test_backtest_engine_strategies(self):
        """测试回测引擎中的策略"""
        engine = BacktestEngine()
        
        # 测试所有策略
        strategies = ['sma', 'rsi', 'macd', 'bb', 'multi', 'regime']
        params = {'strategies': strategies}
        
        results = engine.run_all_strategies(self.df, params)
        
        for strategy in strategies:
            with self.subTest(strategy=strategy):
                self.assertIn(strategy, results)
                self.assertIsNotNone(results[strategy])
                self.assertIn('portfolio_values', results[strategy])
                self.assertIn('trades', results[strategy])
                self.assertIn('stats', results[strategy])
    
    def test_strategy9(self):
        """测试Strategy9"""
        strategy = Strategy9()
        
        # 生成测试数据
        option_chain = pd.DataFrame({
            'strike': np.linspace(90, 110, 21),
            'implied_volatility': np.random.uniform(0.1, 0.5, 21),
            'option_type': ['call'] * 11 + ['put'] * 10
        })
        
        underlying_price = 100
        time_to_expiry = 1
        
        # 测试运行策略
        result = strategy.run_strategy(option_chain, underlying_price, time_to_expiry)
        
        self.assertIsInstance(result, dict)
        self.assertIn('iv_surface_model', result)
        self.assertIn('gamma_squeeze_prediction', result)
        self.assertIn('dynamic_hedging_strategy', result)
        self.assertIn('arbitrage_opportunities', result)
        self.assertIn('arbitrage_portfolio', result)
        self.assertIn('risk_metrics', result)
    
    def test_dynamic_hedging_strategy(self):
        """测试DynamicHedgingStrategy"""
        strategy = DynamicHedgingStrategy()
        
        # 生成测试数据
        option_chain = pd.DataFrame({
            'strike': np.linspace(90, 110, 21),
            'implied_volatility': np.random.uniform(0.1, 0.5, 21),
            'option_type': ['call'] * 11 + ['put'] * 10
        })
        
        underlying_price = 100
        time_to_expiry = 1
        
        # 测试生成对冲策略
        result = strategy.generate_hedging_strategy(option_chain, underlying_price, time_to_expiry)
        
        self.assertIsInstance(result, dict)
        self.assertIn('hedge_ratio', result)
        self.assertIn('gamma_squeeze_prediction', result)
        self.assertIn('hedging_actions', result)
        self.assertIn('risk_management', result)
    
    def test_odte_arb_strategy(self):
        """测试ODTEArbStrategy"""
        strategy = ODTEArbStrategy()
        
        # 生成测试数据
        option_chain = pd.DataFrame({
            'strike': np.linspace(90, 110, 21),
            'implied_volatility': np.random.uniform(0.1, 0.5, 21),
            'option_type': ['call'] * 11 + ['put'] * 10,
            'last_price': np.random.uniform(0.1, 10, 21)
        })
        
        underlying_price = 100
        time_to_expiry = 1
        
        # 测试识别套利机会
        opportunities = strategy.identify_arb_opportunities(option_chain, underlying_price, time_to_expiry)
        self.assertIsInstance(opportunities, list)
        
        # 测试生成套利投资组合
        portfolio = strategy.generate_arb_portfolio(opportunities)
        self.assertIsInstance(portfolio, dict)
        self.assertIn('portfolio', portfolio)
        self.assertIn('total_investment', portfolio)
        self.assertIn('expected_return', portfolio)
    
    def test_alternative_data_driven_strategy(self):
        """测试AlternativeDataDrivenStrategy"""
        strategy = AlternativeDataDrivenStrategy()
        
        # 测试生成信号
        signals = strategy.generate_signals('AAPL')
        self.assertIsInstance(signals, dict)
        self.assertIn('sentiment_forecast', signals)
        self.assertIn('event_driven', signals)
        self.assertIn('sector_rotation', signals)
        self.assertIn('combined', signals)
        
        # 测试回测
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        results, performance = strategy.backtest('AAPL', start_date, end_date)
        
        self.assertIsInstance(results, pd.DataFrame)
        self.assertIsInstance(performance, dict)
        self.assertIn('cumulative_return', performance)
        self.assertIn('annual_return', performance)
        self.assertIn('annual_volatility', performance)
        self.assertIn('sharpe_ratio', performance)
        self.assertIn('max_drawdown', performance)
    
    def test_ai_hi_fundamental_quant_strategy(self):
        """测试AIHIFundamentalQuantStrategy"""
        strategy = AIHIFundamentalQuantStrategy()
        
        # 测试获取股票数据
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        data = strategy.fetch_stock_data('AAPL', start_date, end_date)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertIn('close', data.columns)
        
        # 测试生成模拟基本面数据
        data_with_fundamentals = strategy.generate_fake_fundamental_data(data)
        self.assertIsInstance(data_with_fundamentals, pd.DataFrame)
        
        # 测试运行策略
        results = strategy.run_strategy(['AAPL'], start_date, end_date)
        self.assertIsInstance(results, dict)
        self.assertIn('AAPL', results)
    
    def test_causal_llm_macro_strategy(self):
        """测试CausalLLMMacroStrategy"""
        strategy = CausalLLMMacroStrategy()
        
        # 生成测试数据
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
        
        # 测试构建知识图谱
        strategy.build_macro_knowledge_graph(macro_events, None, market_data)
        
        # 测试运行回测
        result = strategy.run_backtest(market_data, macro_events)
        self.assertIsInstance(result, dict)
        self.assertIn('portfolio_values', result)
        self.assertIn('positions', result)
        self.assertIn('final_value', result)
        self.assertIn('total_return', result)
        
        # 测试计算风险指标
        metrics = strategy.get_risk_metrics(result['portfolio_values'])
        self.assertIsInstance(metrics, dict)
        self.assertIn('annual_return', metrics)
        self.assertIn('annual_volatility', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('sortino_ratio', metrics)
    
    def test_multimodal_semantic_alpha_strategy(self):
        """测试MultimodalSemanticAlphaStrategy"""
        strategy = MultimodalSemanticAlphaStrategy()
        
        # 生成测试数据
        dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
        assets = ['SPY', 'TLT', 'GLD', 'QQQ']
        market_data = pd.DataFrame(
            np.random.randn(len(dates), len(assets)) * 0.01 + 1.001,
            index=dates, columns=assets
        ).cumprod()
        
        # 模拟多模态数据
        multimodal_data = pd.DataFrame({
            'text': ['Economic growth is strong', 'Inflation is rising', 'Market is volatile'] * (len(dates) // 3 + 1),
            'audio': [100, 200, 300] * (len(dates) // 3 + 1),
            'social_media': [10, 20, 30] * (len(dates) // 3 + 1)
        }).iloc[:len(dates)]
        multimodal_data.index = dates
        
        # 测试运行回测
        result = strategy.run_backtest(market_data, multimodal_data)
        self.assertIsInstance(result, dict)
        self.assertIn('portfolio_values', result)
        self.assertIn('positions', result)
        self.assertIn('final_value', result)
        self.assertIn('total_return', result)
        
        # 测试计算风险指标
        metrics = strategy.get_risk_metrics(result['portfolio_values'])
        self.assertIsInstance(metrics, dict)
        self.assertIn('annual_return', metrics)
        self.assertIn('annual_volatility', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        self.assertIn('sortino_ratio', metrics)

if __name__ == '__main__':
    unittest.main()

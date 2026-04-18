# 测试策略10

import unittest
from datetime import datetime, timedelta
from FinanceAlpha.strategy10.strategy10 import AlternativeDataDrivenStrategy

class TestAlternativeDataDrivenStrategy(unittest.TestCase):
    """测试另类数据驱动的事件驱动量化策略"""
    
    def setUp(self):
        """设置测试环境"""
        self.strategy = AlternativeDataDrivenStrategy()
        self.ticker = 'AAPL'
    
    def test_generate_signals(self):
        """测试生成信号"""
        signals = self.strategy.generate_signals(self.ticker)
        
        # 验证信号结构
        self.assertIn('sentiment_forecast', signals)
        self.assertIn('event_driven', signals)
        self.assertIn('sector_rotation', signals)
        self.assertIn('combined', signals)
        
        # 验证信号类型
        self.assertIn(signals['sentiment_forecast']['signal'], ['BUY', 'SELL', 'HOLD'])
        self.assertIn(signals['event_driven']['signal'], ['BUY', 'SELL', 'HOLD'])
        self.assertIn(signals['combined']['signal'], ['BUY', 'SELL', 'HOLD'])
        
        # 验证置信度
        self.assertGreaterEqual(signals['sentiment_forecast']['confidence'], 0)
        self.assertLessEqual(signals['sentiment_forecast']['confidence'], 1)
        self.assertGreaterEqual(signals['event_driven']['confidence'], 0)
        self.assertLessEqual(signals['event_driven']['confidence'], 1)
        self.assertGreaterEqual(signals['combined']['confidence'], 0)
        self.assertLessEqual(signals['combined']['confidence'], 1)
        
        print("✓ Signal generation test passed")
    
    def test_backtest(self):
        """测试回测功能"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        results, performance = self.strategy.backtest(self.ticker, start_date, end_date)
        
        # 验证回测结果
        self.assertIsInstance(results, type({}))
        self.assertIsInstance(performance, dict)
        
        # 验证性能指标
        self.assertIn('cumulative_return', performance)
        self.assertIn('annual_return', performance)
        self.assertIn('annual_volatility', performance)
        self.assertIn('sharpe_ratio', performance)
        self.assertIn('max_drawdown', performance)
        
        print("✓ Backtest test passed")
    
    def test_run_strategy(self):
        """测试运行策略"""
        signals = self.strategy.run_strategy(self.ticker)
        
        # 验证信号结构
        self.assertIn('sentiment_forecast', signals)
        self.assertIn('event_driven', signals)
        self.assertIn('sector_rotation', signals)
        self.assertIn('combined', signals)
        
        print("✓ Run strategy test passed")
    
    def test_run_backtest(self):
        """测试运行回测"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        results, performance = self.strategy.run_backtest(self.ticker, start_date, end_date)
        
        # 验证回测结果
        self.assertIsInstance(results, type({}))
        self.assertIsInstance(performance, dict)
        
        print("✓ Run backtest test passed")

if __name__ == '__main__':
    unittest.main()
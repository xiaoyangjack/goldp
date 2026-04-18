# 运行策略10

from datetime import datetime, timedelta
from FinanceAlpha.strategy10.strategy10 import AlternativeDataDrivenStrategy

# 初始化策略
strategy = AlternativeDataDrivenStrategy()

# 运行策略
ticker = 'AAPL'
print("=== Running Strategy 10 for", ticker, "===")
signals = strategy.run_strategy(ticker)

# 运行回测
print("\n=== Running Backtest ===")
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
results, performance = strategy.run_backtest(ticker, start_date, end_date)

print("\n=== Strategy 10 Test Completed ===")
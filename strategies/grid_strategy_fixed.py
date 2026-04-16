"""
固定网格交易策略回测
使用Backtrader进行回测

策略逻辑:
- 在中心价格上下设置多个网格
- 价格每触及一个网格，进行买入或卖出
- 固定网格间距，不随波动率变化
"""
import backtrader as bt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

class FixedGridStrategy(bt.Strategy):
    """固定网格策略"""

    params = (
        ('grid_size', 10),        # 网格数量
        ('grid_spacing', 15.0),  # 网格间距（元）
        ('position_size', 100),  # 每格交易量（克）
        ('printlog', False),
    )

    def __init__(self):
        self.grid_levels = []  # 网格价格水平
        self.grid_orders = {}  # 记录每个网格的订单
        self.trade_log = []   # 交易日志
        self.last_price = None

    def notify_order(self, order):
        """订单通知"""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.trade_log.append({
                    'date': self.datas[0].datetime.date(0),
                    'type': 'BUY',
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.value
                })
            elif order.issell():
                self.trade_log.append({
                    'date': self.datas[0].datetime.date(0),
                    'type': 'SELL',
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.value
                })

    def next(self):
        """每个Bar执行一次"""
        current_price = self.datas[0].close[0]
        current_date = self.datas[0].datetime.date(0)

        # 初始化网格（在第一根K线设置网格）
        if not self.grid_levels:
            center = current_price
            self.grid_levels = [
                center + (i - self.params.grid_size // 2) * self.params.grid_spacing
                for i in range(self.params.grid_size)
            ]
            self.grid_levels.sort()
            print(f"[{current_date}] 初始化网格，中心价: {center:.2f}")
            print(f"网格水平: {[f'{g:.2f}' for g in self.grid_levels]}")

        # 检查价格是否触及网格
        for i, level in enumerate(self.grid_levels):
            # 价格从下方触及网格 - 买入
            if self.last_price is not None and self.last_price < level <= current_price:
                if self.position.size < self.params.position_size * self.params.grid_size:
                    self.buy(size=self.params.position_size)
                    print(f"[{current_date}] 买入@{level:.2f}, 当前持仓: {self.position.size + self.params.position_size}")

            # 价格从上方触及网格 - 卖出
            elif self.last_price is not None and self.last_price > level >= current_price:
                if self.position.size >= self.params.position_size:
                    self.sell(size=self.params.position_size)
                    print(f"[{current_date}] 卖出@{level:.2f}, 当前持仓: {self.position.size - self.params.position_size}")

        self.last_price = current_price

    def stop(self):
        """回测结束时"""
        if self.params.printlog:
            print(f'回测结束，最终持仓: {self.position.size}')


def run_backtest():
    """运行回测"""
    print("=" * 60)
    print("固定网格策略回测")
    print("=" * 60)

    # 读取数据
    data_path = 'data/gold_au9999_daily.csv'
    if not os.path.exists(data_path):
        print(f"错误: 数据文件 {data_path} 不存在")
        return

    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])

    # Backtrader需要date, open, high, low, close, volume列
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
    })

    if 'Volume' not in df.columns:
        df['Volume'] = 1000000  # 添加默认成交量

    df = df[['date', 'Open', 'High', 'Low', 'Close', 'Volume']]

    # 只使用2024-2025年数据进行回测
    df = df[(df['date'] >= '2024-01-01') & (df['date'] <= '2025-12-31')]

    print(f"\n回测数据范围: {df['date'].min()} ~ {df['date'].max()}")
    print(f"数据条数: {len(df)}")

    # 创建Cerebro引擎
    cerebro = bt.Cerebro()

    # 添加数据
    data = bt.feeds.PandasData(dataname=df, datetime='date')
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(FixedGridStrategy, printlog=False)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)  # 10万初始资金

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # 运行回测
    print(f"\n初始资金: ¥{cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    strat = results[0]

    print(f"最终资金: ¥{cerebro.broker.getvalue():,.2f}")

    # 计算收益
    initial_value = 100000.0
    final_value = cerebro.broker.getvalue()
    total_return = (final_value - initial_value) / initial_value * 100

    print(f"总收益率: {total_return:.2f}%")

    # 获取分析结果
    try:
        sharpe = strat.analyzers.sharpe.get_analysis()
        print(f"夏普比率: {sharpe.get('sharperatio', 'N/A')}")
    except:
        print("夏普比率: N/A")

    try:
        drawdown = strat.analyzers.drawdown.get_analysis()
        print(f"最大回撤: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
    except:
        print("最大回撤: N/A")

    try:
        trades = strat.analyzers.trades.get_analysis()
        total_trades = trades.get('total', {}).get('total', 0)
        won_trades = trades.get('won', {}).get('total', 0)
        lost_trades = trades.get('lost', {}).get('total', 0)
        win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0

        print(f"总交易次数: {total_trades}")
        print(f"盈利交易: {won_trades}")
        print(f"亏损交易: {lost_trades}")
        print(f"胜率: {win_rate:.2f}%")
    except:
        print("交易统计: N/A")

    # 保存回测结果
    save_results(initial_value, final_value, total_return, strat.trade_log)

    return {
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': total_return,
        'trade_log': strat.trade_log
    }


def save_results(initial_value, final_value, total_return, trade_log):
    """保存回测结果"""
    os.makedirs('backtest', exist_ok=True)

    # 保存交易日志
    if trade_log:
        trades_df = pd.DataFrame(trade_log)
        trades_df.to_csv('backtest/fixed_grid_trades.csv', index=False, encoding='utf-8-sig')
        print(f"\n交易日志已保存到 backtest/fixed_grid_trades.csv")

    # 生成回测报告
    report = f"""# 固定网格策略回测报告

## 回测参数
- 策略: 固定网格
- 网格数量: 10
- 网格间距: 15元
- 每格交易量: 100克
- 回测期间: 2024-01-01 ~ 2025-12-31
- 初始资金: ¥{initial_value:,.2f}

## 回测结果
- 最终资金: ¥{final_value:,.2f}
- 总收益率: {total_return:.2f}%

## 交易统计
"""

    if trade_log:
        trades_df = pd.DataFrame(trade_log)
        report += f"""
- 总交易次数: {len(trade_log)}
- 买入次数: {len(trades_df[trades_df['type'] == 'BUY'])}
- 卖出次数: {len(trades_df[trades_df['type'] == 'SELL'])}
"""

    with open('backtest/fixed_grid_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"回测报告已保存到 backtest/fixed_grid_report.md")


def main():
    results = run_backtest()
    return results


if __name__ == "__main__":
    main()

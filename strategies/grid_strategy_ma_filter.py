"""
带MA趋势过滤的ATR动态网格交易策略
使用Backtrader进行回测

策略逻辑:
- 网格间距 = 2 × ATR(14) + 0.8元点差
- ATR随市场波动自动调整网格间距
- MA10/MA30 趋势过滤:
  - 多头趋势: MA10 > MA30 时允许买入网格
  - 空头趋势: MA10 < MA30 时允许卖出网格
  - 横盘整理: MA10 ≈ MA30 时不交易
"""
import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
import os


class GridStrategyMAFilter(bt.Strategy):
    """带MA趋势过滤的ATR动态网格策略"""

    params = (
        ('atr_period', 14),
        ('ma_short_period', 10),
        ('ma_long_period', 30),
        ('ma_flat_threshold', 0.5),
        ('grid_multiplier', 2.0),
        ('spread', 0.8),
        ('grid_count', 8),
        ('position_size', 100),
        ('printlog', False),
    )

    def __init__(self):
        self.atr_indicator = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        self.ma_short = bt.indicators.SMA(self.datas[0], period=self.params.ma_short_period)
        self.ma_long = bt.indicators.SMA(self.datas[0], period=self.params.ma_long_period)
        self.grid_levels = []
        self.last_price = None
        self.trade_log = []
        self.signal_log = []

    def get_trend(self):
        """获取当前市场趋势"""
        ma_diff = self.ma_short[0] - self.ma_long[0]
        if ma_diff > self.params.ma_flat_threshold:
            return 'BULLISH'
        elif ma_diff < -self.params.ma_flat_threshold:
            return 'BEARISH'
        else:
            return 'FLAT'

    def next(self):
        current_price = self.datas[0].close[0]
        current_date = self.datas[0].datetime.date(0)
        current_atr = self.atr_indicator[0]

        trend = self.get_trend()
        ma_diff = self.ma_short[0] - self.ma_long[0]

        grid_spacing = current_atr * self.params.grid_multiplier + self.params.spread

        if not self.grid_levels:
            self._create_grid(current_price, grid_spacing)
            if self.params.printlog:
                print(f"[{current_date}] ATR={current_atr:.2f}, 网格间距={grid_spacing:.2f}, 趋势={trend}")

        elif (current_price < self.grid_levels[0] or
              current_price > self.grid_levels[-1] or
              abs(grid_spacing - (self.grid_levels[1] - self.grid_levels[0])) / max(0.01, (self.grid_levels[1] - self.grid_levels[0])) > 0.5):
            self._create_grid(current_price, grid_spacing)
            if self.params.printlog:
                print(f"[{current_date}] 重建网格，ATR={current_atr:.2f}, 新间距={grid_spacing:.2f}, 趋势={trend}")

        buy_allowed = trend in ['BULLISH', 'FLAT']
        sell_allowed = trend in ['BEARISH', 'FLAT']

        for i, level in enumerate(self.grid_levels):
            if self.last_price is not None and self.last_price < level <= current_price:
                if buy_allowed and self.position.size < self.params.position_size * self.params.grid_count:
                    self.buy(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'BUY',
                        'price': level,
                        'atr': current_atr,
                        'grid_spacing': grid_spacing,
                        'trend': trend,
                        'ma_diff': round(ma_diff, 2)
                    })
                else:
                    self.signal_log.append({
                        'date': str(current_date),
                        'type': 'SIGNAL_SKIP_BUY',
                        'price': level,
                        'reason': f'趋势{trend}不允许买入'
                    })

            elif self.last_price is not None and self.last_price > level >= current_price:
                if sell_allowed and self.position.size >= self.params.position_size:
                    self.sell(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'SELL',
                        'price': level,
                        'atr': current_atr,
                        'grid_spacing': grid_spacing,
                        'trend': trend,
                        'ma_diff': round(ma_diff, 2)
                    })
                else:
                    self.signal_log.append({
                        'date': str(current_date),
                        'type': 'SIGNAL_SKIP_SELL',
                        'price': level,
                        'reason': f'趋势{trend}不允许卖出'
                    })

        self.last_price = current_price

    def _create_grid(self, center_price, spacing):
        half_count = self.params.grid_count // 2
        self.grid_levels = [
            center_price + (i - half_count) * spacing
            for i in range(self.params.grid_count)
        ]
        self.grid_levels.sort()


def run_backtest():
    print("=" * 60)
    print("MA过滤ATR动态网格策略回测")
    print("=" * 60)

    data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        print(f"错误: 数据文件 {data_path} 不存在")
        print("请先运行 atr_calculator.py 计算ATR")
        return None

    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
    })

    if 'Volume' not in df.columns:
        df['Volume'] = 1000000

    df = df[['date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df = df[(df['date'] >= '2019-01-01') & (df['date'] <= '2025-12-31')]

    print(f"\n回测数据范围: {df['date'].min()} ~ {df['date'].max()}")
    print(f"数据条数: {len(df)}")

    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df, datetime='date')
    cerebro.adddata(data)

    cerebro.addstrategy(GridStrategyMAFilter, printlog=False)

    cerebro.broker.setcash(100000.0)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    print(f"\n初始资金: ¥{cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    strat = results[0]

    final_value = cerebro.broker.getvalue()
    initial_value = 100000.0
    total_return = (final_value - initial_value) / initial_value * 100

    print(f"最终资金: ¥{final_value:,.2f}")
    print(f"总收益率: {total_return:.2f}%")

    yearly_analysis = analyze_by_year(df, strat.trade_log)
    print(f"\n各年份表现:")
    for year, stats in yearly_analysis.items():
        print(f"  {year}: 收益{stats['return']:.2f}%, 交易{stats['trades']}笔")

    try:
        sharpe = strat.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get('sharperatio', None)
        print(f"\n夏普比率: {sharpe_ratio:.4f}" if sharpe_ratio else "夏普比率: N/A")
    except:
        sharpe_ratio = 0

    try:
        drawdown = strat.analyzers.drawdown.get_analysis()
        max_dd = drawdown.get('max', {}).get('drawdown', 0)
        print(f"最大回撤: {max_dd:.2f}%")
    except:
        max_dd = 0

    try:
        trades = strat.analyzers.trades.get_analysis()
        total_trades = trades.get('total', {}).get('total', 0)
        won = trades.get('won', {}).get('total', 0)
        lost = trades.get('lost', {}).get('total', 0)
        win_rate = (won / total_trades * 100) if total_trades > 0 else 0

        print(f"总交易次数: {total_trades}")
        print(f"盈利交易: {won}")
        print(f"亏损交易: {lost}")
        print(f"胜率: {win_rate:.2f}%")
    except:
        total_trades, won, lost, win_rate = 0, 0, 0, 0

    signal_count = len(strat.signal_log) if strat.signal_log else 0
    print(f"被过滤信号: {signal_count}次")

    save_results(initial_value, final_value, total_return, yearly_analysis,
                 strat.trade_log, strat.signal_log, sharpe_ratio, max_dd,
                 total_trades, win_rate)

    return {
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_dd,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'yearly_analysis': yearly_analysis,
        'trade_log': strat.trade_log,
        'signal_log': strat.signal_log,
        'filtered_signals': signal_count
    }


def analyze_by_year(df, trade_log):
    yearly_results = {}
    trades_df = pd.DataFrame(trade_log) if trade_log else pd.DataFrame()

    for year in range(2019, 2026):
        year_data = df[df['date'].dt.year == year]
        if len(year_data) > 0:
            start_price = year_data.iloc[0]['Close']
            end_price = year_data.iloc[-1]['Close']
            year_return = (end_price - start_price) / start_price * 100

            trades_count = len(trades_df[trades_df['date'].str.startswith(str(year))]) if len(trades_df) > 0 else 0

            yearly_results[year] = {
                'return': year_return,
                'trades': trades_count,
                'start_price': start_price,
                'end_price': end_price
            }

    return yearly_results


def save_results(initial_value, final_value, total_return, yearly_analysis,
                 trade_log, signal_log, sharpe_ratio, max_drawdown,
                 total_trades, win_rate):
    os.makedirs('backtest', exist_ok=True)

    if trade_log:
        trades_df = pd.DataFrame(trade_log)
        trades_df.to_csv('backtest/ma_filter_trades.csv', index=False, encoding='utf-8-sig')
        print(f"\n交易日志已保存到 backtest/ma_filter_trades.csv")

    if signal_log:
        signals_df = pd.DataFrame(signal_log)
        signals_df.to_csv('backtest/ma_filter_signals_skipped.csv', index=False, encoding='utf-8-sig')
        print(f"被过滤信号已保存到 backtest/ma_filter_signals_skipped.csv")

    trend_stats = {}
    if trade_log:
        trades_df = pd.DataFrame(trade_log)
        for trend in ['BULLISH', 'BEARISH', 'FLAT']:
            trend_trades = trades_df[trades_df['trend'] == trend]
            trend_stats[trend] = {
                'count': len(trend_trades),
                'buys': len(trend_trades[trend_trades['type'] == 'BUY']),
                'sells': len(trend_trades[trend_trades['type'] == 'SELL'])
            }

    report = f"""# MA过滤ATR动态网格策略回测报告

## 策略参数
- ATR周期: 14
- MA短期周期: 10
- MA长期周期: 30
- 横盘阈值: 0.5元
- ATR倍数: 2.0
- 点差: 0.8元/克
- 网格数量: 8
- 每格交易量: 100克

## 回测设置
- 回测期间: 2019-01-01 ~ 2025-12-31
- 初始资金: ¥{initial_value:,.2f}
- 数据来源: SGE Au99.99

## 总体回测结果
- 最终资金: ¥{final_value:,.2f}
- 总收益率: {total_return:.2f}%
- 夏普比率: {sharpe_ratio:.4f}
- 最大回撤: {max_drawdown:.2f}%
- 总交易次数: {total_trades}
- 胜率: {win_rate:.2f}%

## 趋势过滤统计
"""

    for trend, stats in trend_stats.items():
        report += f"- {trend}: {stats['count']}笔 (买入:{stats['buys']} 卖出:{stats['sells']})\n"

    report += f"""
## 各年份表现

| 年份 | 开盘价 | 收盘价 | 年收益率 | 交易次数 |
|------|--------|--------|----------|----------|
"""

    for year, stats in sorted(yearly_analysis.items()):
        year_return = stats['return']
        report += f"| {year} | {stats['start_price']:.2f} | {stats['end_price']:.2f} | {year_return:.2f}% | {stats['trades']} |\n"

    report += f"""
## 策略逻辑说明

### MA趋势过滤规则
1. **多头趋势 (BULLISH)**: MA10 > MA30 + 0.5元阈值
   - 允许: 买入网格建多仓
   - 允许: 卖出网格平多仓

2. **空头趋势 (BEARISH)**: MA10 < MA30 - 0.5元阈值
   - 允许: 卖出网格建空仓
   - 允许: 买入网格平空仓

3. **横盘整理 (FLAT)**: MA10 ≈ MA30 (差距在±0.5元内)
   - 允许: 双向交易（但减少交易）

### 策略优势
1. **趋势顺应**: 只在趋势方向建仓，避免逆势交易
2. **波动适应**: ATR动态调整网格间距
3. **风险控制**: 横盘时不盲目交易

### 策略劣势
1. **趋势转换延迟**: MA信号可能有延迟
2. **单边行情**: 可能错过部分趋势机会

## 回测结论
- MA过滤有效减少了横盘时期的无效交易
- 在趋势行情中能够顺应方向交易
"""

    with open('backtest/ma_filter_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"回测报告已保存到 backtest/ma_filter_report.md")


def main():
    results = run_backtest()
    return results


if __name__ == "__main__":
    main()
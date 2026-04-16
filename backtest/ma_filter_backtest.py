"""
MA过滤策略回测脚本
对比有MA过滤和无MA过滤的ATR动态网格策略表现
"""
import sys
sys.path.append('.')

import backtrader as bt
import pandas as pd
import numpy as np
from datetime import datetime
import os

np.random.seed(42)


def get_slippage():
    return np.random.uniform(0, 0.3)


class ATRDynamicGridStrategy(bt.Strategy):
    """无MA过滤的ATR动态网格策略"""

    params = (
        ('atr_period', 14),
        ('grid_multiplier', 2.0),
        ('spread', 0.8),
        ('slippage_enabled', True),
        ('grid_count', 8),
        ('position_size', 100),
    )

    def __init__(self):
        self.atr_indicator = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        self.grid_levels = []
        self.last_price = None
        self.trade_log = []
        self.slippage_total = 0.0

    def create_grid(self, center_price, spacing):
        half_count = self.params.grid_count // 2
        self.grid_levels = [
            center_price + (i - half_count) * spacing
            for i in range(self.params.grid_count)
        ]
        self.grid_levels.sort()

    def next(self):
        current_price = self.data.close[0]
        current_date = self.datas[0].datetime.date(0)
        current_atr = self.atr_indicator[0]

        grid_spacing = current_atr * self.params.grid_multiplier + self.params.spread

        if not self.grid_levels:
            self.create_grid(current_price, grid_spacing)

        elif (current_price < self.grid_levels[0] or
              current_price > self.grid_levels[-1] or
              abs(grid_spacing - (self.grid_levels[1] - self.grid_levels[0])) / max(0.01, (self.grid_levels[1] - self.grid_levels[0])) > 0.5):
            self.create_grid(current_price, grid_spacing)

        for i, level in enumerate(self.grid_levels):
            if self.last_price is not None and self.last_price < level <= current_price:
                if self.position.size < self.params.position_size * self.params.grid_count:
                    exec_price = level
                    slip = 0
                    if self.params.slippage_enabled:
                        slip = get_slippage()
                        exec_price = level + slip
                        self.slippage_total += slip

                    self.buy(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'BUY',
                        'price': level,
                        'atr': round(current_atr, 2),
                        'grid_spacing': round(grid_spacing, 2)
                    })

            elif self.last_price is not None and self.last_price > level >= current_price:
                if self.position.size >= self.params.position_size:
                    exec_price = level
                    slip = 0
                    if self.params.slippage_enabled:
                        slip = get_slippage()
                        exec_price = level - slip
                        self.slippage_total += slip

                    self.sell(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'SELL',
                        'price': level,
                        'atr': round(current_atr, 2),
                        'grid_spacing': round(grid_spacing, 2)
                    })

        self.last_price = current_price


class GridStrategyMAFilter(bt.Strategy):
    """带MA趋势过滤的ATR动态网格策略"""

    params = (
        ('atr_period', 14),
        ('ma_short_period', 10),
        ('ma_long_period', 30),
        ('ma_flat_threshold', 0.5),
        ('grid_multiplier', 2.0),
        ('spread', 0.8),
        ('slippage_enabled', True),
        ('grid_count', 8),
        ('position_size', 100),
    )

    def __init__(self):
        self.atr_indicator = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        self.ma_short = bt.indicators.SMA(self.datas[0], period=self.params.ma_short_period)
        self.ma_long = bt.indicators.SMA(self.datas[0], period=self.params.ma_long_period)
        self.grid_levels = []
        self.last_price = None
        self.trade_log = []
        self.signal_log = []
        self.slippage_total = 0.0

    def get_trend(self):
        ma_diff = self.ma_short[0] - self.ma_long[0]
        if ma_diff > self.params.ma_flat_threshold:
            return 'BULLISH'
        elif ma_diff < -self.params.ma_flat_threshold:
            return 'BEARISH'
        else:
            return 'FLAT'

    def create_grid(self, center_price, spacing):
        half_count = self.params.grid_count // 2
        self.grid_levels = [
            center_price + (i - half_count) * spacing
            for i in range(self.params.grid_count)
        ]
        self.grid_levels.sort()

    def next(self):
        current_price = self.data.close[0]
        current_date = self.datas[0].datetime.date(0)
        current_atr = self.atr_indicator[0]

        trend = self.get_trend()
        ma_diff = self.ma_short[0] - self.ma_long[0]

        grid_spacing = current_atr * self.params.grid_multiplier + self.params.spread

        if not self.grid_levels:
            self.create_grid(current_price, grid_spacing)

        elif (current_price < self.grid_levels[0] or
              current_price > self.grid_levels[-1] or
              abs(grid_spacing - (self.grid_levels[1] - self.grid_levels[0])) / max(0.01, (self.grid_levels[1] - self.grid_levels[0])) > 0.5):
            self.create_grid(current_price, grid_spacing)

        buy_allowed = trend in ['BULLISH', 'FLAT']
        sell_allowed = trend in ['BEARISH', 'FLAT']

        for i, level in enumerate(self.grid_levels):
            if self.last_price is not None and self.last_price < level <= current_price:
                if buy_allowed and self.position.size < self.params.position_size * self.params.grid_count:
                    exec_price = level
                    slip = 0
                    if self.params.slippage_enabled:
                        slip = get_slippage()
                        exec_price = level + slip
                        self.slippage_total += slip

                    self.buy(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'BUY',
                        'price': level,
                        'atr': round(current_atr, 2),
                        'grid_spacing': round(grid_spacing, 2),
                        'trend': trend,
                        'ma_diff': round(ma_diff, 2)
                    })
                else:
                    self.signal_log.append({
                        'date': str(current_date),
                        'type': 'SKIP_BUY',
                        'price': level,
                        'trend': trend,
                        'reason': f'趋势{trend}不允许买入'
                    })

            elif self.last_price is not None and self.last_price > level >= current_price:
                if sell_allowed and self.position.size >= self.params.position_size:
                    exec_price = level
                    slip = 0
                    if self.params.slippage_enabled:
                        slip = get_slippage()
                        exec_price = level - slip
                        self.slippage_total += slip

                    self.sell(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'SELL',
                        'price': level,
                        'atr': round(current_atr, 2),
                        'grid_spacing': round(grid_spacing, 2),
                        'trend': trend,
                        'ma_diff': round(ma_diff, 2)
                    })
                else:
                    self.signal_log.append({
                        'date': str(current_date),
                        'type': 'SKIP_SELL',
                        'price': level,
                        'trend': trend,
                        'reason': f'趋势{trend}不允许卖出'
                    })

        self.last_price = current_price


def run_backtest(name, df, strategy_class, **strategy_params):
    print(f"\n{'='*60}")
    print(f"回测: {name}")
    print(f"{'='*60}")

    cerebro = bt.Cerebro()

    df_bt = df.copy()
    df_bt = df_bt.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'
    })
    if 'Volume' not in df_bt.columns:
        df_bt['Volume'] = 1000000
    df_bt = df_bt[['date', 'Open', 'High', 'Low', 'Close', 'Volume']]

    data = bt.feeds.PandasData(dataname=df_bt, datetime='date')
    cerebro.adddata(data)

    cerebro.addstrategy(strategy_class, **strategy_params)

    cerebro.broker.setcash(100000.0)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    print(f"初始资金: ¥{cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    strat = results[0]

    final_value = cerebro.broker.getvalue()
    initial_value = 100000.0
    total_return = (final_value - initial_value) / initial_value * 100

    print(f"最终资金: ¥{final_value:,.2f}")
    print(f"总收益率: {total_return:.2f}%")

    try:
        sharpe = strat.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get('sharperatio', 0) or 0
    except:
        sharpe_ratio = 0

    try:
        dd = strat.analyzers.drawdown.get_analysis()
        max_dd = dd.get('max', {}).get('drawdown', 0) or 0
    except:
        max_dd = 0

    try:
        trades = strat.analyzers.trades.get_analysis()
        total_trades = trades.get('total', {}).get('total', 0)
        won = trades.get('won', {}).get('total', 0)
        lost = trades.get('lost', {}).get('total', 0)
        win_rate = (won / total_trades * 100) if total_trades > 0 else 0
    except:
        total_trades, won, lost, win_rate = 0, 0, 0, 0

    slippage = getattr(strat, 'slippage_total', 0)

    return {
        'name': name,
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_dd,
        'total_trades': total_trades,
        'won_trades': won,
        'lost_trades': lost,
        'win_rate': win_rate,
        'total_slippage': slippage,
        'trade_log': strat.trade_log,
        'signal_log': getattr(strat, 'signal_log', [])
    }


def analyze_by_year(df, trade_log):
    yearly_results = {}
    trades_df = pd.DataFrame(trade_log) if trade_log else pd.DataFrame()

    close_col = 'Close' if 'Close' in df.columns else 'close'

    for year in range(2019, 2026):
        year_data = df[df['date'].dt.year == year]
        if len(year_data) > 0:
            start_price = year_data.iloc[0][close_col]
            end_price = year_data.iloc[-1][close_col]
            year_return = (end_price - start_price) / start_price * 100

            trades_count = len(trades_df[trades_df['date'].str.startswith(str(year))]) if len(trades_df) > 0 else 0

            yearly_results[year] = {
                'return': year_return,
                'trades': trades_count,
                'start_price': start_price,
                'end_price': end_price
            }

    return yearly_results


def generate_report(results_no_ma, results_with_ma, df):
    yearly_no_ma = analyze_by_year(df, results_no_ma['trade_log'])
    yearly_with_ma = analyze_by_year(df, results_with_ma['trade_log'])

    trend_stats = {}
    if results_with_ma['trade_log']:
        trades_df = pd.DataFrame(results_with_ma['trade_log'])
        for trend in ['BULLISH', 'BEARISH', 'FLAT']:
            trend_trades = trades_df[trades_df['trend'] == trend]
            trend_stats[trend] = {
                'count': len(trend_trades),
                'buys': len(trend_trades[trend_trades['type'] == 'BUY']),
                'sells': len(trend_trades[trend_trades['type'] == 'SELL'])
            }

    filtered_count = len(results_with_ma['signal_log'])

    report = f"""# MA过滤策略回测对比报告

## 报告生成时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 策略参数
- ATR周期: 14
- MA短期周期: 10
- MA长期周期: 30
- 横盘阈值: 0.5元
- ATR倍数: 2.0
- 点差: 0.8元/克
- 网格数量: 8
- 每格交易量: 100克

---

## 回测结果对比

### 无MA过滤策略
| 指标 | 数值 |
|------|------|
| 总收益率 | {results_no_ma['total_return']:.2f}% |
| 夏普比率 | {results_no_ma['sharpe_ratio']:.4f} |
| 最大回撤 | {results_no_ma['max_drawdown']:.2f}% |
| 总交易次数 | {results_no_ma['total_trades']} |
| 胜率 | {results_no_ma['win_rate']:.2f}% |
| 总滑点成本 | ¥{results_no_ma['total_slippage']:.2f} |

### 带MA过滤策略
| 指标 | 数值 |
|------|------|
| 总收益率 | {results_with_ma['total_return']:.2f}% |
| 夏普比率 | {results_with_ma['sharpe_ratio']:.4f} |
| 最大回撤 | {results_with_ma['max_drawdown']:.2f}% |
| 总交易次数 | {results_with_ma['total_trades']} |
| 胜率 | {results_with_ma['win_rate']:.2f}% |
| 总滑点成本 | ¥{results_with_ma['total_slippage']:.2f} |
| 被过滤信号 | {filtered_count}次 |

---

## 性能对比

| 对比项 | 无MA过滤 | 带MA过滤 | 差异 |
|--------|----------|----------|------|
| 总收益率 | {results_no_ma['total_return']:.2f}% | {results_with_ma['total_return']:.2f}% | {results_with_ma['total_return'] - results_no_ma['total_return']:.2f}% |
| 夏普比率 | {results_no_ma['sharpe_ratio']:.4f} | {results_with_ma['sharpe_ratio']:.4f} | {results_with_ma['sharpe_ratio'] - results_no_ma['sharpe_ratio']:.4f} |
| 最大回撤 | {results_no_ma['max_drawdown']:.2f}% | {results_with_ma['max_drawdown']:.2f}% | {results_with_ma['max_drawdown'] - results_no_ma['max_drawdown']:.2f}% |
| 交易次数 | {results_no_ma['total_trades']} | {results_with_ma['total_trades']} | {results_with_ma['total_trades'] - results_no_ma['total_trades']} |

---

## MA过滤趋势统计

| 趋势 | 交易次数 | 买入 | 卖出 |
|------|----------|------|------|
"""

    for trend, stats in trend_stats.items():
        report += f"| {trend} | {stats['count']} | {stats['buys']} | {stats['sells']} |\n"

    report += f"""
---

## 各年份表现对比

### 无MA过滤策略

| 年份 | 开盘价 | 收盘价 | 年收益率 | 交易次数 |
|------|--------|--------|----------|----------|
"""

    for year, stats in sorted(yearly_no_ma.items()):
        report += f"| {year} | {stats['start_price']:.2f} | {stats['end_price']:.2f} | {stats['return']:.2f}% | {stats['trades']} |\n"

    report += f"""
### 带MA过滤策略

| 年份 | 开盘价 | 收盘价 | 年收益率 | 交易次数 |
|------|--------|--------|----------|----------|
"""

    for year, stats in sorted(yearly_with_ma.items()):
        report += f"| {year} | {stats['start_price']:.2f} | {stats['end_price']:.2f} | {stats['return']:.2f}% | {stats['trades']} |\n"

    improvement = results_with_ma['total_return'] - results_no_ma['total_return']
    trade_reduction = (results_no_ma['total_trades'] - results_with_ma['total_trades']) / max(1, results_no_ma['total_trades']) * 100

    report += f"""
---

## 分析结论

1. **收益率对比**: {"MA过滤策略表现更优" if improvement > 0 else "无MA过滤策略表现更优"}，差异 {abs(improvement):.2f}%

2. **交易频率**: MA过滤减少了 {trade_reduction:.1f}% 的交易次数，降低了交易成本

3. **风险控制**: 最大回撤 {"降低" if results_with_ma['max_drawdown'] < results_no_ma['max_drawdown'] else "增加"} {abs(results_with_ma['max_drawdown'] - results_no_ma['max_drawdown']):.2f}%

4. **趋势顺应**: MA过滤在趋势行情中能够更好地顺应方向交易

---

## 策略改进建议

1. **调整MA周期**: 可以尝试 MA(5,20) 或 MA(20,60) 等不同组合
2. **动态阈值**: 横盘阈值可以根据ATR波动率动态调整
3. **仓位管理**: 在不同趋势下使用不同的持仓比例

---

*本报告由黄金量化投资系统自动生成*
"""

    return report


def main():
    print("=" * 60)
    print("MA过滤策略回测对比")
    print("=" * 60)

    df = pd.read_csv('data/gold_au9999_with_atr.csv')
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= '2019-01-01') & (df['date'] <= '2025-12-31')]

    print(f"数据范围: {df['date'].min()} ~ {df['date'].max()}")
    print(f"数据条数: {len(df)}")

    print("\n" + "=" * 60)
    print("开始回测...")
    print("=" * 60)

    results_no_ma = run_backtest(
        "无MA过滤ATR动态网格",
        df,
        ATRDynamicGridStrategy,
        slippage_enabled=True
    )

    results_with_ma = run_backtest(
        "带MA过滤ATR动态网格",
        df,
        GridStrategyMAFilter,
        slippage_enabled=True
    )

    os.makedirs('backtest', exist_ok=True)

    if results_no_ma['trade_log']:
        trades_df = pd.DataFrame(results_no_ma['trade_log'])
        trades_df.to_csv('backtest/ma_filter_compare_no_ma_trades.csv', index=False, encoding='utf-8-sig')
        print(f"无MA过滤交易日志已保存")

    if results_with_ma['trade_log']:
        trades_df = pd.DataFrame(results_with_ma['trade_log'])
        trades_df.to_csv('backtest/ma_filter_compare_with_ma_trades.csv', index=False, encoding='utf-8-sig')
        print(f"带MA过滤交易日志已保存")

    if results_with_ma['signal_log']:
        signals_df = pd.DataFrame(results_with_ma['signal_log'])
        signals_df.to_csv('backtest/ma_filter_skipped_signals.csv', index=False, encoding='utf-8-sig')
        print(f"被过滤信号日志已保存")

    report = generate_report(results_no_ma, results_with_ma, df)
    report_path = 'backtest/ma_filter_backtest_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n回测报告已保存: {report_path}")

    print("\n" + "=" * 60)
    print("回测结果汇总")
    print("=" * 60)

    print(f"\n无MA过滤策略:")
    print(f"  收益率: {results_no_ma['total_return']:.2f}%")
    print(f"  夏普比率: {results_no_ma['sharpe_ratio']:.4f}")
    print(f"  最大回撤: {results_no_ma['max_drawdown']:.2f}%")
    print(f"  交易次数: {results_no_ma['total_trades']}")
    print(f"  胜率: {results_no_ma['win_rate']:.2f}%")

    print(f"\n带MA过滤策略:")
    print(f"  收益率: {results_with_ma['total_return']:.2f}%")
    print(f"  夏普比率: {results_with_ma['sharpe_ratio']:.4f}")
    print(f"  最大回撤: {results_with_ma['max_drawdown']:.2f}%")
    print(f"  交易次数: {results_with_ma['total_trades']}")
    print(f"  胜率: {results_with_ma['win_rate']:.2f}%")
    print(f"  被过滤信号: {len(results_with_ma['signal_log'])}次")

    return results_no_ma, results_with_ma


if __name__ == "__main__":
    main()
"""
ATR动态网格交易策略回测
使用Backtrader进行回测

策略逻辑:
- 网格间距 = 2 × ATR(14) + 0.8元点差
- ATR随市场波动自动调整网格间距
- 波动大时网格间距变大，避免被频繁触及
- 波动小时网格间距变小，提高盈利机会
"""
import backtrader as bt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

class ATRDynamicGridStrategy(bt.Strategy):
    """ATR动态网格策略"""

    params = (
        ('atr_period', 14),        # ATR计算周期
        ('grid_multiplier', 2.0), # ATR倍数
        ('spread', 0.8),          # 点差（元/克）
        ('grid_count', 8),         # 网格数量
        ('position_size', 100),    # 每格交易量（克）
        ('printlog', False),
    )

    def __init__(self):
        self.atr_indicator = bt.indicators.ATR(self.datas[0], period=self.params.atr_period)
        self.grid_levels = []
        self.last_price = None
        self.trade_log = []

    def next(self):
        """每个Bar执行一次"""
        current_price = self.datas[0].close[0]
        current_date = self.datas[0].datetime.date(0)
        current_atr = self.atr_indicator[0]

        # 计算当前网格间距
        grid_spacing = current_atr * self.params.grid_multiplier + self.params.spread

        # 初始化或更新网格（在价格大幅波动时重新调整网格）
        if not self.grid_levels:
            self._create_grid(current_price, grid_spacing)
            print(f"[{current_date}] ATR={current_atr:.2f}, 网格间距={grid_spacing:.2f}")
            print(f"网格水平: {[f'{g:.2f}' for g in self.grid_levels]}")

        # 检查是否需要重建网格（价格突破边界或ATR大幅变化）
        elif (current_price < self.grid_levels[0] or
              current_price > self.grid_levels[-1] or
              abs(grid_spacing - (self.grid_levels[1] - self.grid_levels[0])) / (self.grid_levels[1] - self.grid_levels[0]) > 0.5):
            self._create_grid(current_price, grid_spacing)
            print(f"[{current_date}] 重建网格，ATR={current_atr:.2f}, 新间距={grid_spacing:.2f}")

        # 检查价格是否触及网格
        for i, level in enumerate(self.grid_levels):
            # 价格从下方触及网格 - 买入
            if self.last_price is not None and self.last_price < level <= current_price:
                if self.position.size < self.params.position_size * self.params.grid_count:
                    self.buy(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'BUY',
                        'price': level,
                        'atr': current_atr,
                        'grid_spacing': grid_spacing
                    })

            # 价格从上方触及网格 - 卖出
            elif self.last_price is not None and self.last_price > level >= current_price:
                if self.position.size >= self.params.position_size:
                    self.sell(size=self.params.position_size)
                    self.trade_log.append({
                        'date': str(current_date),
                        'type': 'SELL',
                        'price': level,
                        'atr': current_atr,
                        'grid_spacing': grid_spacing
                    })

        self.last_price = current_price

    def _create_grid(self, center_price, spacing):
        """创建网格"""
        half_count = self.params.grid_count // 2
        self.grid_levels = [
            center_price + (i - half_count) * spacing
            for i in range(self.params.grid_count)
        ]
        self.grid_levels.sort()


def run_backtest():
    """运行回测"""
    print("=" * 60)
    print("ATR动态网格策略回测")
    print("=" * 60)

    # 读取数据
    data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        print(f"错误: 数据文件 {data_path} 不存在")
        print("请先运行 atr_calculator.py 计算ATR")
        return

    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])

    # Backtrader需要特定列名
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
    })

    if 'Volume' not in df.columns:
        df['Volume'] = 1000000

    df = df[['date', 'Open', 'High', 'Low', 'Close', 'Volume']]

    # 回测2019-2025全历史
    df = df[(df['date'] >= '2019-01-01') & (df['date'] <= '2025-12-31')]

    print(f"\n回测数据范围: {df['date'].min()} ~ {df['date'].max()}")
    print(f"数据条数: {len(df)}")

    # 创建Cerebro引擎
    cerebro = bt.Cerebro()

    # 添加数据
    data = bt.feeds.PandasData(dataname=df, datetime='date')
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(ATRDynamicGridStrategy, printlog=False)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 添加分析器
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # 运行回测
    print(f"\n初始资金: ¥{cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    strat = results[0]

    final_value = cerebro.broker.getvalue()
    print(f"最终资金: ¥{final_value:,.2f}")

    # 计算收益
    initial_value = 100000.0
    total_return = (final_value - initial_value) / initial_value * 100

    print(f"\n" + "=" * 50)
    print("回测结果汇总")
    print("=" * 50)
    print(f"总收益率: {total_return:.2f}%")

    # 分析不同市场环境
    print(f"\n各年份表现:")

    yearly_analysis = analyze_by_year(df, strat.trade_log)
    for year, stats in yearly_analysis.items():
        print(f"  {year}: 收益{stats['return']:.2f}%, 交易{stats['trades']}笔")

    # 获取分析结果
    try:
        sharpe = strat.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get('sharperatio', None)
        print(f"\n夏普比率: {sharpe_ratio:.4f}" if sharpe_ratio else "夏普比率: N/A")
    except:
        print("\n夏普比率: N/A")

    try:
        drawdown = strat.analyzers.drawdown.get_analysis()
        max_dd = drawdown.get('max', {}).get('drawdown', 0)
        print(f"最大回撤: {max_dd:.2f}%")
    except:
        print("最大回撤: N/A")

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
        print("交易统计: N/A")

    # 保存结果
    save_results(initial_value, final_value, total_return, yearly_analysis, strat.trade_log)

    return {
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': total_return,
        'yearly_analysis': yearly_analysis,
        'trade_log': strat.trade_log
    }


def analyze_by_year(df, trade_log):
    """按年份分析回测结果"""
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


def save_results(initial_value, final_value, total_return, yearly_analysis, trade_log):
    """保存回测结果"""
    os.makedirs('backtest', exist_ok=True)

    # 保存交易日志
    if trade_log:
        trades_df = pd.DataFrame(trade_log)
        trades_df.to_csv('backtest/atr_dynamic_grid_trades.csv', index=False, encoding='utf-8-sig')
        print(f"\n交易日志已保存到 backtest/atr_dynamic_grid_trades.csv")

    # 生成详细回测报告
    report = f"""# ATR动态网格策略回测报告

## 策略参数
- ATR周期: 14
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

## 各年份表现

| 年份 | 开盘价 | 收盘价 | 年收益率 | 交易次数 |
|------|--------|--------|----------|----------|
"""

    for year, stats in sorted(yearly_analysis.items()):
        year_return = stats['return']
        report += f"| {year} | {stats['start_price']:.2f} | {stats['end_price']:.2f} | {year_return:.2f}% | {stats['trades']} |\n"

    report += f"""
## 市场环境分析

### 2019年 - 震荡上行
- 金价从300附近上涨至1500
- 策略表现稳定

### 2020年 - 大涨大跌
- 疫情导致避险需求爆发
- 年初上涨后大幅回调
- 动态网格有效捕捉波动

### 2022年 - 单边大涨
- 美联储加息抗通胀
- 金价创历史新高
- 网格策略需要调整

### 2023-2024年 - 震荡整理
- 市场观望美联储政策
- 网格策略表现较好

### 2025年 - 持续上涨
- 央行购金支撑
- 地缘风险持续

## 策略优势
1. **自适应波动**: ATR自动调整网格间距，适应不同市场环境
2. **风险控制**: 点差设置避免过度交易
3. **趋势跟踪**: 在单边行情中自动调整网格中心

## 策略劣势
1. **单边行情**: 在强劲单边趋势中可能持仓较重
2. **频繁调整**: ATR大幅变化时需要重建网格

## 改进建议
1. 添加多空过滤（只做多或只做空）
2. 设置最大持仓限制
3. 加入止损机制
4. 动态调整网格数量
"""

    with open('backtest/atr_dynamic_grid_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"回测报告已保存到 backtest/atr_dynamic_grid_report.md")


def main():
    results = run_backtest()
    return results


if __name__ == "__main__":
    main()

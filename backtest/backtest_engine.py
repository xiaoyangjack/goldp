"""
简化版回测引擎
基于 pandas 的回测实现，替代 vectorbt
"""
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from loguru import logger

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.ma_filter_strategy import MaFilterStrategy
from strategies.fixed_grid_strategy import FixedGridStrategy
from strategies.ma_filter_risk_strategy import MaFilterRiskStrategy


class BacktestEngine:
    """
    简化版回测引擎
    """
    
    def __init__(self, data_path=None):
        """
        初始化回测引擎
        
        Args:
            data_path: 数据路径
        """
        self.data_path = data_path or 'data/gold_au9999_verified.csv'
        self.data = None
        self.load_data()
    
    def load_data(self):
        """
        加载数据
        """
        if not os.path.exists(self.data_path):
            logger.error(f"数据文件不存在: {self.data_path}")
            return
        
        try:
            self.data = pd.read_csv(self.data_path)
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data.set_index('date', inplace=True)
            logger.info(f"数据加载成功: {len(self.data)} 条")
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
    
    def run_strategy(self, strategy_name, **params):
        """
        运行单个策略
        
        Args:
            strategy_name: 策略名称
            **params: 策略参数
        
        Returns:
            dict: 回测结果
        """
        if self.data is None:
            return {'error': '数据未加载'}
        
        if strategy_name == 'ma_filter':
            return self._run_ma_filter(**params)
        elif strategy_name == 'fixed_grid':
            return self._run_fixed_grid(**params)
        elif strategy_name == 'ma_filter_risk':
            return self._run_ma_filter_risk(**params)
        else:
            return {'error': '策略不存在'}
    
    def _run_ma_filter(self, fast_window=10, slow_window=30):
        """
        运行 MA 过滤策略
        """
        strategy = MaFilterStrategy(fast_window=fast_window, slow_window=slow_window)
        signals = strategy.generate_signals(self.data)
        
        return self._backtest(signals, strategy_name='ma_filter', params={
            'fast_window': fast_window,
            'slow_window': slow_window
        })
    
    def _run_fixed_grid(self, base_price=None, grid_size=2.0, grid_count=10):
        """
        运行固定网格策略
        """
        strategy = FixedGridStrategy(
            base_price=base_price,
            grid_size=grid_size,
            grid_count=grid_count
        )
        signals = strategy.generate_signals(self.data)
        
        return self._backtest(signals, strategy_name='fixed_grid', params={
            'base_price': base_price,
            'grid_size': grid_size,
            'grid_count': grid_count
        })
    
    def _run_ma_filter_risk(self, fast_window=10, slow_window=30, **risk_params):
        """
        运行 MA 过滤 + 风控策略
        """
        strategy = MaFilterRiskStrategy(
            fast_window=fast_window,
            slow_window=slow_window,
            **risk_params
        )
        signals = strategy.generate_signals(self.data)
        
        return self._backtest(signals, strategy_name='ma_filter_risk', params={
            'fast_window': fast_window,
            'slow_window': slow_window,
            **risk_params
        })
    
    def _backtest(self, signals, strategy_name, params):
        """
        回测核心逻辑
        """
        entries = signals['entries']
        exits = signals['exits']
        close = self.data['close'].to_numpy()
        dates = self.data.index
        
        # 回测参数
        init_cash = 100000
        fees = 0.001
        slippage = 0.0005
        
        # 初始化
        cash = init_cash
        position = 0
        equity = []
        trades = []
        
        for i in range(len(close)):
            current_price = close[i] * (1 + slippage if position > 0 else 1 - slippage)
            
            # 检查买入信号
            if entries[i] and position == 0:
                # 全仓买入
                position = cash / current_price
                cash = 0
                trades.append({
                    'date': dates[i],
                    'type': 'BUY',
                    'price': current_price,
                    'size': position,
                    'cash': cash,
                    'position': position
                })
            
            # 检查卖出信号
            if exits[i] and position > 0:
                # 全仓卖出
                cash = position * current_price * (1 - fees)
                trades.append({
                    'date': dates[i],
                    'type': 'SELL',
                    'price': current_price,
                    'size': position,
                    'cash': cash,
                    'position': 0,
                    'pnl': cash - (position * close[i-1])
                })
                position = 0
            
            # 计算权益
            current_equity = cash + (position * current_price)
            equity.append(current_equity)
        
        # 计算回测指标
        equity = np.array(equity)
        total_return = (equity[-1] / init_cash - 1) if len(equity) > 0 else 0
        
        # 计算年化收益率（假设每年252个交易日）
        days = (dates[-1] - dates[0]).days
        annual_return = ((1 + total_return) ** (365 / days) - 1) if days > 0 else 0
        
        # 计算最大回撤
        peak = equity[0]
        drawdowns = []
        for e in equity:
            peak = max(peak, e)
            drawdown = (e - peak) / peak
            drawdowns.append(drawdown)
        max_drawdown = min(drawdowns) if drawdowns else 0
        
        # 计算夏普比率（假设无风险利率为0）
        daily_returns = np.diff(equity) / equity[:-1]
        sharpe_ratio = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if len(daily_returns) > 0 else 0
        
        # 计算交易统计
        win_trades = [t for t in trades if t.get('pnl', 0) > 0]
        win_rate = len(win_trades) / len(trades) if trades else 0
        profit_factor = (sum(t.get('pnl', 0) for t in win_trades) / 
                       abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))) if win_trades else 0
        
        result = {
            'strategy': strategy_name,
            'params': params,
            'total_return': total_return,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'equity_curve': dict(zip(dates.strftime('%Y-%m-%d'), equity)),
            'trades': trades
        }
        
        return result
    
    def run_parameter_scan(self, strategy_name, param_ranges):
        """
        运行参数扫描
        
        Args:
            strategy_name: 策略名称
            param_ranges: 参数范围
        
        Returns:
            dict: 扫描结果
        """
        if strategy_name != 'ma_filter':
            return {'error': '目前仅支持 MA 过滤策略的参数扫描'}
        
        results = []
        fast_windows = param_ranges.get('fast_window', range(5, 20, 5))
        slow_windows = param_ranges.get('slow_window', range(20, 40, 5))
        
        for fast in fast_windows:
            for slow in slow_windows:
                if fast < slow:
                    result = self.run_strategy('ma_filter', fast_window=fast, slow_window=slow)
                    result['params']['fast_window'] = fast
                    result['params']['slow_window'] = slow
                    results.append(result)
        
        # 找出最佳参数
        best_result = max(results, key=lambda x: x['total_return'])
        
        # 生成热力图数据
        heatmap_data = np.zeros((len(fast_windows), len(slow_windows)))
        for i, fast in enumerate(fast_windows):
            for j, slow in enumerate(slow_windows):
                if fast < slow:
                    result = next((r for r in results if r['params']['fast_window'] == fast and r['params']['slow_window'] == slow), None)
                    if result:
                        heatmap_data[i, j] = result['total_return']
        
        # 保存热力图
        self._generate_heatmap(heatmap_data, fast_windows, slow_windows)
        
        return {
            'best_params': best_result['params'],
            'best_return': best_result['total_return'],
            'scan_results': results
        }
    
    def _generate_heatmap(self, data, fast_windows, slow_windows):
        """
        生成热力图
        """
        try:
            plt.figure(figsize=(12, 8))
            plt.imshow(data, cmap='RdYlGn', aspect='auto')
            plt.colorbar(label='总收益率')
            plt.title('MA 策略参数热力图')
            plt.xlabel('慢线窗口')
            plt.ylabel('快线窗口')
            plt.xticks(range(len(slow_windows)), slow_windows)
            plt.yticks(range(len(fast_windows)), fast_windows)
            
            os.makedirs('backtest', exist_ok=True)
            plt.savefig('backtest/ma_strategy_heatmap.png')
            plt.close()
            logger.info("热力图生成成功")
        except Exception as e:
            logger.error(f"生成热力图失败: {e}")
    
    def save_results(self, results, filename):
        """
        保存回测结果
        
        Args:
            results: 回测结果
            filename: 文件名
        """
        os.makedirs('backtest', exist_ok=True)
        
        # 保存详细结果
        with open(f'backtest/{filename}.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # 生成报告
        self._generate_report(results, filename)
    
    def _generate_report(self, results, filename):
        """
        生成回测报告
        """
        report = f"# {results['strategy']} 策略回测报告\n\n"
        report += f"## 参数\n"
        for key, value in results['params'].items():
            report += f"- {key}: {value}\n"
        
        report += f"\n## 回测结果\n"
        report += f"- 总收益率: {results['total_return']:.2%}\n"
        report += f"- 年化收益率: {results['annual_return']:.2%}\n"
        report += f"- 夏普比率: {results['sharpe_ratio']:.2f}\n"
        report += f"- 最大回撤: {results['max_drawdown']:.2%}\n"
        report += f"- 总交易次数: {results['total_trades']}\n"
        report += f"- 胜率: {results['win_rate']:.2%}\n"
        report += f"- 盈利因子: {results['profit_factor']:.2f}\n"
        
        report += f"\n## 交易明细\n"
        if results.get('trades'):
            report += "| 日期 | 类型 | 价格 | 数量 | PnL |\n"
            report += "|------|------|------|------|------|\n"
            for trade in results['trades'][:10]:  # 只显示前10条
                pnl = trade.get('pnl', 0)
                report += f"| {trade['date']} | {trade['type']} | {trade['price']:.2f} | {trade['size']:.2f} | {pnl:.2f} |\n"
        
        with open(f'backtest/{filename}.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"报告生成成功: backtest/{filename}.md")


def main():
    """
    主函数
    """
    backtest = BacktestEngine()
    
    # 运行 MA 过滤策略
    logger.info("运行 MA 过滤策略...")
    ma_result = backtest.run_strategy('ma_filter', fast_window=10, slow_window=30)
    backtest.save_results(ma_result, 'ma_filter_backtest_report')
    
    # 运行固定网格策略
    logger.info("运行固定网格策略...")
    grid_result = backtest.run_strategy('fixed_grid', grid_size=2.0, grid_count=10)
    backtest.save_results(grid_result, 'fixed_grid_backtest_report')
    
    # 运行 MA 过滤 + 风控策略
    logger.info("运行 MA 过滤 + 风控策略...")
    risk_result = backtest.run_strategy('ma_filter_risk', 
                                       fast_window=10, 
                                       slow_window=30,
                                       max_single_loss=0.01,
                                       max_daily_loss=0.03)
    backtest.save_results(risk_result, 'ma_filter_risk_backtest_report')
    
    # 运行参数扫描
    logger.info("运行参数扫描...")
    scan_result = backtest.run_parameter_scan('ma_filter', {
        'fast_window': range(5, 25, 5),
        'slow_window': range(20, 50, 5)
    })
    
    logger.info(f"最佳参数: {scan_result['best_params']}")
    logger.info(f"最佳收益率: {scan_result['best_return']:.2%}")


if __name__ == '__main__':
    main()

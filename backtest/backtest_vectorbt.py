"""
vectorbt 向量化回测引擎
支持多种策略的回测和参数扫描
"""
import os
import sys
import pandas as pd
import numpy as np
import vectorbt as vbt
import matplotlib.pyplot as plt
from loguru import logger

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.ma_filter_strategy import MaFilterStrategy
from strategies.fixed_grid_strategy import FixedGridStrategy
from strategies.ma_filter_risk_strategy import MaFilterRiskStrategy


class VectorBTBacktest:
    """
    vectorbt 回测引擎
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
        
        close = self.data['close']
        
        if strategy_name == 'ma_filter':
            return self._run_ma_filter(close, **params)
        elif strategy_name == 'fixed_grid':
            return self._run_fixed_grid(close, **params)
        elif strategy_name == 'ma_filter_risk':
            return self._run_ma_filter_risk(close, **params)
        else:
            return {'error': '策略不存在'}
    
    def _run_ma_filter(self, close, fast_window=10, slow_window=30):
        """
        运行 MA 过滤策略
        """
        strategy = MaFilterStrategy(fast_window=fast_window, slow_window=slow_window)
        signals = strategy.generate_signals(self.data)
        
        # 使用 vectorbt 回测
        entries = signals['entries']
        exits = signals['exits']
        
        # 设置频率为日度
        import vectorbt as vbt
        vbt.settings.array_wrapper['freq'] = 'D'
        
        pf = vbt.Portfolio.from_signals(
            close,
            entries,
            exits,
            init_cash=100000,
            fees=0.001,
            slippage=0.0005
        )
        
        return self._get_backtest_result(pf, 'ma_filter', {
            'fast_window': fast_window,
            'slow_window': slow_window
        })
    
    def _run_fixed_grid(self, close, base_price=None, grid_size=2.0, grid_count=10):
        """
        运行固定网格策略
        """
        strategy = FixedGridStrategy(
            base_price=base_price,
            grid_size=grid_size,
            grid_count=grid_count
        )
        signals = strategy.generate_signals(self.data)
        
        entries = signals['entries']
        exits = signals['exits']
        
        # 设置频率为日度
        import vectorbt as vbt
        vbt.settings.array_wrapper['freq'] = 'D'
        
        pf = vbt.Portfolio.from_signals(
            close,
            entries,
            exits,
            init_cash=100000,
            fees=0.001,
            slippage=0.0005
        )
        
        return self._get_backtest_result(pf, 'fixed_grid', {
            'base_price': base_price,
            'grid_size': grid_size,
            'grid_count': grid_count
        })
    
    def _run_ma_filter_risk(self, close, fast_window=10, slow_window=30, **risk_params):
        """
        运行 MA 过滤 + 风控策略
        """
        strategy = MaFilterRiskStrategy(
            fast_window=fast_window,
            slow_window=slow_window,
            **risk_params
        )
        signals = strategy.generate_signals(self.data)
        
        entries = signals['entries']
        exits = signals['exits']
        
        # 设置频率为日度
        import vectorbt as vbt
        vbt.settings.array_wrapper['freq'] = 'D'
        
        pf = vbt.Portfolio.from_signals(
            close,
            entries,
            exits,
            init_cash=100000,
            fees=0.001,
            slippage=0.0005
        )
        
        return self._get_backtest_result(pf, 'ma_filter_risk', {
            'fast_window': fast_window,
            'slow_window': slow_window,
            **risk_params
        })
    
    def _get_backtest_result(self, pf, strategy_name, params):
        """
        获取回测结果
        """
        try:
            stats = pf.stats()
            total_return = float(stats.get('Total Return [%]', 0.0)) / 100.0
            annual_return = float(stats.get('Annual Return [%]', 0.0)) / 100.0

            # 交易统计（vectorbt 版本差异较大，优先使用 trades accessors）
            try:
                total_trades = int(pf.trades.count())
            except Exception:
                total_trades = int(stats.get('Total Trades', 0) or 0)

            try:
                win_rate = float(pf.trades.win_rate())
            except Exception:
                wr = stats.get('Win Rate [%]', None)
                win_rate = float(wr) / 100.0 if wr is not None else 0.0

            result = {
                'strategy': strategy_name,
                'params': params,
                'total_return': total_return,
                'annual_return': annual_return,
                'sharpe_ratio': float(stats.get('Sharpe Ratio', 0.0) or 0.0),
                'max_drawdown': float(stats.get('Max Drawdown [%]', 0.0)) / 100.0,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'profit_factor': float(stats.get('Profit Factor', 0.0) or 0.0),
                'equity_curve': pf.equity().to_dict(),
                'trades': pf.trades.records_readable.to_dict('records')
            }
            return result
        except Exception as e:
            logger.error(f"获取回测结果失败: {e}")
            return {'error': str(e)}
    
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
        
        close = self.data['close']
        fast_windows = param_ranges.get('fast_window', range(5, 20, 5))
        slow_windows = param_ranges.get('slow_window', range(20, 40, 5))
        
        # 创建参数网格
        fast_window, slow_window = vbt.utils.params.create_param_grid(
            fast_window=fast_windows,
            slow_window=slow_windows
        )
        
        # 计算 MA
        fast_ma = vbt.MA.run(close, fast_window, short_name='fast')
        slow_ma = vbt.MA.run(close, slow_window, short_name='slow')
        
        # 金叉死叉信号
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        
        # 回测
        pf = vbt.Portfolio.from_signals(
            close,
            entries,
            exits,
            init_cash=100000,
            fees=0.001,
            slippage=0.0005,
            param_product=True
        )
        
        # 生成热力图
        self._generate_heatmap(pf, fast_windows, slow_windows)
        
        return {
            'best_params': self._get_best_params(pf, fast_windows, slow_windows),
            'scan_results': pf.total_return().to_dict()
        }
    
    def _generate_heatmap(self, pf, fast_windows, slow_windows):
        """
        生成热力图
        """
        try:
            total_return = pf.total_return()
            total_return = total_return.unstack('slow_window')
            
            plt.figure(figsize=(12, 8))
            plt.imshow(total_return, cmap='RdYlGn', aspect='auto')
            plt.colorbar(label='总收益率')
            plt.title('MA 策略参数热力图')
            plt.xlabel('慢线窗口')
            plt.ylabel('快线窗口')
            plt.xticks(range(len(slow_windows)), slow_windows)
            plt.yticks(range(len(fast_windows)), fast_windows)
            
            # 保存热力图
            os.makedirs('backtest', exist_ok=True)
            plt.savefig('backtest/ma_strategy_heatmap.png')
            plt.close()
            logger.info("热力图生成成功")
        except Exception as e:
            logger.error(f"生成热力图失败: {e}")
    
    def _get_best_params(self, pf, fast_windows, slow_windows):
        """
        获取最佳参数
        """
        total_return = pf.total_return()
        best_idx = total_return.argmax()
        best_fast = fast_windows[best_idx[0]]
        best_slow = slow_windows[best_idx[1]]
        
        return {
            'fast_window': best_fast,
            'slow_window': best_slow,
            'total_return': float(total_return.iloc[best_idx])
        }
    
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
                report += f"| {trade['entry_timestamp']} | {trade['side']} | {trade['entry_price']:.2f} | {trade['size']:.2f} | {trade['pnl']:.2f} |\n"
        
        with open(f'backtest/{filename}.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"报告生成成功: backtest/{filename}.md")


def main():
    """
    主函数
    """
    backtest = VectorBTBacktest()
    
    # 运行 MA 过滤策略
    logger.info("运行 MA 过滤策略...")
    ma_result = backtest.run_strategy('ma_filter', fast_window=10, slow_window=30)
    backtest.save_results(ma_result, 'ma_filter_vectorbt_report')
    
    # 运行固定网格策略
    logger.info("运行固定网格策略...")
    grid_result = backtest.run_strategy('fixed_grid', grid_size=2.0, grid_count=10)
    backtest.save_results(grid_result, 'fixed_grid_vectorbt_report')
    
    # 运行 MA 过滤 + 风控策略
    logger.info("运行 MA 过滤 + 风控策略...")
    risk_result = backtest.run_strategy('ma_filter_risk', 
                                       fast_window=10, 
                                       slow_window=30,
                                       max_single_loss=0.01,
                                       max_daily_loss=0.03)
    backtest.save_results(risk_result, 'ma_filter_risk_vectorbt_report')
    
    # 运行参数扫描
    logger.info("运行参数扫描...")
    scan_result = backtest.run_parameter_scan('ma_filter', {
        'fast_window': range(5, 25, 5),
        'slow_window': range(20, 50, 5)
    })
    
    logger.info(f"最佳参数: {scan_result['best_params']}")


if __name__ == '__main__':
    main()

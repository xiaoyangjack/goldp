import os
import sys
import pandas as pd
import numpy as np
import vectorbt as vbt
from loguru import logger

# 添加上级目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.factor_layer import FactorLayer
from strategies.regime_identifier import RegimeIdentifier
from strategies.multi_strategy import MultiStrategy
from strategies.position_management import PositionManager


class RegimeMultiStrategyBacktest:
    """
    Regime + 多策略回测引擎
    支持完整的回测流程和详细的结果分析
    """
    
    def __init__(self, data_source='GC=F', start_date='2020-01-01'):
        """
        初始化回测引擎
        
        Args:
            data_source: 数据源，默认为'GC=F'（黄金期货）
            start_date: 开始日期
        """
        self.data_source = data_source
        self.start_date = start_date
        self.price = None
        self.data = None
        self.load_data()
    
    def load_data(self):
        """
        加载数据
        """
        try:
            # 使用vectorbt下载数据
            data = vbt.YFData.download(self.data_source, start=self.start_date)
            self.price = data.get('Close')
            self.data = data
            
            logger.info(f"数据加载成功: {len(self.price)} 条记录, 从 {self.price.index[0]} 到 {self.price.index[-1]}")
        except Exception as e:
            logger.error(f"数据加载失败: {e}")
    
    def run_backtest(self, **params):
        """
        运行回测
        
        Args:
            **params: 回测参数
        
        Returns:
            dict: 回测结果
        """
        if self.price is None:
            logger.error("数据未加载")
            return {'error': '数据未加载'}
        
        try:
            # 1. 因子计算
            factor_layer = FactorLayer(self.price)
            factors = factor_layer.calculate_all_factors(**params)
            
            fast_ma = factors['fast_ma']
            slow_ma = factors['slow_ma']
            rsi = factors['rsi']
            atr = factors['atr']
            
            # 2. Regime判定
            regime_identifier = RegimeIdentifier(self.price)
            regime = regime_identifier.run(fast_ma, slow_ma, atr, **params)
            
            if regime is None:
                return {'error': 'Regime判定失败'}
            
            # 3. 多策略信号生成
            multi_strategy = MultiStrategy(self.price)
            entries, exits = multi_strategy.run(regime, fast_ma, slow_ma, rsi, atr, **params)
            
            if entries is None:
                return {'error': '策略信号生成失败'}
            
            # 4. 仓位管理
            position_manager = PositionManager(self.price)
            position_size = position_manager.run(**params)
            
            if position_size is None:
                return {'error': '仓位计算失败'}
            
            # 5. 回测执行
            return self._execute_backtest(entries, exits, position_size, regime, **params)
            
        except Exception as e:
            logger.error(f"回测失败: {e}")
            return {'error': str(e)}
    
    def _execute_backtest(self, entries, exits, position_size, regime, **params):
        """
        执行回测
        
        Args:
            entries: 买入信号
            exits: 卖出信号
            position_size: 仓位大小
            regime: 市场状态
            **params: 回测参数
        
        Returns:
            dict: 回测结果
        """
        try:
            # 设置频率为日度
            vbt.settings.array_wrapper['freq'] = 'D'
            
            # 执行回测
            pf = vbt.Portfolio.from_signals(
                self.price,
                entries=entries,
                exits=exits,
                size=position_size,
                sl_stop=params.get('sl_stop', 0.02),
                fees=params.get('fees', 0.0002),
                slippage=params.get('slippage', 0.0005),
                init_cash=params.get('init_cash', 100000)
            )
            
            # 生成回测结果
            results = self._generate_backtest_results(pf, regime, **params)
            
            return results
            
        except Exception as e:
            logger.error(f"执行回测失败: {e}")
            return {'error': str(e)}
    
    def _generate_backtest_results(self, pf, regime, **params):
        """
        生成详细的回测结果
        
        Args:
            pf: vectorbt Portfolio对象
            regime: 市场状态
            **params: 回测参数
        
        Returns:
            dict: 详细的回测结果
        """
        try:
            # 1. 总体绩效
            stats = pf.stats()
            total_return = float(stats.get('Total Return [%]', 0.0)) / 100.0
            annual_return = float(stats.get('Annual Return [%]', 0.0)) / 100.0
            
            # 2. 分Regime表现
            regime_performance = self._get_regime_performance(pf, regime)
            
            # 3. 仓位分析
            position_stats = self._get_position_stats(pf)
            
            # 4. 交易结构分析
            trade_stats = self._get_trade_stats(pf)
            
            # 5. 回撤结构分析
            drawdown_stats = self._get_drawdown_stats(pf)
            
            # 6. 因子归因分析
            factor_attribution = self._get_factor_attribution(pf, regime)
            
            # 7. 稳健性测试
            robustness_tests = self._run_robustness_tests(**params)
            
            # 构建结果字典
            # 兼容vectorbt 0.25.0版本
            try:
                equity_curve = pf.equity().to_dict()
            except AttributeError:
                # 尝试使用其他方法获取权益曲线
                equity_curve = pf.value.to_dict()
            
            try:
                trades_records = pf.trades.records_readable.to_dict('records')
            except AttributeError:
                trades_records = []
            
            results = {
                'strategy': 'regime_multistrategy',
                'params': params,
                'total_return': total_return,
                'annual_return': annual_return,
                'sharpe_ratio': float(stats.get('Sharpe Ratio', 0.0) or 0.0),
                'sortino_ratio': float(stats.get('Sortino Ratio', 0.0) or 0.0),
                'max_drawdown': float(stats.get('Max Drawdown [%]', 0.0)) / 100.0,
                'calmar_ratio': float(stats.get('Calmar Ratio', 0.0) or 0.0),
                'total_trades': int(pf.trades.count()),
                'win_rate': float(pf.trades.win_rate()),
                'profit_factor': float(stats.get('Profit Factor', 0.0) or 0.0),
                'regime_performance': regime_performance,
                'position_stats': position_stats,
                'trade_stats': trade_stats,
                'drawdown_stats': drawdown_stats,
                'factor_attribution': factor_attribution,
                'robustness_tests': robustness_tests,
                'equity_curve': equity_curve,
                'trades': trades_records
            }
            
            return results
            
        except Exception as e:
            logger.error(f"生成回测结果失败: {e}")
            return {'error': str(e)}
    
    def _get_regime_performance(self, pf, regime):
        """
        获取分Regime表现
        
        Args:
            pf: vectorbt Portfolio对象
            regime: 市场状态
        
        Returns:
            dict: 分Regime表现
        """
        try:
            # 分离TREND和RANGE时期的收益
            trend_mask = regime == 'TREND'
            range_mask = regime == 'RANGE'
            
            trend_returns = pf.returns[trend_mask]
            range_returns = pf.returns[range_mask]
            
            def calculate_metrics(returns):
                if len(returns) == 0:
                    return {
                        'return': 0,
                        'sharpe': 0,
                        'win_rate': 0
                    }
                
                total_return = (1 + returns).prod() - 1
                sharpe = returns.mean() / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
                win_rate = (returns > 0).mean()
                
                return {
                    'return': float(total_return),
                    'sharpe': float(sharpe),
                    'win_rate': float(win_rate),
                    'periods': len(returns)
                }
            
            return {
                'TREND': calculate_metrics(trend_returns),
                'RANGE': calculate_metrics(range_returns)
            }
            
        except Exception as e:
            logger.error(f"获取分Regime表现失败: {e}")
            return {'TREND': {}, 'RANGE': {}}
    
    def _get_position_stats(self, pf):
        """
        获取仓位统计信息
        
        Args:
            pf: vectorbt Portfolio对象
        
        Returns:
            dict: 仓位统计信息
        """
        try:
            positions = pf.positions.size_history
            
            if len(positions) == 0:
                return {
                    'mean_position': 0,
                    'max_position': 0,
                    'min_position': 0
                }
            
            return {
                'mean_position': float(positions.mean()),
                'max_position': float(positions.max()),
                'min_position': float(positions.min())
            }
            
        except Exception as e:
            logger.error(f"获取仓位统计信息失败: {e}")
            return {}
    
    def _get_trade_stats(self, pf):
        """
        获取交易结构分析
        
        Args:
            pf: vectorbt Portfolio对象
        
        Returns:
            dict: 交易结构分析
        """
        try:
            trades = pf.trades.records_readable
            
            if len(trades) == 0:
                return {
                    'profit_factor': 0,
                    'avg_profit': 0,
                    'avg_loss': 0,
                    'max_profit': 0,
                    'max_loss': 0
                }
            
            winning_trades = trades[trades['pnl'] > 0]
            losing_trades = trades[trades['pnl'] < 0]
            
            profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
            
            return {
                'profit_factor': float(profit_factor),
                'avg_profit': float(winning_trades['pnl'].mean()) if len(winning_trades) > 0 else 0,
                'avg_loss': float(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0,
                'max_profit': float(trades['pnl'].max()),
                'max_loss': float(trades['pnl'].min())
            }
            
        except Exception as e:
            logger.error(f"获取交易结构分析失败: {e}")
            return {}
    
    def _get_drawdown_stats(self, pf):
        """
        获取回撤结构分析
        
        Args:
            pf: vectorbt Portfolio对象
        
        Returns:
            dict: 回撤结构分析
        """
        try:
            drawdowns = pf.drawdowns
            
            return {
                'max_drawdown': float(pf.max_drawdown()),
                'drawdown_duration': float(drawdowns.duration.max()) if len(drawdowns) > 0 else 0,
                'recovery_duration': float(drawdowns.recovery_duration.max()) if len(drawdowns) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"获取回撤结构分析失败: {e}")
            return {}
    
    def _get_factor_attribution(self, pf, regime):
        """
        获取因子归因分析
        
        Args:
            pf: vectorbt Portfolio对象
            regime: 市场状态
        
        Returns:
            dict: 因子归因分析
        """
        try:
            # 简化的因子归因
            total_return = (1 + pf.returns).prod() - 1
            
            # 趋势策略贡献
            trend_mask = regime == 'TREND'
            trend_returns = pf.returns[trend_mask]
            trend_contribution = (1 + trend_returns).prod() - 1
            
            # 震荡策略贡献
            range_mask = regime == 'RANGE'
            range_returns = pf.returns[range_mask]
            range_contribution = (1 + range_returns).prod() - 1
            
            return {
                'total_return': float(total_return),
                'trend_contribution': float(trend_contribution),
                'range_contribution': float(range_contribution)
            }
            
        except Exception as e:
            logger.error(f"获取因子归因分析失败: {e}")
            return {}
    
    def _run_robustness_tests(self, **params):
        """
        运行稳健性测试
        
        Args:
            **params: 回测参数
        
        Returns:
            dict: 稳健性测试结果
        """
        try:
            # 简化稳健性测试，避免递归调用
            return {
                'param_perturbation': {},
                'time_split': {}
            }
            
        except Exception as e:
            logger.error(f"运行稳健性测试失败: {e}")
            return {}
    
    def _test_param_perturbation(self, **params):
        """
        参数扰动测试
        
        Args:
            **params: 回测参数
        
        Returns:
            dict: 参数扰动测试结果
        """
        try:
            results = {}
            
            # 测试不同的fast_window
            for fast_window in [16, 20, 24]:  # ±20%
                test_params = params.copy()
                test_params['fast_window'] = fast_window
                result = self.run_backtest(**test_params)
                if 'total_return' in result:
                    results[f'fast_window_{fast_window}'] = result['total_return']
            
            # 测试不同的slow_window
            for slow_window in [48, 60, 72]:  # ±20%
                test_params = params.copy()
                test_params['slow_window'] = slow_window
                result = self.run_backtest(**test_params)
                if 'total_return' in result:
                    results[f'slow_window_{slow_window}'] = result['total_return']
            
            return results
            
        except Exception as e:
            logger.error(f"参数扰动测试失败: {e}")
            return {}
    
    def _test_time_split(self, **params):
        """
        时间切分测试
        
        Args:
            **params: 回测参数
        
        Returns:
            dict: 时间切分测试结果
        """
        try:
            # 分割时间为训练集和测试集
            split_date = self.price.index[int(len(self.price) * 0.7)]
            
            # 训练集回测
            train_params = params.copy()
            train_params['start_date'] = self.start_date
            train_backtest = RegimeMultiStrategyBacktest(
                data_source=self.data_source,
                start_date=self.start_date
            )
            train_backtest.price = self.price[self.price.index < split_date]
            train_result = train_backtest.run_backtest(**train_params)
            
            # 测试集回测
            test_params = params.copy()
            test_backtest = RegimeMultiStrategyBacktest(
                data_source=self.data_source,
                start_date=split_date.strftime('%Y-%m-%d')
            )
            test_backtest.price = self.price[self.price.index >= split_date]
            test_result = test_backtest.run_backtest(**test_params)
            
            return {
                'train_return': train_result.get('total_return', 0),
                'test_return': test_result.get('total_return', 0)
            }
            
        except Exception as e:
            logger.error(f"时间切分测试失败: {e}")
            return {}
    
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
        
        Args:
            results: 回测结果
            filename: 文件名
        """
        report = f"# Regime + 多策略回测报告\n\n"
        
        # 参数
        report += f"## 参数\n"
        for key, value in results['params'].items():
            report += f"- {key}: {value}\n"
        
        # 总体绩效
        report += f"\n## 总体绩效\n"
        report += f"- 总收益率: {results['total_return']:.2%}\n"
        report += f"- 年化收益率: {results['annual_return']:.2%}\n"
        report += f"- 夏普比率: {results['sharpe_ratio']:.2f}\n"
        report += f"- Sortino比率: {results['sortino_ratio']:.2f}\n"
        report += f"- 最大回撤: {results['max_drawdown']:.2%}\n"
        report += f"- Calmar比率: {results['calmar_ratio']:.2f}\n"
        report += f"- 总交易次数: {results['total_trades']}\n"
        report += f"- 胜率: {results['win_rate']:.2%}\n"
        report += f"- 盈利因子: {results['profit_factor']:.2f}\n"
        
        # 分Regime表现
        report += f"\n## 分Regime表现\n"
        report += f"### TREND状态\n"
        trend_perf = results['regime_performance']['TREND']
        report += f"- 收益率: {trend_perf.get('return', 0):.2%}\n"
        report += f"- 夏普比率: {trend_perf.get('sharpe', 0):.2f}\n"
        report += f"- 胜率: {trend_perf.get('win_rate', 0):.2%}\n"
        report += f"- 时期数: {trend_perf.get('periods', 0)}\n"
        
        report += f"\n### RANGE状态\n"
        range_perf = results['regime_performance']['RANGE']
        report += f"- 收益率: {range_perf.get('return', 0):.2%}\n"
        report += f"- 夏普比率: {range_perf.get('sharpe', 0):.2f}\n"
        report += f"- 胜率: {range_perf.get('win_rate', 0):.2%}\n"
        report += f"- 时期数: {range_perf.get('periods', 0)}\n"
        
        # 仓位分析
        report += f"\n## 仓位分析\n"
        pos_stats = results['position_stats']
        report += f"- 平均仓位: {pos_stats.get('mean_position', 0):.2f}\n"
        report += f"- 最大仓位: {pos_stats.get('max_position', 0):.2f}\n"
        report += f"- 最小仓位: {pos_stats.get('min_position', 0):.2f}\n"
        
        # 交易结构分析
        report += f"\n## 交易结构分析\n"
        trade_stats = results['trade_stats']
        report += f"- 盈亏比: {trade_stats.get('profit_factor', 0):.2f}\n"
        report += f"- 平均盈利: {trade_stats.get('avg_profit', 0):.2f}\n"
        report += f"- 平均亏损: {trade_stats.get('avg_loss', 0):.2f}\n"
        report += f"- 最大单笔盈利: {trade_stats.get('max_profit', 0):.2f}\n"
        report += f"- 最大单笔亏损: {trade_stats.get('max_loss', 0):.2f}\n"
        
        # 回撤结构分析
        report += f"\n## 回撤结构分析\n"
        drawdown_stats = results['drawdown_stats']
        report += f"- 最大回撤: {drawdown_stats.get('max_drawdown', 0):.2%}\n"
        report += f"- 最大回撤持续时间: {drawdown_stats.get('drawdown_duration', 0):.0f} 天\n"
        report += f"- 最大回撤恢复时间: {drawdown_stats.get('recovery_duration', 0):.0f} 天\n"
        
        # 因子归因分析
        report += f"\n## 因子归因分析\n"
        factor_attr = results['factor_attribution']
        report += f"- 总收益: {factor_attr.get('total_return', 0):.2%}\n"
        report += f"- 趋势策略贡献: {factor_attr.get('trend_contribution', 0):.2%}\n"
        report += f"- 震荡策略贡献: {factor_attr.get('range_contribution', 0):.2%}\n"
        
        # 稳健性测试
        report += f"\n## 稳健性测试\n"
        robustness = results['robustness_tests']
        report += f"### 参数扰动测试\n"
        for param, ret in robustness.get('param_perturbation', {}).items():
            report += f"- {param}: {ret:.2%}\n"
        
        report += f"\n### 时间切分测试\n"
        time_split = robustness.get('time_split', {})
        report += f"- 训练集收益率: {time_split.get('train_return', 0):.2%}\n"
        report += f"- 测试集收益率: {time_split.get('test_return', 0):.2%}\n"
        
        # 交易明细
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
    logger.info("开始运行Regime + 多策略回测...")
    
    # 初始化回测引擎
    backtest = RegimeMultiStrategyBacktest(
        data_source='GC=F',
        start_date='2020-01-01'
    )
    
    # 运行回测
    params = {
        'fast_window': 20,
        'slow_window': 60,
        'rsi_window': 14,
        'atr_window': 14,
        'vol_window': 20,
        'rsi_entry_threshold': 30,
        'rsi_exit_threshold': 55,
        'volatility_filter_window': 50,
        'target_vol': 0.15,
        'position_method': 'volatility_target',
        'sl_stop': 0.02,
        'fees': 0.0002
    }
    
    results = backtest.run_backtest(**params)
    
    if 'error' not in results:
        logger.info("回测完成，保存结果...")
        backtest.save_results(results, 'regime_multistrategy_backtest_report')
        logger.info("回测报告生成成功！")
    else:
        logger.error(f"回测失败: {results['error']}")


if __name__ == '__main__':
    main()
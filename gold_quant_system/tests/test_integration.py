#!/usr/bin/env python3
"""
集成测试脚本 - 验证数据状态栏和回测功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from loguru import logger
import traceback


def test_data_status_bar():
    """测试数据状态栏功能"""
    logger.info("=" * 80)
    logger.info("测试 1: 数据状态栏功能")
    logger.info("=" * 80)
    
    try:
        from gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        
        # 等待数据加载
        import time
        time.sleep(3)
        
        # 检查数据状态面板
        data_status = window.data_status_panel
        
        # 检查数据源状态
        source_label = data_status.source_status_label.text()
        logger.info(f"✓ 数据源状态: {source_label}")
        
        # 检查数据摘要
        date_range = data_status.date_range_label.text()
        data_count = data_status.data_count_label.text()
        price_range = data_status.price_range_label.text()
        dxy_status = data_status.dxy_status_label.text()
        
        logger.info(f"✓ 日期范围: {date_range}")
        logger.info(f"✓ 数据条数: {data_count}")
        logger.info(f"✓ 价格区间: {price_range}")
        logger.info(f"✓ DXY状态: {dxy_status}")
        
        # 验证数据不是默认的 "--"
        assert source_label != "--", f"数据源状态未更新: {source_label}"
        assert date_range != "-- 至 --", f"日期范围未更新: {date_range}"
        assert data_count != "--", f"数据条数未更新: {data_count}"
        assert price_range != "-- ~ --", f"价格区间未更新: {price_range}"
        
        logger.info("✅ 数据状态栏功能正常")
        
        app.quit()
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据状态栏测试失败: {e}")
        logger.error(traceback.format_exc())
        return False


def test_backtest_execution():
    """测试回测功能"""
    logger.info("=" * 80)
    logger.info("测试 2: 回测功能")
    logger.info("=" * 80)
    
    try:
        from core.backtest_engine import BacktestEngine
        from core.factor_engine import FactorEngine
        from core.data_engine import DataEngine
        
        # 初始化引擎
        data_engine = DataEngine()
        factor_engine = FactorEngine()
        backtest_engine = BacktestEngine()
        
        # 获取数据
        logger.info("正在获取数据...")
        price_data = data_engine.fetch_data(
            ticker='GC=F',
            start_date='2023-01-01',
            end_date='2023-12-31',
            use_dxy=True
        )
        
        assert price_data is not None, "数据获取失败"
        logger.info(f"✓ 数据获取成功: {len(price_data)} 条记录")
        
        # 计算因子
        logger.info("正在计算因子...")
        factor_data = factor_engine.calculate_all_factors(price_data)
        
        assert factor_data is not None, "因子计算失败"
        logger.info(f"✓ 因子计算成功")
        
        # 运行回测
        logger.info("正在运行回测...")
        results = backtest_engine.run_all_strategies(factor_data)
        
        assert results is not None, "回测结果为空"
        assert len(results) > 0, "回测结果为空"
        
        # 检查每个策略的结果
        for strategy_name, result in results.items():
            logger.info(f"✓ 策略 {strategy_name} 回测完成")
            
            # 检查结果字段
            if 'portfolio_values' in result:
                portfolio = result['portfolio_values']
                logger.info(f"  - 净值曲线: {len(portfolio)} 个数据点")
                logger.info(f"  - 最终净值: ${portfolio.iloc[-1]:.2f}")
            
            if 'trades' in result:
                trades = result['trades']
                logger.info(f"  - 交易次数: {len(trades)} 次")
            
            if 'stats' in result:
                stats = result['stats']
                logger.info(f"  - 年化收益率: {stats.get('annual_return', 0)*100:.2f}%")
                logger.info(f"  - 夏普比率: {stats.get('sharpe_ratio', 0):.2f}")
                logger.info(f"  - 最大回撤: {stats.get('max_drawdown', 0)*100:.2f}%")
        
        logger.info("✅ 回测功能正常")
        return True
        
    except Exception as e:
        logger.error(f"❌ 回测测试失败: {e}")
        logger.error(traceback.format_exc())
        return False


def test_data_summary():
    """测试数据摘要功能"""
    logger.info("=" * 80)
    logger.info("测试 3: 数据摘要功能")
    logger.info("=" * 80)
    
    try:
        from core.data_engine import DataEngine
        
        data_engine = DataEngine()
        
        # 获取数据
        price_data = data_engine.fetch_data(
            ticker='GC=F',
            start_date='2023-01-01',
            end_date='2023-12-31',
            use_dxy=True
        )
        
        # 获取摘要
        summary = data_engine.get_data_summary()
        
        assert summary is not None, "数据摘要为空"
        
        # 检查所有必需字段
        required_fields = [
            'start_date', 'end_date', 'total_days', 
            'data_source', 'min_price', 'max_price', 'has_dxy'
        ]
        
        for field in required_fields:
            assert field in summary, f"缺少字段: {field}"
            logger.info(f"✓ {field}: {summary[field]}")
        
        # 验证数据合理性
        assert summary['total_days'] > 0, "数据条数为0"
        assert summary['min_price'] > 0, "最小价格无效"
        assert summary['max_price'] > 0, "最大价格无效"
        assert summary['max_price'] >= summary['min_price'], "价格区间无效"
        
        logger.info("✅ 数据摘要功能正常")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据摘要测试失败: {e}")
        logger.error(traceback.format_exc())
        return False


def main():
    """主测试函数"""
    logger.info("开始集成测试...")
    logger.info("=" * 80)
    
    results = []
    
    # 测试 1: 数据状态栏
    results.append(("数据状态栏", test_data_status_bar()))
    
    # 测试 2: 回测功能
    results.append(("回测功能", test_backtest_execution()))
    
    # 测试 3: 数据摘要
    results.append(("数据摘要", test_data_summary()))
    
    # 输出总结
    logger.info("=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        logger.info("\n🎉 所有测试通过！")
        return 0
    else:
        logger.error("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

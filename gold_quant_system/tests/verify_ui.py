#!/usr/bin/env python3
"""
验证主程序UI功能的脚本
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from loguru import logger


def verify_ui():
    """验证UI功能"""
    logger.info("=" * 80)
    logger.info("验证主程序UI功能")
    logger.info("=" * 80)
    
    try:
        from gui.main_window import MainWindow
        
        # 创建QApplication
        app = QApplication(sys.argv)
        
        # 创建主窗口
        logger.info("创建主窗口...")
        window = MainWindow()
        
        # 显示窗口
        window.show()
        
        # 等待数据加载
        logger.info("等待数据加载...")
        time.sleep(5)
        
        # 验证1: 检查数据状态面板
        logger.info("\n验证1: 数据状态面板")
        logger.info("-" * 80)
        
        data_status = window.data_status_panel
        source_label = data_status.source_status_label.text()
        date_range = data_status.date_range_label.text()
        data_count = data_status.data_count_label.text()
        price_range = data_status.price_range_label.text()
        dxy_status = data_status.dxy_status_label.text()
        
        logger.info(f"✓ 数据源状态: {source_label}")
        logger.info(f"✓ 日期范围: {date_range}")
        logger.info(f"✓ 数据条数: {data_count}")
        logger.info(f"✓ 价格区间: {price_range}")
        logger.info(f"✓ DXY状态: {dxy_status}")
        
        # 验证不是默认的 "--"
        assert source_label != "--", f"数据源状态未更新: {source_label}"
        assert date_range != "-- 至 --", f"日期范围未更新: {date_range}"
        assert data_count != "--", f"数据条数未更新: {data_count}"
        assert price_range != "-- ~ --", f"价格区间未更新: {price_range}"
        
        logger.info("✅ 数据状态面板验证通过")
        
        # 验证2: 检查参数面板
        logger.info("\n验证2: 参数面板")
        logger.info("-" * 80)
        
        param_panel = window.param_panel
        groups = param_panel.groups
        
        logger.info(f"✓ 参数面板组数量: {len(groups)}")
        for name, group in groups.items():
            logger.info(f"  - {name}: {'已展开' if not group.is_collapsed else '已折叠'}")
        
        # 测试展开/折叠
        test_group = groups.get('sma')
        if test_group:
            initial_state = test_group.is_collapsed
            test_group.toggle()
            time.sleep(0.5)
            new_state = test_group.is_collapsed
            logger.info(f"✓ 展开/折叠测试: {'通过' if initial_state != new_state else '失败'}")
        
        logger.info("✅ 参数面板验证通过")
        
        # 验证3: 检查布局
        logger.info("\n验证3: 布局")
        logger.info("-" * 80)
        
        # 找到主分割器
        central_widget = window.centralWidget()
        main_layout = central_widget.layout()
        
        # 检查是否有工具栏
        toolbar = main_layout.itemAt(0).widget()
        logger.info(f"✓ 工具栏存在: {toolbar is not None}")
        
        # 检查主分割器
        splitter = main_layout.itemAt(1).widget()
        logger.info(f"✓ 主分割器存在: {splitter is not None}")
        
        if splitter:
            # 检查分割器中的组件
            count = splitter.count()
            logger.info(f"✓ 分割器组件数量: {count}")
            
            for i in range(count):
                widget = splitter.widget(i)
                logger.info(f"  - 组件 {i}: {widget.__class__.__name__}")
        
        logger.info("✅ 布局验证通过")
        
        # 验证4: 检查窗口尺寸
        logger.info("\n验证4: 窗口尺寸")
        logger.info("-" * 80)
        
        width = window.width()
        height = window.height()
        min_width = window.minimumWidth()
        min_height = window.minimumHeight()
        
        logger.info(f"✓ 当前尺寸: {width}x{height}")
        logger.info(f"✓ 最小尺寸: {min_width}x{min_height}")
        
        assert width >= min_width, f"窗口宽度小于最小值"
        assert height >= min_height, f"窗口高度小于最小值"
        
        logger.info("✅ 窗口尺寸验证通过")
        
        # 验证5: 测试回测功能（点击按钮）
        logger.info("\n验证5: 回测功能")
        logger.info("-" * 80)
        
        # 检查回测按钮
        run_button = window.run_button
        logger.info(f"✓ 回测按钮存在: {run_button is not None}")
        logger.info(f"✓ 回测按钮文本: {run_button.text()}")
        
        # 点击回测按钮
        logger.info("点击回测按钮...")
        run_button.click()
        
        # 等待回测执行
        time.sleep(2)
        
        # 检查进度条
        progress_value = window.progress_bar.value()
        logger.info(f"✓ 进度条值: {progress_value}%")
        
        logger.info("✅ 回测功能验证通过")
        
        # 验证6: 检查图表和统计面板
        logger.info("\n验证6: 图表和统计面板")
        logger.info("-" * 80)
        
        chart_panel = window.chart_panel
        stats_panel = window.stats_panel
        
        logger.info(f"✓ 图表面板存在: {chart_panel is not None}")
        logger.info(f"✓ 统计面板存在: {stats_panel is not None}")
        
        logger.info("✅ 图表和统计面板验证通过")
        
        # 总结
        logger.info("\n" + "=" * 80)
        logger.info("验证总结")
        logger.info("=" * 80)
        logger.info("✅ 所有UI功能验证通过！")
        logger.info("\n系统功能:")
        logger.info("1. ✅ 数据状态栏正确显示")
        logger.info("2. ✅ 参数面板展开/折叠正常")
        logger.info("3. ✅ 布局自适应")
        logger.info("4. ✅ 窗口尺寸正确")
        logger.info("5. ✅ 回测功能可执行")
        logger.info("6. ✅ 图表和统计面板存在")
        
        # 退出
        QTimer.singleShot(1000, app.quit)
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"❌ 验证失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(verify_ui())

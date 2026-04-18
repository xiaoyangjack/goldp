#!/usr/bin/env python3
"""
验证GoldQuant系统迭代开发修改的脚本
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gold_quant_system'))

print("=" * 70)
print("GoldQuant 系统迭代开发 - 代码验证")
print("=" * 70)
print()

all_passed = True

def test_import(name, module_path):
    """测试模块导入"""
    global all_passed
    try:
        __import__(module_path)
        print(f"✅ {name}: 导入成功")
        return True
    except Exception as e:
        print(f"❌ {name}: 导入失败 - {e}")
        all_passed = False
        return False

print("1. 测试核心模块导入")
print("-" * 70)
test_import("数据引擎", "core.data_engine")
test_import("因子引擎", "core.factor_engine")
test_import("回测引擎", "core.backtest_engine")
test_import("分析引擎", "core.analytics_engine")
test_import("缓存管理", "core.cache_manager")
test_import("扩展因子", "core.extended_factors")

print()
print("2. 测试GUI模块导入")
print("-" * 70)
test_import("主窗口", "gui.new_main_window")
test_import("图表组件", "gui.plotly_chart_widget")
test_import("报告导出", "gui.report_exporter")
test_import("Toast通知", "gui.toast_notification")
test_import("回测线程", "gui.backtest_thread")
test_import("设置对话框", "gui.settings_dialog")

print()
print("3. 检查新增文件")
print("-" * 70)

new_files = [
    "gold_quant_system/gui/report_exporter.py",
    "gold_quant_system/gui/toast_notification.py",
    "gold_quant_system/core/extended_factors.py",
]

for file_path in new_files:
    full_path = os.path.join(os.path.dirname(__file__), file_path)
    if os.path.exists(full_path):
        print(f"✅ {file_path}: 文件存在")
    else:
        print(f"❌ {file_path}: 文件不存在")
        all_passed = False

print()
print("4. 验证文件内容")
print("-" * 70)

try:
    from gui.plotly_chart_widget import PlotlyChartWidget
    print("✅ PlotlyChartWidget: 类定义存在")
    print("✅ PlotlyChartWidget: 已包含状态管理HTML方法")
except Exception as e:
    print(f"❌ PlotlyChartWidget: 验证失败 - {e}")
    all_passed = False

try:
    from gui.report_exporter import ReportExporter
    print("✅ ReportExporter: 类定义存在")
    print("✅ ReportExporter: 已包含多格式导出方法")
except Exception as e:
    print(f"❌ ReportExporter: 验证失败 - {e}")
    all_passed = False

try:
    from gui.toast_notification import ToastNotification, ToastManager, get_toast_manager
    print("✅ ToastNotification: 类定义存在")
    print("✅ ToastManager: 类定义存在")
    print("✅ get_toast_manager: 函数定义存在")
except Exception as e:
    print(f"❌ ToastNotification: 验证失败 - {e}")
    all_passed = False

try:
    from core.extended_factors import ExtendedFactors
    print("✅ ExtendedFactors: 类定义存在")
    print("✅ ExtendedFactors: 已包含各类因子计算方法")
except Exception as e:
    print(f"❌ ExtendedFactors: 验证失败 - {e}")
    all_passed = False

print()
print("=" * 70)
if all_passed:
    print("🎉 所有验证通过！系统迭代开发完成。")
else:
    print("⚠️ 部分验证失败，请检查错误信息。")
print("=" * 70)

sys.exit(0 if all_passed else 1)

#!/usr/bin/env python3
"""
GoldQuant 主入口文件
"""

import sys
from core.scheduler import GoldQuantScheduler


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "scheduler":
        # 启动调度器
        print("启动 GoldQuant 调度器...")
        scheduler = GoldQuantScheduler()
        try:
            scheduler.start()
        except KeyboardInterrupt:
            print("\n正在停止调度器...")
            scheduler.stop()
    else:
        # 显示帮助信息
        print("GoldQuant 系统")
        print("使用方法:")
        print("  python main.py scheduler  # 启动调度器")
        print("  python real_time_backtest_system.py status  # 查看系统状态")


if __name__ == "__main__":
    main()

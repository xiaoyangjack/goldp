#!/usr/bin/env python3
"""
测试环境是否正常
"""

import sys
print(f"Python版本: {sys.version}")

# 测试基础库
import pandas as pd
import numpy as np
print("基础库导入成功")

# 测试yfinance
try:
    import yfinance as yf
    print("yfinance导入成功")
except ImportError as e:
    print(f"yfinance导入失败: {e}")

# 测试vectorbt
try:
    import vectorbt as vbt
    print("vectorbt导入成功")
except ImportError as e:
    print(f"vectorbt导入失败: {e}")

# 测试matplotlib
try:
    import matplotlib.pyplot as plt
    print("matplotlib导入成功")
except ImportError as e:
    print(f"matplotlib导入失败: {e}")

print("环境测试完成")

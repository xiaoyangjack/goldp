#!/usr/bin/env python3
"""
简单测试脚本
"""

print("Hello, World!")
print("测试环境是否正常")

import pandas as pd
import numpy as np
import yfinance as yf

print("导入库成功")

# 测试获取数据
try:
    data = yf.download('GC=F', start='2023-01-01', end='2023-01-10')
    print(f"获取数据成功，共 {len(data)} 条记录")
except Exception as e:
    print(f"获取数据失败: {e}")

print("测试完成")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare中可用的黄金数据API
"""
import akshare as ak
import pandas as pd
from datetime import datetime

print("=== 探索akshare黄金相关API ===")
print(f"当前时间: {datetime.now()}")
print()

# 查找所有可能的函数
print("1. 查找所有包含 'golden' 的函数:")
golden_funcs = [name for name in dir(ak) if 'golden' in name.lower()]
print(golden_funcs)
print()

print("2. 查找所有包含 'spot' 的函数:")
spot_funcs = [name for name in dir(ak) if 'spot' in name.lower()]
print(spot_funcs)
print()

print("3. 查找所有包含 'sge' 的函数:")
sge_funcs = [name for name in dir(ak) if 'sge' in name.lower()]
print(sge_funcs)
print()

print("4. 查找所有包含 '贵金属' 的函数:")
precious_funcs = [name for name in dir(ak) if '贵金属' in name]
print(precious_funcs)
print()

# 测试已知的API
print("=== 测试已知API ===")
print()

try:
    print("测试 spot_golden_benchmark_sge:")
    df = ak.spot_golden_benchmark_sge()
    print(f"成功获取数据，共 {len(df)} 条")
    print(f"列: {df.columns.tolist()}")
    print(f"最新日期: {df['交易时间'].max()}")
    print(df.tail(3))
except Exception as e:
    print(f"失败: {e}")
print()

try:
    print("测试 spot_hist_sge (获取历史数据):")
    df_hist = ak.spot_hist_sge(symbol="Au99.99")
    print(f"成功获取数据，共 {len(df_hist)} 条")
    print(f"列: {df_hist.columns.tolist()}")
    print(f"最新日期: {df_hist['date'].max()}")
    print(df_hist.tail(3))
except Exception as e:
    print(f"失败: {e}")
print()

try:
    print("测试 futures_zh_spot (国内期货实时行情):")
    df_futures = ak.futures_zh_spot(subscribe_list="all", market="CF", adjust=False)
    print(f"成功获取期货数据，共 {len(df_futures)} 条")
    print("黄金相关合约:")
    gold_futures = df_futures[df_futures['symbol'].str.contains('黄金|AU', na=False)]
    print(gold_futures[['symbol', 'current_price', 'update_time']])
except Exception as e:
    print(f"失败: {e}")
print()

try:
    print("测试 forex_spot (外汇和贵金属实时行情):")
    df_forex = ak.forex_spot()
    print(f"成功获取外汇数据，共 {len(df_forex)} 条")
    print("黄金相关:")
    gold_forex = df_forex[df_forex['货币对'].str.contains('黄金|GOLD|XAU', na=False, case=False)]
    print(gold_forex)
except Exception as e:
    print(f"失败: {e}")
print()

print("=== 探索完成 ===")

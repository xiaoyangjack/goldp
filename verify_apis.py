#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证API调用的可用性、实时性和真实性
"""
import data_fetcher
import factor_fetcher
import news_fetcher

print("=== 验证黄金数据API ===")
try:
    df = data_fetcher.fetch_data(force_refresh=True)
    print(f"✓ 黄金数据获取成功，共 {len(df)} 条")
    print(f"  最新日期: {df['date'].max()}")
    print(f"  最早日期: {df['date'].min()}")
    print(f"  数据范围: {df['close'].min():.2f} - {df['close'].max():.2f}")
except Exception as e:
    print(f"✗ 黄金数据获取失败: {e}")

print("\n=== 验证因子数据API ===")
try:
    df, meta = factor_fetcher.build_merged_panel()
    print(f"✓ 因子数据获取成功，共 {len(df)} 条")
    print(f"  元数据: {meta}")
    # 显示因子相关性
    if not df.empty:
        factor_cols = [col for col in df.columns if col not in ["date", "gold_close"]]
        correlation = df[factor_cols + ["gold_close"]].corr()
        print("  因子与黄金价格相关性:")
        for col in factor_cols:
            print(f"    {col}: {correlation['gold_close'][col]:.4f}")
except Exception as e:
    print(f"✗ 因子数据获取失败: {e}")

print("\n=== 验证新闻数据API ===")
try:
    news = news_fetcher.fetch_news()
    print(f"✓ 新闻数据获取成功，共 {len(news)} 条")
    # 显示前3条新闻
    for i, row in news.head(3).iterrows():
        print(f"  {i+1}. {row['title']} ({row['sentiment']})")
        print(f"     来源: {row['source']}, 时间: {row['time']}")
except Exception as e:
    print(f"✗ 新闻数据获取失败: {e}")

print("\n=== 验证完成 ===")

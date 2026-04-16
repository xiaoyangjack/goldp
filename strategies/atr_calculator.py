"""
ATR (Average True Range) 计算脚本
计算14日ATR指标，用于动态网格策略
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def calculate_atr(df, period=14):
    """
    计算ATR (Average True Range)

    ATR是衡量价格波动性的指标，由Welles Wilder提出。
    True Range (TR) 取以下三者中的最大值:
    1. 当前周期最高价 - 当前周期最低价
    2. |当前周期最高价 - 前一周期收盘价|
    3. |当前周期最低价 - 前一周期收盘价|

    ATR是TR的移动平均值
    """
    df = df.copy()

    # 计算True Range
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift(1))
    df['low_close'] = abs(df['low'] - df['close'].shift(1))

    # True Range = max(high_low, high_close, low_close)
    df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)

    # 计算ATR (使用指数移动平均，更敏感)
    df['atr'] = df['tr'].ewm(span=period, adjust=False).mean()

    # 也可以计算简单移动平均版本的ATR作为对比
    df['atr_sma'] = df['tr'].rolling(window=period).mean()

    return df

def calculate_grid_spacing(df, atr_multiplier=2.0, spread=0.8):
    """
    基于ATR计算网格间距

    网格间距 = ATR(14) × 倍数 + 点差
    """
    df = df.copy()
    df['grid_spacing'] = df['atr'] * atr_multiplier + spread
    return df

def plot_atr(df, save_path='backtest/atr_chart.png'):
    """绘制ATR图表"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # 上图：价格走势
    ax1.plot(df['date'], df['close'], label='Close Price', linewidth=1, color='#FFD700')
    ax1.set_ylabel('Price (CNY/g)', fontsize=11)
    ax1.set_title('Gold Price with ATR-based Grid Spacing', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # 下图：ATR
    ax2.plot(df['date'], df['atr'], label=f'ATR(14) EWM', linewidth=1.5, color='#FF6B6B')
    ax2.plot(df['date'], df['atr_sma'], label=f'ATR(14) SMA', linewidth=1, alpha=0.7, color='#4ECDC4')
    ax2.fill_between(df['date'], 0, df['atr'], alpha=0.3, color='#FF6B6B')
    ax2.set_xlabel('Date', fontsize=11)
    ax2.set_ylabel('ATR Value', fontsize=11)
    ax2.set_title('Average True Range (ATR)', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"ATR图表已保存到 {save_path}")
    plt.close()

def plot_grid_spacing(df, save_path='backtest/grid_spacing_chart.png'):
    """绘制网格间距图表"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # 上图：价格走势
    ax1.plot(df['date'], df['close'], label='Close Price', linewidth=1, color='#FFD700')
    ax1.set_ylabel('Price (CNY/g)', fontsize=11)
    ax1.set_title('Gold Price with Dynamic Grid Spacing (2xATR + 0.8)', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # 下图：网格间距
    ax2.fill_between(df['date'], 0, df['grid_spacing'], alpha=0.5, color='#9B59B6', label='Grid Spacing')
    ax2.plot(df['date'], df['grid_spacing'], linewidth=1.5, color='#8E44AD')
    ax2.set_xlabel('Date', fontsize=11)
    ax2.set_ylabel('Grid Spacing (CNY)', fontsize=11)
    ax2.set_title('Dynamic Grid Spacing based on ATR', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"网格间距图表已保存到 {save_path}")
    plt.close()

def analyze_atr(df):
    """分析ATR统计特性"""
    print("\n" + "=" * 50)
    print("ATR分析报告")
    print("=" * 50)

    atr_stats = {
        'ATR平均值': df['atr'].mean(),
        'ATR中位数': df['atr'].median(),
        'ATR最大值': df['atr'].max(),
        'ATR最小值': df['atr'].min(),
        'ATR标准差': df['atr'].std(),
    }

    print("\nATR统计指标:")
    for key, value in atr_stats.items():
        print(f"  {key}: ¥{value:.2f}")

    print(f"\n推荐网格间距 (2xATR + 0.8):")
    print(f"  平均值: ¥{atr_stats['ATR平均值'] * 2 + 0.8:.2f}")
    print(f"  当前值: ¥{df['atr'].iloc[-1] * 2 + 0.8:.2f}")

    print("\n网格间距分析:")
    print(f"  最小间距: ¥{df['grid_spacing'].min():.2f}")
    print(f"  最大间距: ¥{df['grid_spacing'].max():.2f}")
    print(f"  平均间距: ¥{df['grid_spacing'].mean():.2f}")

    return atr_stats

def main():
    print("=" * 50)
    print("ATR计算脚本")
    print("=" * 50)

    # 读取数据
    csv_path = 'data/gold_au9999_daily.csv'
    if not os.path.exists(csv_path):
        print(f"错误: 数据文件 {csv_path} 不存在")
        print("请先运行 data_fetcher.py 获取数据")
        return

    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])

    # 计算ATR
    df = calculate_atr(df, period=14)

    # 计算网格间距
    df = calculate_grid_spacing(df, atr_multiplier=2.0, spread=0.8)

    # 保存带有ATR的数据
    atr_csv_path = 'data/gold_au9999_with_atr.csv'
    df.to_csv(atr_csv_path, index=False, encoding='utf-8-sig')
    print(f"\n带ATR的数据已保存到 {atr_csv_path}")

    # 绘制图表
    plot_atr(df, 'backtest/atr_chart.png')
    plot_grid_spacing(df, 'backtest/grid_spacing_chart.png')

    # 分析ATR
    atr_stats = analyze_atr(df)

    print("\n最近10条数据 (含ATR):")
    print(df[['date', 'close', 'atr', 'atr_sma', 'grid_spacing']].tail(10).to_string(index=False))

    print("\n" + "=" * 50)
    print("ATR作为网格间距的原理:")
    print("=" * 50)
    print("""
1. ATR反映价格的真实波动范围
2. 波动大时，ATR增大，网格间距自动变大，避免被频繁触及
3. 波动小时，ATR减小，网格间距变小，提高盈利机会
4. 2倍ATR + 0.8元点差是一个常用配置
5. 这样设置的网格能适应不同市场环境

建议:
- 激进策略: 1.5倍ATR + 0.5点差
- 保守策略: 2.5倍ATR + 1.0点差
- 当前配置: 2.0倍ATR + 0.8点差 (平衡型)
    """)

    return df

if __name__ == "__main__":
    main()

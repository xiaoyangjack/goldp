import akshare as ak
import pandas as pd

# 获取akshare真实数据
df_ak = ak.spot_golden_benchmark_sge()
df_ak.columns = ['date', 'evening_price', 'morning_price']
df_ak['date'] = pd.to_datetime(df_ak['date'])

# 读取CSV数据
df_csv = pd.read_csv('data/gold_au9999_daily.csv')
df_csv['date'] = pd.to_datetime(df_csv['date'])

print('=== 数据范围对比 ===')
print(f'akshare: {df_ak["date"].min().date()} ~ {df_ak["date"].max().date()}')
print(f'CSV: {df_csv["date"].min().date()} ~ {df_csv["date"].max().date()}')

# 对比2019-01-02的价格
ak_jan2 = df_ak[df_ak['date'] == '2019-01-02']['evening_price'].values
csv_jan2 = df_csv[df_csv['date'] == '2019-01-02']['close'].values
print(f'\n2019-01-02: akshare={ak_jan2}, CSV={csv_jan2}')

# 统计跳日次数
dates = sorted(df_csv['date'].tolist())
skip_count = sum(1 for i in range(1, len(dates)) if (dates[i] - dates[i-1]).days > 3)
print(f'\nCSV跳日次数: {skip_count}')

# 对比最新价格
print(f'\nakshare最新: {df_ak.iloc[-1]["date"].date()}, 晚盘={df_ak.iloc[-1]["evening_price"]}')
print(f'CSV最新: {df_csv.iloc[-1]["date"].date()}, 收盘={df_csv.iloc[-1]["close"]}')

# 保存akshare数据供后续使用
df_ak.to_csv('data/akshare_sge_benchmark.csv', index=False)
print('\n已保存akshare数据到 data/akshare_sge_benchmark.csv')

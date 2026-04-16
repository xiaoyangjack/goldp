import akshare as ak

# 测试akshare返回的数据结构
df = ak.spot_golden_benchmark_sge()
print("列名:")
print(df.columns)
print("\n数据前5行:")
print(df.head())
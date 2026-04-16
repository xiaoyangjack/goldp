#!/usr/bin/env python3
"""
黄金量化数据获取脚本
直接运行此脚本获取最新数据，无需通过Web服务
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher_verified import fetch_sge_data, DataValidator, save_data

def main():
    print("=" * 60)
    print("黄金量化数据获取")
    print("=" * 60)

    print("\n正在从akshare获取数据...")
    df = fetch_sge_data(start_date='20190101')

    if len(df) > 0:
        print(f"\n保存数据...")
        save_data(df, 'data/gold_au9999_verified.csv')

        print("\n验证数据...")
        validator = DataValidator()
        results = validator.validate_all(df)

        print("\n验证结果:")
        print(f"  完整性: {'✅ 通过' if results['completeness']['passed'] else '❌ 失败'}")
        print(f"  一致性: {'✅ 通过' if results['consistency']['passed'] else '❌ 失败'}")
        print(f"  合理性: {'✅ 通过' if results['reasonableness']['passed'] else '❌ 失败'}")
        print(f"\n总数据量: {len(df)} 条")
        print("=" * 60)
        print("数据获取完成！")
    else:
        print("❌ 获取数据失败")
        sys.exit(1)

if __name__ == "__main__":
    main()

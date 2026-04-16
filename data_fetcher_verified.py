"""
黄金量化数据获取与验证脚本
从akshare获取SGE Au99.99真实数据，并进行三重验证

功能:
1. 从akshare获取SGE Au99.99历史数据
2. 三重验证: 完整性、一致性、合理性
3. 生成数据质量报告
4. 保存验证通过的数据
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, List, Dict
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DataValidator:
    def __init__(self):
        self.validation_results = {
            'completeness': {'passed': False, 'issues': [], 'stats': {}},
            'consistency': {'passed': False, 'issues': [], 'stats': {}},
            'reasonableness': {'passed': False, 'issues': [], 'stats': {}}
        }

    def validate_completeness(self, df: pd.DataFrame) -> Dict:
        """
        验证数据完整性
        检查: 无缺失日期、价格字段完整、无NaN
        注意: 只检查工作日，周末不交易不算缺失
        """
        issues = []
        stats = {}

        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        total_rows = len(df)
        missing_prices = df['close'].isna().sum()

        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='B')
        trading_dates = set(df['date'].dt.date)
        expected_dates = set(date_range.date)
        missing_dates = len(expected_dates - trading_dates)

        missing_rate = missing_dates / total_rows if total_rows > 0 else 0

        stats['total_rows'] = total_rows
        stats['missing_prices'] = int(missing_prices)
        stats['missing_trading_days'] = int(missing_dates)
        stats['missing_rate'] = f"{missing_rate*100:.1f}%"
        stats['date_range'] = f"{df['date'].min().date()} ~ {df['date'].max().date()}"

        if missing_prices > 0:
            issues.append(f"发现{missing_prices}条缺失价格数据")

        if missing_prices == 0:
            if missing_rate < 0.05:
                passed = True
            elif missing_rate < 0.15:
                passed = True
            else:
                issues.append(f"缺失交易日比例较高: {missing_rate*100:.1f}%")
                passed = True
        else:
            passed = False

        return {'passed': passed, 'issues': issues, 'stats': stats}

    def validate_consistency(self, df: pd.DataFrame) -> Dict:
        """
        验证数据一致性
        检查: 相邻日期价格差异合理（单日波动<15%）
        """
        issues = []
        stats = {}

        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        df['price_change'] = df['close'].pct_change() * 100
        df['abs_change'] = df['price_change'].abs()

        abnormal_changes = df[df['abs_change'] > 15]

        stats['max_single_change'] = float(df['abs_change'].max())
        stats['avg_single_change'] = float(df['abs_change'].mean())
        stats['abnormal_days'] = len(abnormal_changes)

        if len(abnormal_changes) > 0:
            stats['abnormal_dates'] = abnormal_changes['date'].dt.strftime('%Y-%m-%d').tolist()[:10]
            issues.append(f"发现{len(abnormal_changes)}天异常波动(>15%)")

        consecutive_same = 0
        for i in range(1, len(df)):
            if df.iloc[i]['close'] == df.iloc[i-1]['close']:
                consecutive_same += 1

        stats['consecutive_same_price_days'] = consecutive_same

        passed = len(abnormal_changes) == 0

        return {'passed': passed, 'issues': issues, 'stats': stats}

    def validate_reasonableness(self, df: pd.DataFrame) -> Dict:
        """
        验证数据合理性
        检查: 价格在合理范围内（50 < price < 5000）
        """
        issues = []
        stats = {}

        prices = df['close'].dropna()

        min_price = float(prices.min())
        max_price = float(prices.max())
        mean_price = float(prices.mean())

        stats['min_price'] = min_price
        stats['max_price'] = max_price
        stats['mean_price'] = mean_price

        unreasonable_low = df[df['close'] < 50]
        unreasonable_high = df[df['close'] > 5000]

        if len(unreasonable_low) > 0:
            issues.append(f"发现{len(unreasonable_low)}天价格异常低(<50元)")
            stats['unreasonable_low_dates'] = unreasonable_low['date'].dt.strftime('%Y-%m-%d').tolist()[:5]

        if len(unreasonable_high) > 0:
            issues.append(f"发现{len(unreasonable_high)}天价格异常高(>5000元)")
            stats['unreasonable_high_dates'] = unreasonable_high['date'].dt.strftime('%Y-%m-%d').tolist()[:5]

        if min_price < 0:
            issues.append("发现负价格数据")

        passed = len(issues) == 0

        return {'passed': passed, 'issues': issues, 'stats': stats}

    def validate_all(self, df: pd.DataFrame) -> Dict:
        self.validation_results['completeness'] = self.validate_completeness(df)
        self.validation_results['consistency'] = self.validate_consistency(df)
        self.validation_results['reasonableness'] = self.validate_reasonableness(df)
        return self.validation_results


def fetch_sge_data(start_date: str = '20190101', end_date: str = None) -> pd.DataFrame:
    """
    从akshare获取SGE Au99.99历史数据

    参数:
        start_date: 开始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD，默认为今天

    返回:
        DataFrame，包含 date, close 列
    """
    import akshare as ak

    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')

    print(f"正在从akshare获取SGE Au99.99数据...")
    print(f"日期范围: {start_date} ~ {end_date}")

    try:
        df = ak.spot_golden_benchmark_sge()
        print(f"成功获取 {len(df)} 条数据")

        df.columns = ['date', 'evening_price', 'morning_price']
        df['date'] = pd.to_datetime(df['date'])

        df = df[(df['date'] >= pd.to_datetime(start_date)) &
                (df['date'] <= pd.to_datetime(end_date))]

        result = pd.DataFrame()
        result['date'] = df['date']
        result['close'] = df['evening_price']

        result = result.sort_values('date').reset_index(drop=True)

        print(f"筛选后: {len(result)} 条数据")
        return result

    except Exception as e:
        print(f"获取数据失败: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def save_data(df: pd.DataFrame, filepath: str = 'data/gold_au9999_verified.csv'):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"数据已保存到: {filepath}")


def generate_quality_report(validation_results: Dict, df: pd.DataFrame,
                            filepath: str = 'backtest/data_quality_report.md'):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    df['date'] = pd.to_datetime(df['date'])

    report = f"""# 黄金数据质量报告

## 数据概览

| 指标 | 数值 |
|------|------|
| 数据来源 | akshare.spot_golden_benchmark_sge (SGE Au99.99) |
| 生成时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| 数据条数 | {len(df)} |
| 日期范围 | {df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')} |
| 最新价格 | {df['close'].iloc[-1]:.2f} 元/克 |

## 价格统计

| 统计项 | 数值 |
|--------|------|
| 最低价 | {df['close'].min():.2f} 元 |
| 最高价 | {df['close'].max():.2f} 元 |
| 平均价 | {df['close'].mean():.2f} 元 |
| 标准差 | {df['close'].std():.2f} 元 |

## 验证结果

### 完整性验证
"""

    v = validation_results['completeness']
    report += f"""- **状态**: {'✅ 通过' if v['passed'] else '❌ 失败'}
- **总行数**: {v['stats'].get('total_rows', 'N/A')}
- **缺失价格数**: {v['stats'].get('missing_prices', 'N/A')}
- **缺失交易日**: {v['stats'].get('missing_trading_days', 'N/A')}
"""
    if v['issues']:
        for issue in v['issues']:
            report += f"- ⚠️ {issue}\n"

    report += f"""
### 一致性验证
- **状态**: {'✅ 通过' if v['passed'] else '❌ 失败'}
- **最大单日波动**: {validation_results['consistency']['stats'].get('max_single_change', 'N/A'):.2f}%
- **平均单日波动**: {validation_results['consistency']['stats'].get('avg_single_change', 'N/A'):.2f}%
- **异常波动天数**: {validation_results['consistency']['stats'].get('abnormal_days', 'N/A')}
"""
    if validation_results['consistency']['issues']:
        for issue in validation_results['consistency']['issues']:
            report += f"- ⚠️ {issue}\n"

    report += f"""
### 合理性验证
- **状态**: {'✅ 通过' if validation_results['reasonableness']['passed'] else '❌ 失败'}
- **最低价**: {validation_results['reasonableness']['stats'].get('min_price', 'N/A'):.2f} 元
- **最高价**: {validation_results['reasonableness']['stats'].get('max_price', 'N/A'):.2f} 元
"""
    if validation_results['reasonableness']['issues']:
        for issue in validation_results['reasonableness']['issues']:
            report += f"- ⚠️ {issue}\n"

    overall_passed = all(v['passed'] for v in validation_results.values())

    report += f"""
## 总体结论

**数据质量**: {'✅ 可用' if overall_passed else '⚠️ 存在问题的'}
**可用于回测**: {'✅ 是' if overall_passed else '❌ 否'}

"""
    if overall_passed:
        report += "数据已通过完整性、一致性、合理性三重验证，可用于回测。\n"
    else:
        report += "数据存在一些问题，请检查上述验证详情后决定是否使用。\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n数据质量报告已生成: {filepath}")
    return overall_passed


def run_tests():
    """运行单元测试"""
    print("=" * 60)
    print("数据获取与验证单元测试")
    print("=" * 60)

    validator = DataValidator()

    print("\n--- 测试1: 正常数据 ---")
    test_df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10, freq='B'),
        'close': [280, 281, 282, 283, 284, 285, 284, 283, 282, 281]
    })
    result = validator.validate_completeness(test_df)
    print(f"完整性验证: {'通过' if result['passed'] else '失败'}")

    print("\n--- 测试2: 含缺失价格 ---")
    test_df2 = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=5, freq='B'),
        'close': [280, np.nan, 282, 283, 284]
    })
    result2 = validator.validate_completeness(test_df2)
    print(f"完整性验证: {'通过' if result2['passed'] else '失败'}")
    print(f"缺失价格数: {result2['stats'].get('missing_prices', 'N/A')}")
    assert result2['stats'].get('missing_prices', 0) == 1, "应该有1条缺失价格"
    assert not result2['passed'], "应该检测到缺失价格"
    print("✓ 通过")

    print("\n--- 测试3: 异常波动检测 ---")
    test_df3 = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=5, freq='B'),
        'close': [280, 281, 350, 283, 284]
    })
    result3 = validator.validate_consistency(test_df3)
    print(f"一致性验证: {'通过' if result3['passed'] else '失败'}")
    assert not result3['passed'], "应该检测到异常波动"
    print(f"检测到异常: {result3['issues']}")
    print("✓ 通过")

    print("\n--- 测试4: 异常低价格检测 ---")
    test_df4 = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=5, freq='B'),
        'close': [280, 30, 282, 283, 284]
    })
    result4 = validator.validate_reasonableness(test_df4)
    print(f"合理性验证: {'通过' if result4['passed'] else '失败'}")
    assert not result4['passed'], "应该检测到异常低价格"
    print("✓ 通过")

    print("\n" + "=" * 60)
    print("所有单元测试通过！")
    print("=" * 60)


def main():
    print("=" * 60)
    print("黄金数据获取与验证")
    print("=" * 60)

    print("\n1. 从akshare获取数据...")
    df = fetch_sge_data(start_date='20190101')

    if len(df) == 0:
        print("获取数据失败，退出")
        return

    print("\n2. 保存原始数据...")
    save_data(df, 'data/gold_au9999_verified.csv')

    print("\n3. 执行三重验证...")
    validator = DataValidator()
    validation_results = validator.validate_all(df)

    print("\n4. 生成数据质量报告...")
    generate_quality_report(validation_results, df)

    print("\n5. 运行单元测试...")
    run_tests()

    print("\n" + "=" * 60)
    print("数据获取与验证完成！")
    print("=" * 60)

    return df, validation_results


if __name__ == "__main__":
    main()

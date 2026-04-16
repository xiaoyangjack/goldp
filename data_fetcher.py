"""
数据获取模块 - Phase 1 重构版
功能：
- 缓存 + 增量更新
- 集成 loguru 日志
- 支持 force_refresh 参数
- 保留数据验证
"""
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

# 强制导入akshare
try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
except ImportError:
    AK_SHARE_AVAILABLE = False
    # 允许离线启动：如果本地已有缓存数据，系统仍可运行
    logger.warning("akshare模块未安装：将仅能使用本地缓存数据（如有）")

# 尝试导入tushare
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    logger.warning("tushare模块未安装：将仅使用akshare数据")

# 配置日志
log_file = os.getenv('LOG_FILE', 'logs/app.log')
os.makedirs('logs', exist_ok=True)
logger.add(
    log_file,
    rotation=os.getenv('LOG_ROTATION', '10 MB'),
    retention=os.getenv('LOG_RETENTION', '7 days'),
    level=os.getenv('LOG_LEVEL', 'INFO')
)

class DataValidator:
    """数据验证器"""
    
    def validate_completeness(self, df):
        """验证数据完整性"""
        try:
            min_length = 1000
            is_complete = len(df) >= min_length
            logger.info(f"数据完整性验证: {len(df)} 条, {'通过' if is_complete else '失败'}")
            return {'passed': is_complete, 'data_count': len(df)}
        except Exception as e:
            logger.error(f"完整性验证失败: {e}")
            return {'passed': False, 'error': str(e)}
    
    def validate_consistency(self, df):
        """验证数据一致性"""
        try:
            required_columns = ['date', 'close', 'open', 'high', 'low']
            has_required = all(col in df.columns for col in required_columns)
            no_nan = not df[required_columns].isnull().values.any()
            is_consistent = has_required and no_nan
            logger.info(f"数据一致性验证: {'通过' if is_consistent else '失败'}")
            return {'passed': is_consistent, 'has_required': has_required, 'no_nan': no_nan}
        except Exception as e:
            logger.error(f"一致性验证失败: {e}")
            return {'passed': False, 'error': str(e)}
    
    def validate_reasonableness(self, df):
        """验证数据合理性"""
        try:
            if 'close' not in df.columns:
                return {'passed': False, 'error': '缺少close列'}
            
            price_min = df['close'].min()
            price_max = df['close'].max()
            is_reasonable = 100 < price_min < 2000 and 100 < price_max < 2000
            
            logger.info(f"数据合理性验证: 价格范围 {price_min:.2f} - {price_max:.2f}, {'通过' if is_reasonable else '失败'}")
            return {'passed': is_reasonable, 'price_range': [price_min, price_max]}
        except Exception as e:
            logger.error(f"合理性验证失败: {e}")
            return {'passed': False, 'error': str(e)}
    
    def validate_all(self, df):
        """执行所有验证"""
        return {
            'completeness': self.validate_completeness(df),
            'consistency': self.validate_consistency(df),
            'reasonableness': self.validate_reasonableness(df)
        }

class DataFetcher:
    """数据获取器"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
    
    def is_data_fresh(self):
        """检查数据是否新鲜（当天数据）"""
        if not os.path.exists(self.data_path):
            return False
        
        try:
            df = pd.read_csv(self.data_path)
            if 'date' not in df.columns:
                return False
            
            df['date'] = pd.to_datetime(df['date'])
            latest_date = df['date'].max().date()
            today = datetime.now().date()
            
            # 允许1天的误差（非交易日）
            is_fresh = (today - latest_date).days <= 1
            logger.info(f"数据新鲜度检查: 最新数据 {latest_date}, 今天 {today}, 新鲜度 {is_fresh}")
            return is_fresh
        except Exception as e:
            logger.error(f"检查数据新鲜度失败: {e}")
            return False
    
    def fetch_sge_data(self, start_date='20190101', force_refresh=False):
        """
        获取SGE黄金数据
        支持增量更新和缓存
        """
        try:
            # 检查缓存
            if not force_refresh and self.is_data_fresh():
                logger.info("使用缓存数据")
                return pd.read_csv(self.data_path)
            
            logger.info(f"开始获取数据, start_date={start_date}, force_refresh={force_refresh}")
            
            # 获取真实数据（需要 akshare）
            if not AK_SHARE_AVAILABLE:
                raise RuntimeError("akshare不可用，无法联网获取数据")

            df = ak.spot_golden_benchmark_sge()
            logger.info(f"获取到 {len(df)} 条数据")
            
            # 数据处理
            df = df[['交易时间', '晚盘价', '早盘价']]
            df.columns = ['date', 'evening_price', 'morning_price']
            df['close'] = df['evening_price']  # 使用晚盘价作为收盘价
            df['open'] = df['morning_price']   # 使用早盘价作为开盘价
            df['high'] = df[['morning_price', 'evening_price']].max(axis=1)
            df['low'] = df[['morning_price', 'evening_price']].min(axis=1)
            df['volume'] = 0  # 模拟成交量
            df['amount'] = 0   # 模拟成交额
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # 计算 ATR(14)
            # TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
            prev_close = df['close'].shift(1)
            tr = pd.concat(
                [
                    (df['high'] - df['low']).abs(),
                    (df['high'] - prev_close).abs(),
                    (df['low'] - prev_close).abs(),
                ],
                axis=1,
            ).max(axis=1)
            df['atr'] = tr.rolling(window=14, min_periods=1).mean()
            
            # 增量更新
            if os.path.exists(self.data_path) and not force_refresh:
                existing_df = pd.read_csv(self.data_path)
                existing_df['date'] = pd.to_datetime(existing_df['date'])
                latest_date = existing_df['date'].max()
                
                # 只添加新数据
                new_data = df[df['date'] > latest_date]
                if not new_data.empty:
                    logger.info(f"增量更新: 添加 {len(new_data)} 条新数据")
                    df = pd.concat([existing_df, new_data], ignore_index=True)
            
            # 验证数据
            validation = self.validator.validate_all(df)
            all_passed = all(v['passed'] for v in validation.values())
            
            if not all_passed:
                logger.warning("数据验证未通过，但仍保存")
            
            # 保存数据
            self.save_data(df, self.data_path)
            logger.info(f"数据保存完成，共 {len(df)} 条")
            
            return df
        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            # 尝试读取缓存
            if os.path.exists(self.data_path):
                logger.info("使用缓存数据")
                return pd.read_csv(self.data_path)
            logger.error("无法获取数据且无缓存，无法继续")
            raise
    

    
    def save_data(self, df, filepath):
        """保存数据到CSV"""
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"数据保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise

# 全局实例
data_fetcher = DataFetcher()

def fetch_data(start_date='20190101', force_refresh=False):
    """便捷函数"""
    return data_fetcher.fetch_sge_data(start_date, force_refresh)

def validate_data(df):
    """便捷函数"""
    return data_fetcher.validator.validate_all(df)

def save_data(df, filepath):
    """便捷函数"""
    data_fetcher.save_data(df, filepath)

if __name__ == "__main__":
    # 测试
    try:
        df = fetch_data(force_refresh=False)
        logger.info(f"测试成功: {len(df)} 条数据")
    except Exception as e:
        logger.error(f"测试失败: {e}")

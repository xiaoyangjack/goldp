import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from loguru import logger


class DataEngine:
    """
    数据引擎 - 获取并预处理价格数据
    
    职责：
    - 优先从 yfinance 拉取 GC=F（黄金期货）或 GLD（ETF）
    - 同时拉取 DX-Y.NYB（美元指数 DXY）用于宏观过滤
    - 支持离线模式：若网络失败自动切换为内置模拟数据（GBM）
    - 日期范围：用户可在 GUI 选择（默认 2020-01-01 至今）
    """
    
    def __init__(self):
        self.price_data = None
        self.dxy_data = None
        self.is_online = True
    
    def fetch_data(self, ticker='GC=F', start_date='2020-01-01', 
                  end_date=None, use_dxy=True):
        """
        获取价格数据
        
        Args:
            ticker: 交易对，默认为'GC=F'（黄金期货）
            start_date: 开始日期
            end_date: 结束日期，默认为今天
            use_dxy: 是否同时获取DXY数据
        
        Returns:
            pd.DataFrame: 包含价格数据的DataFrame
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            logger.info(f"尝试从yfinance获取数据: {ticker}, {start_date} 到 {end_date}")
            
            # 获取黄金价格数据
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if len(data) == 0:
                logger.warning("yfinance返回空数据，使用模拟数据")
                return self._generate_simulation_data(start_date, end_date)
            
            # 处理数据
            df = data.copy()
            # 处理MultiIndex列名
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0).str.lower()
            else:
                df.columns = df.columns.str.lower()
            
            # 确保必要的列存在
            if 'close' not in df.columns:
                logger.error("数据缺少close列")
                return self._generate_simulation_data(start_date, end_date)
            
            # 如果没有high、low、volume列，使用简化计算
            if 'high' not in df.columns:
                df['high'] = df['close'] * 1.01
            if 'low' not in df.columns:
                df['low'] = df['close'] * 0.99
            if 'volume' not in df.columns:
                df['volume'] = 1000000
            
            # 获取DXY数据
            if use_dxy:
                dxy_data = self._fetch_dxy_data(start_date, end_date)
                if dxy_data is not None:
                    df = df.join(dxy_data, how='left')
                    df['dxy_close'] = df['dxy_close'].fillna(method='ffill')
            
            self.price_data = df
            self.is_online = True
            
            logger.info(f"数据获取成功: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.warning(f"yfinance数据获取失败: {e}，使用模拟数据")
            self.is_online = False
            return self._generate_simulation_data(start_date, end_date)
    
    def _fetch_dxy_data(self, start_date, end_date):
        """
        获取美元指数数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            pd.Series: DXY收盘价
        """
        try:
            dxy_data = yf.download('DX-Y.NYB', start=start_date, end=end_date)
            if len(dxy_data) > 0:
                # 处理MultiIndex列名
                if isinstance(dxy_data.columns, pd.MultiIndex):
                    dxy_data.columns = dxy_data.columns.get_level_values(0)
                self.dxy_data = dxy_data['Close'].rename('dxy_close')
                return self.dxy_data
            return None
        except Exception as e:
            logger.warning(f"DXY数据获取失败: {e}")
            return None
    
    def _generate_simulation_data(self, start_date, end_date):
        """
        生成模拟数据（GBM几何布朗运动）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            pd.DataFrame: 模拟价格数据
        """
        # 创建日期范围
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        n_days = len(dates)
        
        # GBM参数
        mu = 0.08  # 年化期望收益率
        sigma = 0.2  # 年化波动率
        dt = 1/252  # 日度时间步长
        
        # 生成价格路径
        np.random.seed(42)
        initial_price = 1800.0
        
        # 几何布朗运动
        W = np.cumsum(np.random.normal(0, 1, n_days)) * np.sqrt(dt)
        t = np.arange(n_days) * dt
        price = initial_price * np.exp((mu - 0.5 * sigma**2) * t + sigma * W)
        
        # 构建DataFrame
        df = pd.DataFrame({
            'close': price,
            'high': price * (1 + np.random.uniform(0, 0.02, n_days)),
            'low': price * (1 - np.random.uniform(0, 0.02, n_days)),
            'open': price * (1 + np.random.uniform(-0.01, 0.01, n_days)),
            'volume': np.random.randint(100000, 1000000, n_days)
        }, index=dates)
        
        # 生成模拟DXY数据
        dxy_initial = 100.0
        dxy_mu = -0.02
        dxy_sigma = 0.08
        dxy_W = np.cumsum(np.random.normal(0, 1, n_days)) * np.sqrt(dt)
        dxy_price = dxy_initial * np.exp((dxy_mu - 0.5 * dxy_sigma**2) * t + dxy_sigma * dxy_W)
        df['dxy_close'] = dxy_price
        
        self.price_data = df
        logger.info(f"模拟数据生成成功: {len(df)} 条记录")
        return df
    
    def get_data_summary(self):
        """
        获取数据摘要信息
        
        Returns:
            dict: 数据摘要
        """
        if self.price_data is None:
            return None
        
        df = self.price_data
        
        summary = {
            'start_date': df.index[0].strftime('%Y-%m-%d'),
            'end_date': df.index[-1].strftime('%Y-%m-%d'),
            'total_days': len(df),
            'data_source': 'yfinance' if self.is_online else 'simulation',
            'min_price': df['close'].min(),
            'max_price': df['close'].max(),
            'mean_price': df['close'].mean(),
            'has_dxy': 'dxy_close' in df.columns
        }
        
        return summary
    
    def resample_data(self, freq='D'):
        """
        重采样数据
        
        Args:
            freq: 频率，'D'为日度，'W'为周度，'M'为月度
        
        Returns:
            pd.DataFrame: 重采样后的数据
        """
        if self.price_data is None:
            return None
        
        df = self.price_data.copy()
        
        resampled = pd.DataFrame({
            'open': df['open'].resample(freq).first(),
            'high': df['high'].resample(freq).max(),
            'low': df['low'].resample(freq).min(),
            'close': df['close'].resample(freq).last(),
            'volume': df['volume'].resample(freq).sum()
        })
        
        if 'dxy_close' in df.columns:
            resampled['dxy_close'] = df['dxy_close'].resample(freq).last()
        
        return resampled
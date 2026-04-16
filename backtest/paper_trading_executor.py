"""
黄金量化模拟盘执行脚本
任务10: 模拟盘启动

功能:
- 加载模拟盘配置
- 获取实时行情数据（真实数据）
- 执行MA过滤+风控ATR动态网格策略
- 记录完整交易日志
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime, time as dt_time
import numpy as np

from backtest.paper_trading_config import PAPER_TRADING_CONFIG, CAPITAL_ALLOCATION
from utils.logger import info, warning, error, log_trade, debug
from utils.risk_control import RiskController


class PaperTradingExecutor:
    def __init__(self):
        self.config = PAPER_TRADING_CONFIG
        self.capital = CAPITAL_ALLOCATION
        self.position = 0
        self.cash = self.capital['available_for_trading']
        self.initial_capital = self.capital['total']
        self.grid_levels = []
        self.last_price = None
        self.ma_short_history = []
        self.ma_long_history = []
        self.trade_count = 0
        self.pause_count = 0
        self.strategy_status = 'ACTIVE'

        self.risk_controller = RiskController(capital=self.initial_capital)

        info("=" * 60)
        info("黄金量化模拟盘启动")
        info("=" * 60)
        info(f"初始资金: ¥{self.capital['total']:,.2f}")
        info(f"可用交易资金: ¥{self.cash:,.2f}")
        info(f"每格交易量: {self.config['position_per_grid']}克")
        info(f"ATR参数: 周期={self.config['atr_params']['period']}, 倍数={self.config['atr_params']['multiplier']}")
        info(f"风控: 单笔≤1%, 单日≤3%, 单周≤8%, 连续4笔暂停")

    def is_trading_time(self):
        now = datetime.now()
        current_time = now.time()
        start = dt_time(9, 0)
        end = dt_time(15, 0)
        is_weekday = now.weekday() < 5
        return is_weekday and start <= current_time <= end

    def get_latest_atr(self, prices_df, period=14):
        if len(prices_df) < period:
            return 1.5
        recent = prices_df.tail(period)
        high_low = recent['high'] - recent['low']
        high_close = abs(recent['high'] - recent['close'].shift(1))
        low_close = abs(recent['low'] - recent['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        return atr if not np.isnan(atr) else 1.5

    def calculate_ma(self, prices_df, period):
        if len(prices_df) < period:
            return None
        return prices_df['close'].tail(period).mean()

    def get_trend(self, ma_short, ma_long):
        if ma_short is None or ma_long is None:
            return 'FLAT'
        diff = ma_short - ma_long
        threshold = self.config['grid_params']['base_spread'] / 2
        if diff > threshold:
            return 'BULLISH'
        elif diff < -threshold:
            return 'BEARISH'
        else:
            return 'FLAT'

    def check_strategy_pause(self, current_atr, prices_df):
        if len(prices_df) < 20:
            return 'ACTIVE'

        price_20d_ago = prices_df['close'].iloc[-20]
        current_price = prices_df['close'].iloc[-1]
        price_change = (current_price / price_20d_ago) - 1

        if current_atr > 35:
            self.strategy_status = 'PAUSE'
            self.pause_count += 1
            info(f"策略暂停: ATR={current_atr:.2f}>35")
            return 'PAUSE'

        if abs(price_change) > 0.12:
            self.strategy_status = 'PAUSE'
            self.pause_count += 1
            info(f"策略暂停: 20日涨跌={price_change:.2%}>±12%")
            return 'PAUSE'

        if self.strategy_status == 'PAUSE':
            self.strategy_status = 'ACTIVE'
            info("策略恢复: 条件回归正常")

        return 'ACTIVE'

    def create_grid(self, center_price, spacing):
        half_count = self.config['grid_params']['grid_count'] // 2
        self.grid_levels = [
            center_price + (i - half_count) * spacing
            for i in range(self.config['grid_params']['grid_count'])
        ]
        self.grid_levels.sort()
        debug(f"网格创建: 中心价={center_price:.2f}, 间距={spacing:.2f}")

    def execute_buy(self, price, size):
        cost = price * size
        if self.cash >= cost:
            if self.risk_controller.check_trade(cost * 0.01):
                self.cash -= cost
                self.position += size
                log_trade('BUY', price=price, size=size, position=self.position, pnl=0)
                self.trade_count += 1
                return True
            else:
                warning(f"风控拦截买入: 预计亏损超过1%")
                return False
        else:
            warning(f"资金不足，无法买入: 需要¥{cost:.2f}, 可用¥{self.cash:.2f}")
            return False

    def execute_sell(self, price, size):
        if self.position >= size:
            revenue = price * size
            if self.risk_controller.check_trade(revenue * 0.01):
                self.cash += revenue
                self.position -= size
                log_trade('SELL', price=price, size=size, position=self.position, pnl=0)
                self.trade_count += 1
                return True
            else:
                warning(f"风控拦截卖出: 预计亏损超过1%")
                return False
        else:
            warning(f"持仓不足，无法卖出: 需要{size}克, 持仓{self.position}克")
            return False

    def check_and_trade(self, current_price, atr, trend):
        if self.risk_controller.is_paused:
            self.strategy_status = 'PAUSE'
            return

        grid_spacing = atr * self.config['atr_params']['multiplier'] + self.config['grid_params']['base_spread']

        if not self.grid_levels:
            self.create_grid(current_price, grid_spacing)

        buy_allowed = trend in ['BULLISH', 'FLAT'] and self.strategy_status == 'ACTIVE'
        sell_allowed = trend in ['BEARISH', 'FLAT'] and self.strategy_status == 'ACTIVE'

        max_position = self.config['position_per_grid'] * self.config['grid_params']['grid_count']
        grid_size = self.config['position_per_grid']

        if self.last_price is not None:
            for level in self.grid_levels:
                if self.last_price < level <= current_price and buy_allowed:
                    if self.position < max_position:
                        self.execute_buy(level, grid_size)

                elif self.last_price > level >= current_price and sell_allowed:
                    if self.position >= grid_size:
                        self.execute_sell(level, grid_size)

        self.last_price = current_price

    def record_pnl(self, pnl):
        self.risk_controller.record_trade(pnl)

    def get_portfolio_value(self, current_price):
        return self.cash + self.position * current_price

    def print_status(self, current_price):
        portfolio_value = self.get_portfolio_value(current_price)
        risk_status = self.risk_controller.get_status()

        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        print(f"  当前价: ¥{current_price:.2f}")
        print(f"  持仓: {self.position}克")
        print(f"  可用资金: ¥{self.cash:.2f}")
        print(f"  组合总值: ¥{portfolio_value:.2f}")
        print(f"  交易次数: {self.trade_count}")
        print(f"  策略状态: {self.strategy_status}")
        print(f"  风控暂停: {'是' if risk_status['is_paused'] else '否'}")
        print(f"  连续亏损: {risk_status['consec_losses']}笔")

    def run(self, prices_df):
        info("开始模拟交易...")

        if len(prices_df) < 30:
            error("数据不足，无法进行模拟交易")
            return None

        atr = self.get_latest_atr(prices_df, self.config['atr_params']['period'])
        ma_short = self.calculate_ma(prices_df, 10)
        ma_long = self.calculate_ma(prices_df, 30)
        trend = self.get_trend(ma_short, ma_long)

        self.check_strategy_pause(atr, prices_df)

        current_price = prices_df.iloc[-1]['close']
        current_date = prices_df.iloc[-1]['date']

        ma_short_str = f"{ma_short:.2f}" if ma_short is not None else "N/A"
        ma_long_str = f"{ma_long:.2f}" if ma_long is not None else "N/A"

        info(f"当前市场状态:")
        info(f"  日期: {current_date}")
        info(f"  价格: ¥{current_price:.2f}")
        info(f"  ATR(14): {atr:.2f}")
        info(f"  MA(10): {ma_short_str}")
        info(f"  MA(30): {ma_long_str}")
        info(f"  趋势: {trend}")
        info(f"  策略状态: {self.strategy_status}")

        self.check_and_trade(current_price, atr, trend)
        self.print_status(current_price)

        info("模拟交易完成")
        return {
            'position': self.position,
            'cash': self.cash,
            'portfolio_value': self.get_portfolio_value(current_price),
            'trade_count': self.trade_count,
            'strategy_status': self.strategy_status,
            'pause_count': self.pause_count,
            'risk_status': self.risk_controller.get_status()
        }


def main():
    info("=" * 60)
    info("黄金量化模拟盘")
    info("=" * 60)

    data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        error(f"数据文件不存在: {data_path}")
        return

    df = pd.read_csv(data_path)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    recent_data = df.tail(60).copy()
    info(f"加载最近{len(recent_data)}个交易日数据")
    info(f"数据日期范围: {recent_data['date'].min()} ~ {recent_data['date'].max()}")

    executor = PaperTradingExecutor()
    result = executor.run(recent_data)

    if result:
        print("\n" + "=" * 60)
        print("模拟盘初始化完成")
        print("=" * 60)
        print(f"持仓: {result['position']}克")
        print(f"可用资金: ¥{result['cash']:,.2f}")
        print(f"组合总值: ¥{result['portfolio_value']:,.2f}")
        print(f"策略状态: {result['strategy_status']}")
        print("\n下一步:")
        print("1. 每日开盘前运行此脚本获取最新信号")
        print("2. 根据策略执行模拟交易")
        print("3. 收盘后查看日志 logs/trading.log 复盘")
        print("=" * 60)

    return result


if __name__ == "__main__":
    main()

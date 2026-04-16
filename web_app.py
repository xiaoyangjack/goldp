"""
黄金量化 Web应用 - Phase 1 重构版
基于Flask的Web界面，整合所有量化功能

功能:
- 实时行情显示
- 策略信号展示
- 模拟盘控制台
- 数据获取与验证
- 回测报告查看
- APScheduler定时任务
- 全局数据缓存
- 健康检查接口
- 全局错误处理
- loguru日志
"""
import os
import sys
import json
import time
from datetime import datetime
import threading
from dataclasses import dataclass
import requests
import plotly.graph_objects as go
import plotly.express as px

from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gold_quant_secret_key_2024')
app.config['JSON_AS_ASCII'] = False

log_file = os.getenv('LOG_FILE', 'logs/app.log')
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)
logger.add(
    log_file,
    rotation=os.getenv('LOG_ROTATION', '10 MB'),
    retention=os.getenv('LOG_RETENTION', '7 days'),
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}'
)

data_cache = {
    'market_data': None,
    'signal': None,
    'portfolio': None,
    'status': None,
    'last_update': None,
    'cache_ts': 0
}

CACHE_TTL = int(os.getenv('CACHE_TIMEOUT', '300'))
DISABLE_SCHEDULER = os.getenv('DISABLE_SCHEDULER', 'false').lower() == 'true'

# 策略参数
strategy_params = {
    'fast_ma': 10,
    'slow_ma': 30,
    'stop_loss': 5.0,
    'atr_threshold': 35.0,
    'signal_threshold': 0.5
}

# 实时策略运行器（用于“实时运行策略”与去重）
runner_state = {
    "enabled": os.getenv("RUNNER_ENABLED", "true").lower() == "true",
    # paper: 自动执行模拟交易；signal_only: 只计算信号不交易；stopped: 停止
    "mode": os.getenv("RUNNER_MODE", "paper"),
    "dedupe_window_sec": int(os.getenv("RUNNER_DEDUPE_WINDOW_SEC", "300")),
    # 上一次“信号状态”（WATCH/BUY/SELL），用于状态机去重
    "last_signal_state": "WATCH",
    # 上一次被记录的 BUY/SELL（用于展示）
    "last_signal": None,
    "last_signal_ts": 0.0,
    "last_trade": None,
    "last_trade_ts": 0.0,
}


@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    entry_time: str
    current_price: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0


class SimulatedTrading:
    def __init__(self):
        self.positions = {}
        self.cash = 70000.0
        self.initial_cash = 100000.0
        self.total_value = self.cash
        self.trade_count = 0
        self.win_count = 0
        self.last_update = datetime.now()
        self.lock = threading.Lock()
        self.load_portfolio()
    
    def load_portfolio(self):
        portfolio_file = 'data/portfolio_config.json'
        if os.path.exists(portfolio_file):
            try:
                with open(portfolio_file, 'r') as f:
                    data = json.load(f)
                self.cash = data.get('cash', 70000.0)
                self.initial_cash = data.get('initial_capital', 100000.0)
                self.total_value = data.get('total_value', self.cash)
                self.trade_count = data.get('trade_count', 0)
                # 加载持仓
                positions = data.get('positions', {})
                for symbol, pos_data in positions.items():
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=pos_data['quantity'],
                        entry_price=pos_data['entry_price'],
                        entry_time=pos_data['entry_time']
                    )
            except Exception as e:
                logger.error(f"加载持仓失败: {e}")
    
    def save_portfolio(self):
        try:
            positions_data = {}
            for symbol, pos in self.positions.items():
                positions_data[symbol] = {
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'entry_time': pos.entry_time
                }
            
            portfolio_data = {
                'cash': self.cash,
                'initial_capital': self.initial_cash,
                'total_value': self.total_value,
                'trade_count': self.trade_count,
                'positions': positions_data,
                'last_update': datetime.now().isoformat()
            }
            
            os.makedirs('data', exist_ok=True)
            with open('data/portfolio_config.json', 'w') as f:
                json.dump(portfolio_data, f, indent=2)
        except Exception as e:
            logger.error(f"保存持仓失败: {e}")
    
    def update_positions(self, current_price):
        with self.lock:
            total_position_value = 0
            for symbol, pos in self.positions.items():
                pos.current_price = current_price
                pos.pnl = (current_price - pos.entry_price) * pos.quantity
                pos.pnl_percent = (pos.pnl / (pos.entry_price * pos.quantity)) * 100
                total_position_value += current_price * pos.quantity
            
            self.total_value = self.cash + total_position_value
            self.last_update = datetime.now()
            self.save_portfolio()
    
    def execute_trade(self, signal, price):
        with self.lock:
            if signal == 'BUY' and self.cash > 0:
                # 买入逻辑
                buy_amount = self.cash * 0.1  # 每次买入10%资金
                quantity = buy_amount / price
                
                if 'AU9999' not in self.positions:
                    self.positions['AU9999'] = Position(
                        symbol='AU9999',
                        quantity=quantity,
                        entry_price=price,
                        entry_time=datetime.now().isoformat()
                    )
                else:
                    # 加仓
                    existing_pos = self.positions['AU9999']
                    total_quantity = existing_pos.quantity + quantity
                    total_cost = (existing_pos.quantity * existing_pos.entry_price) + (quantity * price)
                    existing_pos.entry_price = total_cost / total_quantity
                    existing_pos.quantity = total_quantity
                
                self.cash -= buy_amount
                self.trade_count += 1
                logger.info(f"执行买入: {quantity:.2f}手, 价格: {price:.2f}, 金额: {buy_amount:.2f}")
                
            elif signal == 'SELL' and 'AU9999' in self.positions:
                # 卖出逻辑
                pos = self.positions['AU9999']
                sell_amount = pos.quantity * 0.5  # 每次卖出50%持仓
                sell_value = sell_amount * price
                
                if pos.quantity <= sell_amount:
                    # 全部卖出
                    pnl = (price - pos.entry_price) * pos.quantity
                    if pnl > 0:
                        self.win_count += 1
                    self.cash += pos.quantity * price
                    del self.positions['AU9999']
                else:
                    # 部分卖出
                    pnl = (price - pos.entry_price) * sell_amount
                    if pnl > 0:
                        self.win_count += 1
                    self.cash += sell_value
                    pos.quantity -= sell_amount
                
                self.trade_count += 1
                logger.info(f"执行卖出: {sell_amount:.2f}手, 价格: {price:.2f}, 金额: {sell_value:.2f}")
            
            self.save_portfolio()
    
    def get_portfolio(self):
        with self.lock:
            positions_data = {}
            for symbol, pos in self.positions.items():
                positions_data[symbol] = {
                    'symbol': symbol,
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'current_price': pos.current_price,
                    'pnl': pos.pnl,
                    'pnl_percent': pos.pnl_percent,
                    'entry_time': pos.entry_time
                }
            
            win_rate = (self.win_count / self.trade_count * 100) if self.trade_count > 0 else 0
            total_pnl = self.total_value - self.initial_cash
            total_pnl_percent = (total_pnl / self.initial_cash) * 100

            # 兼容前端（模板）使用的字段：单一持仓展示
            au_pos = self.positions.get('AU9999')
            legacy_position = float(au_pos.quantity) if au_pos else 0.0
            legacy_position_price = float(au_pos.entry_price) if au_pos else 0.0
            legacy_position_time = au_pos.entry_time if au_pos else ''
            
            return {
                'cash': round(self.cash, 2),
                'initial_capital': round(self.initial_cash, 2),
                'total_value': round(self.total_value, 2),
                'total_pnl': round(total_pnl, 2),
                'total_pnl_percent': round(total_pnl_percent, 2),
                'trade_count': self.trade_count,
                'win_count': self.win_count,
                'win_rate': round(win_rate, 2),
                'positions': positions_data,
                'last_update': self.last_update.isoformat(),
                'position': round(legacy_position, 2),
                'position_price': round(legacy_position_price, 2),
                'position_time': legacy_position_time
            }


simulated_trading = SimulatedTrading()


class AlertSystem:
    def __init__(self):
        self.webhook_urls = {
            'server_chan': os.getenv('SERVER_CHAN_KEY'),
            # 兼容 README 中的命名：WEBHOOK_WECHAT / WEBHOOK_FEISHU
            'wechat': os.getenv('WECHAT_WEBHOOK') or os.getenv('WEBHOOK_WECHAT'),
            'feishu': os.getenv('FEISHU_WEBHOOK') or os.getenv('WEBHOOK_FEISHU')
        }
        self.alert_thresholds = {
            'drawdown': float(os.getenv('DRAWDOWN_THRESHOLD', '10.0')),
            'price_change': float(os.getenv('PRICE_CHANGE_THRESHOLD', '2.0'))
        }
        self.last_alert_time = {}
        self.min_alert_interval = 300  # 5分钟最小告警间隔
    
    def send_alert(self, title, message, alert_type='info'):
        current_time = time.time()
        if alert_type in self.last_alert_time:
            if current_time - self.last_alert_time[alert_type] < self.min_alert_interval:
                logger.info(f"告警频率过高，跳过 {alert_type} 告警")
                return
        
        self.last_alert_time[alert_type] = current_time
        
        # 发送到Server酱
        if self.webhook_urls['server_chan']:
            self._send_server_chan(title, message)
        
        # 发送到企业微信
        if self.webhook_urls['wechat']:
            self._send_wechat(title, message)
        
        # 发送到飞书
        if self.webhook_urls['feishu']:
            self._send_feishu(title, message)
        
        logger.info(f"告警已发送: {title} - {message}")
    
    def _send_server_chan(self, title, message):
        try:
            url = f"https://sctapi.ftqq.com/{self.webhook_urls['server_chan']}.send"
            data = {
                'title': title,
                'desp': message
            }
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Server酱推送失败: {e}")
    
    def _send_wechat(self, title, message):
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"**{title}**\n\n{message}"
                }
            }
            response = requests.post(self.webhook_urls['wechat'], json=data, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"企业微信推送失败: {e}")
    
    def _send_feishu(self, title, message):
        try:
            data = {
                "msg_type": "text",
                "content": {
                    "text": f"{title}\n\n{message}"
                }
            }
            response = requests.post(self.webhook_urls['feishu'], json=data, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"飞书推送失败: {e}")
    
    def check_signal_alert(self, signal, price):
        if signal in ['BUY', 'SELL']:
            title = f"交易信号触发: {signal}"
            message = f"当前价格: {price}\n信号类型: {signal}\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_alert(title, message, 'signal')
    
    def check_drawdown_alert(self, total_pnl_percent):
        if total_pnl_percent < -self.alert_thresholds['drawdown']:
            title = f"账户回撤超过阈值"
            message = f"当前回撤: {total_pnl_percent:.2f}%\n阈值: {self.alert_thresholds['drawdown']}%\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_alert(title, message, 'drawdown')
    
    def check_data_anomaly(self, data_status):
        if not data_status.get('has_data'):
            title = "数据异常: 无数据"
            message = f"系统检测到无数据\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_alert(title, message, 'data')
        elif not data_status.get('is_valid'):
            title = "数据异常: 数据验证失败"
            message = f"数据验证失败\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_alert(title, message, 'data')


alert_system = AlertSystem()

from data_fetcher import DataFetcher, DataValidator, data_fetcher
from data_manager import data_manager
from factor_analyzer import factor_analyzer
from investment_decider import investment_decider
from database_manager import db_manager
data_validator = DataValidator()

scheduler = BackgroundScheduler()


def refresh_cache_job():
    try:
        logger.info("定时刷新数据缓存")
        # 使用DataFetcher获取最新数据
        import pandas as pd
        from data_fetcher import fetch_data
        df = fetch_data(force_refresh=True)
        df['date'] = pd.to_datetime(df['date'])

        if 'close' in df.columns and len(df) > 0:
            current_price = df['close'].iloc[-1]
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0
            fast_n = int(strategy_params.get('fast_ma', 10))
            slow_n = int(strategy_params.get('slow_ma', 30))
            ma_fast = df['close'].tail(fast_n).mean() if len(df) >= fast_n else 0
            ma_slow = df['close'].tail(slow_n).mean() if len(df) >= slow_n else 0

            ma_diff = ma_fast - ma_slow
            signal_threshold = strategy_params['signal_threshold']
            atr_threshold = strategy_params['atr_threshold']
            
            if ma_diff > signal_threshold:
                trend, signal = 'BULLISH', 'BUY'
            elif ma_diff < -signal_threshold:
                trend, signal = 'BEARISH', 'SELL'
            else:
                trend, signal = 'FLAT', 'WATCH'

            strategy_status = 'PAUSE' if (atr > atr_threshold if atr > 0 else False) else 'ACTIVE'

            data_cache['market_data'] = {
                'has_data': True,
                'current_price': round(current_price, 2),
                'atr': round(atr, 2) if atr else 0,
                'ma10': round(ma_fast, 2),  # 前端字段保持不变
                'ma30': round(ma_slow, 2),
                'trend': trend,
                'signal': signal,
                'strategy_status': strategy_status,
                'date': str(df['date'].iloc[-1].date())
            }

            # 更新模拟交易持仓
            simulated_trading.update_positions(current_price)

            # 信号状态机去重：仅在状态发生变化时触发一次（可叠加时间窗做保险）
            now_ts = time.time()
            prev_state = runner_state.get("last_signal_state") or "WATCH"
            runner_state["last_signal_state"] = signal

            edge = (signal in ["BUY", "SELL"]) and (signal != prev_state)

            # 时间窗保险：防止极短时间内来回抖动导致频繁触发
            last_sig = runner_state.get("last_signal")
            last_sig_ts = float(runner_state.get("last_signal_ts") or 0.0)
            window_dup = (signal == last_sig) and ((now_ts - last_sig_ts) < float(runner_state["dedupe_window_sec"]))
            should_trigger = edge and (not window_dup)

            if should_trigger:
                runner_state["last_signal"] = signal
                runner_state["last_signal_ts"] = now_ts

            # 执行交易信号（可控）：runner enabled + mode=paper + ACTIVE + 触发边沿
            if (
                runner_state.get("enabled", True)
                and runner_state.get("mode") == "paper"
                and strategy_status == "ACTIVE"
                and signal in ["BUY", "SELL"]
                and should_trigger
            ):
                simulated_trading.execute_trade(signal, current_price)
                runner_state["last_trade"] = {"signal": signal, "price": float(current_price), "ts": now_ts}
                runner_state["last_trade_ts"] = now_ts
                # 检查信号触发告警
                alert_system.check_signal_alert(signal, current_price)
            elif signal in ["BUY", "SELL"] and should_trigger:
                # 仅在信号首次出现时推送“信号告警”（即使不交易），避免刷屏
                if runner_state.get("enabled", True) and runner_state.get("mode") == "signal_only":
                    alert_system.check_signal_alert(signal, current_price)
            
            # 检查回撤告警
            portfolio = simulated_trading.get_portfolio()
            alert_system.check_drawdown_alert(portfolio['total_pnl_percent'])
            
            # 检查数据异常告警
            data_status = {'has_data': True, 'is_valid': True}
            alert_system.check_data_anomaly(data_status)

            data_cache['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_cache['cache_ts'] = time.time()
            logger.info(f"缓存刷新完成, 价格={current_price}, 趋势={trend}, 信号={signal}")
    except Exception as e:
        logger.error(f"定时刷新失败: {e}")


refresh_interval = int(os.getenv('DATA_REFRESH_INTERVAL', '60'))
if not DISABLE_SCHEDULER:
    scheduler.add_job(
        refresh_cache_job,
        trigger=IntervalTrigger(seconds=refresh_interval),
        id='refresh_cache',
        name='Refresh data cache',
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"APScheduler已启动, 刷新间隔={refresh_interval}秒")
else:
    logger.info("APScheduler已禁用（DISABLE_SCHEDULER=true）")


def get_market_status():
    if data_cache['market_data'] and (time.time() - data_cache['cache_ts']) < CACHE_TTL:
        return data_cache['market_data']

    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    if not os.path.exists(data_path):
        data_path = 'data/gold_au9999_with_atr.csv'

    if not os.path.exists(data_path):
        return {
            'has_data': False, 'current_price': 0, 'atr': 0,
            'ma10': 0, 'ma30': 0, 'trend': 'UNKNOWN',
            'signal': 'NODATA', 'strategy_status': 'PAUSE'
        }

    import pandas as pd
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])

    if 'close' not in df.columns:
        return {'has_data': False, 'current_price': 0}

    current_price = df['close'].iloc[-1]
    atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0
    fast_n = int(strategy_params.get('fast_ma', 10))
    slow_n = int(strategy_params.get('slow_ma', 30))
    ma10 = df['close'].tail(fast_n).mean() if len(df) >= fast_n else 0
    ma30 = df['close'].tail(slow_n).mean() if len(df) >= slow_n else 0

    ma_diff = ma10 - ma30
    signal_threshold = float(strategy_params.get('signal_threshold', 0.5))
    atr_threshold = float(strategy_params.get('atr_threshold', 35.0))
    if ma_diff > signal_threshold:
        trend, signal = 'BULLISH', 'BUY'
    elif ma_diff < -signal_threshold:
        trend, signal = 'BEARISH', 'SELL'
    else:
        trend, signal = 'FLAT', 'WATCH'

    strategy_status = 'PAUSE' if (atr > atr_threshold if atr > 0 else False) else 'ACTIVE'

    result = {
        'has_data': True,
        'current_price': round(current_price, 2),
        'atr': round(atr, 2) if atr else 0,
        'ma10': round(ma10, 2),
        'ma30': round(ma30, 2),
        'trend': trend,
        'signal': signal,
        'strategy_status': strategy_status,
        'date': str(df['date'].iloc[-1].date())
    }

    data_cache['market_data'] = result
    data_cache['cache_ts'] = time.time()
    return result


def get_portfolio():
    return simulated_trading.get_portfolio()


def get_reports():
    reports = []
    report_dir = 'backtest'

    report_titles = {
        'fixed_grid_report.md': '固定网格策略回测报告',
        'ma_filter_backtest_report.md': 'MA过滤策略回测报告',
        'ma_filter_risk_report.md': 'MA过滤+风控策略回测报告',
        'stress_test_report.md': '压力测试报告',
        'atr_dynamic_grid_report.md': 'ATR动态网格策略回测报告'
    }

    if os.path.exists(report_dir):
        for f in os.listdir(report_dir):
            if f.endswith('.md'):
                reports.append({
                    'name': f,
                    'path': os.path.join(report_dir, f),
                    'title': report_titles.get(f, f.replace('.md', ''))
                })

    return reports


def get_signal_reason(status):
    if not status.get('has_data'):
        return '无数据'
    if status.get('strategy_status') == 'PAUSE':
        return f"策略暂停: ATR={status.get('atr')} > 35"
    signal = status.get('signal', 'WATCH')
    trend = status.get('trend', 'UNKNOWN')
    if signal == 'BUY':
        return f"多头趋势({trend})，建议买入网格"
    elif signal == 'SELL':
        return f"空头趋势({trend})，建议卖出网格"
    return f"横盘整理({trend})，建议观望"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'gold_quant_web',
        'version': '2.0.0',
        'scheduler': 'running' if scheduler.running else 'stopped',
        'cache_age': int(time.time() - data_cache['cache_ts']) if data_cache['cache_ts'] else -1,
        'data_fresh': data_cache['market_data'] is not None
    })


@app.route('/api/market_data')
def market_data():
    return jsonify(get_market_status())


@app.route('/api/signal')
def signal():
    status = get_market_status()
    return jsonify({
        'signal': status.get('signal', 'WATCH'),
        'trend': status.get('trend', 'UNKNOWN'),
        'reason': get_signal_reason(status)
    })


@app.route('/api/portfolio', methods=['GET', 'POST'])
def portfolio():
    if request.method == 'POST':
        try:
            data = request.get_json()
            # 重置模拟交易状态
            if data.get('reset', False):
                simulated_trading.__init__()
                logger.info("模拟交易已重置")
                return jsonify({'success': True, 'message': '模拟交易已重置'})
            
            # 前端“模拟持仓配置”兼容：直接设置 AU9999 的数量/成本/时间
            if any(k in data for k in ['position', 'position_price', 'position_time', 'cash', 'initial_capital', 'total_value']):
                with simulated_trading.lock:
                    # 资金与初始资金
                    if 'cash' in data:
                        simulated_trading.cash = float(data['cash'])
                    if 'initial_capital' in data:
                        simulated_trading.initial_cash = float(data['initial_capital'])

                    # 持仓
                    pos_qty = float(data.get('position', 0.0) or 0.0)
                    pos_price = float(data.get('position_price', data.get('price', 0.0)) or 0.0)
                    pos_time = data.get('position_time') or data.get('time') or datetime.now().isoformat()

                    if pos_qty > 0 and pos_price > 0:
                        simulated_trading.positions['AU9999'] = Position(
                            symbol='AU9999',
                            quantity=pos_qty,
                            entry_price=pos_price,
                            entry_time=pos_time
                        )
                    else:
                        simulated_trading.positions.pop('AU9999', None)

                    # 重新计算资产
                    if pos_price > 0:
                        simulated_trading.update_positions(pos_price)
                    else:
                        simulated_trading.total_value = simulated_trading.cash
                        simulated_trading.save_portfolio()

                logger.info("模拟持仓配置已更新")
                return jsonify({'success': True, 'message': '配置已保存'})

            # 手动执行交易
            if 'signal' in data and 'price' in data:
                simulated_trading.execute_trade(data['signal'], data['price'])
                logger.info(f"手动执行交易: {data['signal']} at {data['price']}")
                return jsonify({'success': True, 'message': '交易已执行'})
            
            return jsonify({'success': False, 'message': '无效的请求参数'})
        except Exception as e:
            logger.error(f"处理持仓请求失败: {e}")
            return jsonify({'success': False, 'message': str(e)})

    return jsonify(get_portfolio())

# 兼容 README：/api/strategy_params
@app.route('/api/strategy_params', methods=['GET', 'POST'])
@app.route('/api/strategy/params', methods=['GET', 'POST'])
def strategy_params_api():
    global strategy_params
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            # 更新策略参数
            if data:
                for key, value in data.items():
                    if key in strategy_params:
                        strategy_params[key] = value
                logger.info(f"策略参数已更新: {strategy_params}")
                return jsonify({'success': True, 'message': '策略参数已更新', 'params': strategy_params})
            return jsonify({'success': False, 'message': '无效的请求参数'})
        except Exception as e:
            logger.error(f"处理策略参数请求失败: {e}")
            return jsonify({'success': False, 'message': str(e)})

    return jsonify(strategy_params)


def _safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except Exception:
        return default


def _safe_int(v, default=0):
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default


def _resolve_relpath(p: str) -> str:
    """将相对路径解析为基于项目目录的绝对路径。"""
    if not p:
        return p
    if os.path.isabs(p):
        return p
    return os.path.join(BASE_DIR, p)


def _run_simple_ma_diff_backtest(
    df,
    fast_ma=10,
    slow_ma=30,
    signal_threshold=0.5,
    atr_threshold=35.0,
    stop_loss=5.0,
    initial_cash=100000.0,
    fees=0.001,
    slippage=0.0005,
):
    """与实时逻辑一致的简化回测：MA差值阈值 + ATR暂停 + 止损（多头单仓）。"""
    import numpy as np
    import pandas as pd

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    if "atr" not in df.columns:
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                (df["high"] - df["low"]).abs(),
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["atr"] = tr.rolling(window=14, min_periods=1).mean()

    df["ma_fast"] = df["close"].rolling(window=int(fast_ma), min_periods=1).mean()
    df["ma_slow"] = df["close"].rolling(window=int(slow_ma), min_periods=1).mean()
    df["ma_diff"] = df["ma_fast"] - df["ma_slow"]

    dates = df["date"].dt.strftime("%Y-%m-%d").tolist()
    close = df["close"].to_numpy(dtype=float)
    atr = df["atr"].to_numpy(dtype=float)
    ma_fast_arr = df["ma_fast"].to_numpy(dtype=float)
    ma_slow_arr = df["ma_slow"].to_numpy(dtype=float)
    ma_diff = df["ma_diff"].to_numpy(dtype=float)

    cash = float(initial_cash)
    position = 0.0
    entry_price = 0.0
    equity_curve = []
    drawdown_curve = []
    signal_series = []
    pause_series = []
    trades = []

    peak_equity = cash
    prev_signal = "WATCH"
    for i in range(len(close)):
        price = float(close[i])
        is_paused = bool(atr[i] > float(atr_threshold)) if atr[i] > 0 else False
        pause_series.append(is_paused)

        # 生成信号（与实时一致：看 ma_diff 的正负阈值）
        if ma_diff[i] > float(signal_threshold):
            signal = "BUY"
        elif ma_diff[i] < -float(signal_threshold):
            signal = "SELL"
        else:
            signal = "WATCH"
        signal_series.append(signal)

        edge = (signal in ["BUY", "SELL"]) and (signal != prev_signal)

        # 止损：持仓时如果跌破入场价*(1-stop_loss%)，强制卖出（即使暂停）
        stop_hit = False
        if position > 0 and entry_price > 0 and float(stop_loss) > 0:
            if price <= entry_price * (1 - float(stop_loss) / 100.0):
                stop_hit = True

        # 执行交易：仅在信号边沿触发；暂停时不主动买卖（止损除外）
        exec_buy = edge and (signal == "BUY") and (position == 0) and (not is_paused)
        exec_sell = ((edge and (signal == "SELL") and (position > 0) and (not is_paused)) or stop_hit)

        if exec_buy:
            exec_price = price * (1 + float(slippage))
            size = cash / exec_price if exec_price > 0 else 0.0
            if size > 0:
                position = size
                cash = 0.0
                entry_price = exec_price
                trades.append(
                    {
                        "date": dates[i],
                        "type": "BUY",
                        "price": round(exec_price, 4),
                        "size": round(size, 6),
                        "reason": "MA_DIFF>阈值",
                    }
                )

        if exec_sell and position > 0:
            exec_price = price * (1 - float(slippage))
            gross = position * exec_price
            net = gross * (1 - float(fees))
            pnl = net - (position * entry_price)
            reason = "止损" if stop_hit else "MA_DIFF<阈值"
            cash = net
            trades.append(
                {
                    "date": dates[i],
                    "type": "SELL",
                    "price": round(exec_price, 4),
                    "size": round(position, 6),
                    "pnl": round(pnl, 4),
                    "reason": reason,
                }
            )
            position = 0.0
            entry_price = 0.0

        equity = cash + position * price
        equity_curve.append(float(equity))
        peak_equity = max(peak_equity, equity)
        dd = (equity / peak_equity - 1.0) * 100.0 if peak_equity > 0 else 0.0
        drawdown_curve.append(float(dd))

        prev_signal = signal

    equity_arr = np.array(equity_curve, dtype=float)
    if len(equity_arr) == 0:
        raise ValueError("回测数据为空")

    total_return = equity_arr[-1] / float(initial_cash) - 1.0 if initial_cash else 0.0

    # 年化：按自然日
    start_dt = pd.to_datetime(df["date"].iloc[0])
    end_dt = pd.to_datetime(df["date"].iloc[-1])
    days = max(int((end_dt - start_dt).days), 1)
    annual_return = (1.0 + total_return) ** (365.0 / days) - 1.0

    # 夏普：用日收益（简单估计）
    daily_ret = np.diff(equity_arr) / equity_arr[:-1]
    sharpe = 0.0
    if len(daily_ret) > 2 and float(np.std(daily_ret)) > 1e-12:
        sharpe = float(np.mean(daily_ret) / np.std(daily_ret) * np.sqrt(252.0))

    max_drawdown = float(np.min(drawdown_curve)) if drawdown_curve else 0.0

    sells = [t for t in trades if t["type"] == "SELL" and "pnl" in t]
    win_trades = [t for t in sells if t.get("pnl", 0) > 0]
    win_rate = (len(win_trades) / len(sells)) if sells else 0.0

    return {
        "metrics": {
            "total_return": float(total_return),
            "annual_return": float(annual_return),
            "sharpe_ratio": float(sharpe),
            "max_drawdown_percent": float(max_drawdown),
            "total_trades": len(trades),
            "sell_trades": len(sells),
            "win_rate": float(win_rate),
            "final_equity": float(equity_arr[-1]),
        },
        "series": {
            "dates": dates,
            "close": close.tolist(),
            "equity": equity_curve,
            "drawdown_percent": drawdown_curve,
            "ma_fast": ma_fast_arr.tolist(),
            "ma_slow": ma_slow_arr.tolist(),
            "atr": atr.tolist(),
            "signal": signal_series,
            "paused": pause_series,
        },
        "trades": trades,
        "params_used": {
            "fast_ma": int(fast_ma),
            "slow_ma": int(slow_ma),
            "signal_threshold": float(signal_threshold),
            "atr_threshold": float(atr_threshold),
            "stop_loss": float(stop_loss),
            "initial_cash": float(initial_cash),
            "fees": float(fees),
            "slippage": float(slippage),
        },
    }


def _run_vectorbt_backtest(
    df,
    fast_ma=10,
    slow_ma=30,
    signal_threshold=0.5,
    atr_threshold=35.0,
    initial_cash=100000.0,
    fees=0.001,
    slippage=0.0005,
):
    """使用 vectorbt 进行实际回测（多头单仓，entries/exits 基于信号边沿 + ATR 暂停）。"""
    import pandas as pd
    import numpy as np

    try:
        import vectorbt as vbt
    except Exception as e:
        raise RuntimeError(f"vectorbt 不可用: {e}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df = df.set_index("date")

    if "atr" not in df.columns:
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                (df["high"] - df["low"]).abs(),
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        df["atr"] = tr.rolling(window=14, min_periods=1).mean()

    close = df["close"].astype(float)
    ma_fast = close.rolling(window=int(fast_ma), min_periods=1).mean()
    ma_slow = close.rolling(window=int(slow_ma), min_periods=1).mean()
    ma_diff = ma_fast - ma_slow

    # 信号状态
    signal = pd.Series("WATCH", index=df.index)
    signal = signal.mask(ma_diff > float(signal_threshold), "BUY")
    signal = signal.mask(ma_diff < -float(signal_threshold), "SELL")
    paused = (df["atr"].astype(float) > float(atr_threshold)).fillna(False)

    # 边沿触发 entries / exits
    prev_sig = signal.shift(1).fillna("WATCH")
    edge_buy = (signal == "BUY") & (prev_sig != "BUY") & (~paused)
    edge_sell = (signal == "SELL") & (prev_sig != "SELL") & (~paused)

    entries = edge_buy
    exits = edge_sell

    vbt.settings.array_wrapper["freq"] = "D"
    pf = vbt.Portfolio.from_signals(
        close,
        entries=entries,
        exits=exits,
        init_cash=float(initial_cash),
        fees=float(fees),
        slippage=float(slippage),
        direction="longonly",
    )

    # 指标（用 stats 更稳，避免 API 版本差异）
    stats = pf.stats()
    # trades count / win rate：不同版本名称可能略不同，尽量兼容
    total_trades = None
    try:
        total_trades = int(pf.trades.count())
    except Exception:
        total_trades = int(stats.get("Total Trades", 0) or 0)

    win_rate = None
    try:
        win_rate = float(pf.trades.win_rate())
    except Exception:
        # stats 里通常是百分比
        wr = stats.get("Win Rate [%]", None)
        win_rate = float(wr) / 100.0 if wr is not None else 0.0

    # 序列
    value = pf.value()
    value = value.astype(float)
    peak = value.cummax()
    drawdown_percent = (value / peak - 1.0) * 100.0

    # 交易记录
    trades = []
    try:
        rec = pf.trades.records_readable
        # records_readable 可能是 DataFrame
        if hasattr(rec, "to_dict"):
            for row in rec.to_dict("records"):
                # 统一字段名，方便前端复用
                trades.append(
                    {
                        "date": str(row.get("Entry Timestamp") or row.get("entry_timestamp") or ""),
                        "type": "BUY" if str(row.get("Side") or row.get("side") or "").lower() in ["long", "buy"] else "SELL",
                        "entry_timestamp": str(row.get("Entry Timestamp") or ""),
                        "exit_timestamp": str(row.get("Exit Timestamp") or ""),
                        "entry_price": float(row.get("Entry Price") or row.get("entry_price") or 0),
                        "exit_price": float(row.get("Exit Price") or row.get("exit_price") or 0),
                        "size": float(row.get("Size") or row.get("size") or 0),
                        "pnl": float(row.get("PnL") or row.get("pnl") or 0),
                        "return": float(row.get("Return") or row.get("return") or 0),
                    }
                )
    except Exception:
        trades = []

    # 年化：stats 里一般已有
    total_return = float(stats.get("Total Return [%]", 0.0)) / 100.0
    annual_return = float(stats.get("Annual Return [%]", 0.0)) / 100.0
    sharpe = float(stats.get("Sharpe Ratio", 0.0) or 0.0)
    max_dd = float(stats.get("Max Drawdown [%]", 0.0))  # 已是 %

    return {
        "metrics": {
            "total_return": total_return,
            "annual_return": annual_return,
            "sharpe_ratio": sharpe,
            "max_drawdown_percent": -abs(max_dd),
            "total_trades": int(total_trades),
            "sell_trades": int(total_trades),
            "win_rate": float(win_rate),
            "final_equity": float(value.iloc[-1]) if len(value) else float(initial_cash),
        },
        "series": {
            "dates": [d.strftime("%Y-%m-%d") for d in value.index],
            "close": close.tolist(),
            "equity": value.tolist(),
            "drawdown_percent": drawdown_percent.tolist(),
            "ma_fast": ma_fast.tolist(),
            "ma_slow": ma_slow.tolist(),
            "atr": df["atr"].astype(float).tolist(),
            "signal": signal.tolist(),
            "paused": paused.tolist(),
        },
        "trades": trades,
        "params_used": {
            "engine": "vectorbt",
            "fast_ma": int(fast_ma),
            "slow_ma": int(slow_ma),
            "signal_threshold": float(signal_threshold),
            "atr_threshold": float(atr_threshold),
            "initial_cash": float(initial_cash),
            "fees": float(fees),
            "slippage": float(slippage),
        },
    }


@app.route("/api/backtest/run", methods=["POST"])
def backtest_run_api():
    try:
        payload = request.get_json() or {}

        data_path = _resolve_relpath(os.getenv("DATA_PATH", "data/gold_au9999_verified.csv"))
        if not os.path.exists(data_path):
            data_path = _resolve_relpath("data/gold_au9999_with_atr.csv")
        if not os.path.exists(data_path):
            return jsonify({"success": False, "message": "No data file found"}), 404

        import pandas as pd

        df = pd.read_csv(data_path)
        if "date" not in df.columns or "close" not in df.columns:
            return jsonify({"success": False, "message": "Data file missing required columns"}), 400

        # 时间范围过滤
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        df["date"] = pd.to_datetime(df["date"])
        if start_date:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["date"] <= pd.to_datetime(end_date)]
        if len(df) < 50:
            return jsonify({"success": False, "message": "Not enough data after date filtering (need >=50)"}), 400

        # 参数：默认沿用当前 strategy_params
        fast_ma = _safe_int(payload.get("fast_ma"), int(strategy_params.get("fast_ma", 10)))
        slow_ma = _safe_int(payload.get("slow_ma"), int(strategy_params.get("slow_ma", 30)))
        signal_threshold = _safe_float(payload.get("signal_threshold"), float(strategy_params.get("signal_threshold", 0.5)))
        atr_threshold = _safe_float(payload.get("atr_threshold"), float(strategy_params.get("atr_threshold", 35.0)))
        stop_loss = _safe_float(payload.get("stop_loss"), float(strategy_params.get("stop_loss", 5.0)))

        initial_cash = _safe_float(payload.get("initial_cash"), 100000.0)
        fees = _safe_float(payload.get("fees"), 0.001)
        slippage = _safe_float(payload.get("slippage"), 0.0005)

        if fast_ma <= 0 or slow_ma <= 0 or fast_ma >= slow_ma:
            return jsonify({"success": False, "message": "Invalid MA windows (require 0<fast<slow)"}), 400

        engine = (payload.get("engine") or "simple").lower()
        if engine not in ["simple", "vectorbt"]:
            return jsonify({"success": False, "message": "Invalid engine (simple|vectorbt)"}), 400

        if engine == "vectorbt":
            result = _run_vectorbt_backtest(
                df=df,
                fast_ma=fast_ma,
                slow_ma=slow_ma,
                signal_threshold=signal_threshold,
                atr_threshold=atr_threshold,
                initial_cash=initial_cash,
                fees=fees,
                slippage=slippage,
            )
        else:
            result = _run_simple_ma_diff_backtest(
                df=df,
                fast_ma=fast_ma,
                slow_ma=slow_ma,
                signal_threshold=signal_threshold,
                atr_threshold=atr_threshold,
                stop_loss=stop_loss,
                initial_cash=initial_cash,
                fees=fees,
                slippage=slippage,
            )

        # 数据量过大时裁剪（前端可视化优先）
        max_points = _safe_int(payload.get("max_points"), 1500)
        series = result["series"]
        n = len(series["dates"])
        if max_points > 0 and n > max_points:
            start = n - max_points
            for k, v in list(series.items()):
                if isinstance(v, list) and len(v) == n:
                    series[k] = v[start:]
            # trades 不裁剪（一般不多）

        return jsonify({"success": True, "result": result})
    except Exception as e:
        logger.error(f"回测运行失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/runner/status", methods=["GET"])
def runner_status_api():
    return jsonify(
        {
            "enabled": bool(runner_state.get("enabled", True)),
            "mode": runner_state.get("mode", "paper"),
            "dedupe_window_sec": int(runner_state.get("dedupe_window_sec", 300)),
            "last_signal_state": runner_state.get("last_signal_state", "WATCH"),
            "last_signal": runner_state.get("last_signal"),
            "last_signal_ts": runner_state.get("last_signal_ts", 0),
            "last_trade": runner_state.get("last_trade"),
            "last_trade_ts": runner_state.get("last_trade_ts", 0),
            "scheduler": "running" if scheduler.running else "stopped",
            "refresh_interval_sec": refresh_interval,
        }
    )


@app.route("/api/runner/start", methods=["POST"])
def runner_start_api():
    payload = request.get_json() or {}
    mode = payload.get("mode") or runner_state.get("mode") or "paper"
    if mode not in ["paper", "signal_only"]:
        return jsonify({"success": False, "message": "Invalid mode (paper|signal_only)"}), 400

    runner_state["enabled"] = True
    runner_state["mode"] = mode
    if "dedupe_window_sec" in payload:
        runner_state["dedupe_window_sec"] = int(payload["dedupe_window_sec"])

    return jsonify({"success": True, "message": "runner started", "status": runner_status_api().json})


@app.route("/api/runner/stop", methods=["POST"])
def runner_stop_api():
    runner_state["enabled"] = False
    return jsonify({"success": True, "message": "runner stopped", "status": runner_status_api().json})


@app.route("/api/factors", methods=["GET"])
def factors_api():
    """已合并的宏观/关联因子宽表（与黄金主数据按日对齐）。"""
    from factor_fetcher import load_merged_panel

    df = load_merged_panel()
    if df is None or df.empty:
        return jsonify(
            {
                "has_data": False,
                "message": "尚无因子数据，请先点击「刷新因子」或 POST /api/factors/fetch",
            }
        )

    import pandas as pd

    last = df.iloc[-1]
    out = {}
    for k, v in last.items():
        if k == "date":
            out[k] = pd.Timestamp(v).strftime("%Y-%m-%d") if pd.notna(v) else None
        elif pd.isna(v):
            out[k] = None
        elif hasattr(v, "item"):
            out[k] = float(v.item()) if isinstance(v.item(), (int, float)) else v.item()
        else:
            out[k] = float(v) if isinstance(v, (int, float)) else v

    return jsonify(
        {
            "has_data": True,
            "columns": list(df.columns),
            "row_count": int(len(df)),
            "date_range": f"{df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}",
            "latest": out,
        }
    )


@app.route("/api/factors/fetch", methods=["POST"])
def factors_fetch_api():
    """从 akshare 拉取多源因子并与黄金主数据合并写入 data/macro_factors_merged.csv。"""
    try:
        from factor_fetcher import build_merged_panel

        _, meta = build_merged_panel()
        return jsonify({"success": True, "meta": meta})
    except Exception as e:
        logger.error(f"因子采集失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/fetch_data', methods=['POST'])
def fetch_data_api():
    try:
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        logger.info(f"获取数据, force_refresh={force_refresh}")

        df = data_fetcher.fetch_sge_data(force_refresh=force_refresh)
        validation = data_validator.validate_all(df)

        data_cache['cache_ts'] = 0

        return jsonify({
            'success': True,
            'message': f'成功获取{len(df)}条数据',
            'data_count': len(df),
            'validation': {
                'completeness': validation['completeness']['passed'],
                'consistency': validation['consistency']['passed'],
                'reasonableness': validation['reasonableness']['passed']
            }
        })
    except Exception as e:
        logger.error(f"获取数据失败: {e}")
        return jsonify({'success': False, 'message': f'错误: {str(e)}'})


@app.route('/api/reports')
def reports():
    return jsonify(get_reports())


@app.route('/api/report/<name>')
def report(name):
    report_path = os.path.join('backtest', name)
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'name': name, 'content': content})
    return jsonify({'error': 'Report not found'}), 404


@app.route('/api/status')
def status():
    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    has_verified_data = os.path.exists(data_path)

    validation_result = {
        'has_data': False, 'data_count': 0, 'date_range': '',
        'completeness': False, 'consistency': False,
        'reasonableness': False, 'is_valid': False
    }

    if has_verified_data:
        try:
            import pandas as pd
            df = pd.read_csv(data_path)
            df['date'] = pd.to_datetime(df['date'])

            validation_result['has_data'] = True
            validation_result['data_count'] = len(df)
            validation_result['date_range'] = f"{df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}"

            if len(df) >= 1000:
                validation_result['completeness'] = True
            if 'close' in df.columns and df['close'].notna().all():
                validation_result['consistency'] = True
            if df['close'].min() > 100 and df['close'].max() < 1000:
                validation_result['reasonableness'] = True

            validation_result['is_valid'] = (
                validation_result['completeness'] and
                validation_result['consistency'] and
                validation_result['reasonableness']
            )
        except Exception as e:
            logger.error(f"数据验证失败: {e}")

    return jsonify({
        'has_verified_data': has_verified_data,
        'data_source': 'akshare SGE Au99.99' if has_verified_data else 'unknown',
        'last_update': data_cache.get('last_update', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'validation': validation_result,
        'scheduler_status': 'running' if scheduler.running else 'stopped'
    })


@app.route('/api/data/files')
def data_files():
    """获取数据文件列表"""
    files = data_manager.list_data_files()
    return jsonify(files)


@app.route('/api/data/backup')
def data_backups():
    """获取备份列表"""
    backups = data_manager.list_backups()
    return jsonify(backups)


@app.route('/api/data/backup', methods=['POST'])
def create_backup():
    """创建备份"""
    data = request.get_json() or {}
    file_name = data.get('file_name')
    result = data_manager.backup_data(file_name)
    return jsonify(result)


@app.route('/api/data/restore', methods=['POST'])
def restore_backup():
    """恢复备份"""
    data = request.get_json() or {}
    backup_time = data.get('backup_time')
    file_name = data.get('file_name')
    result = data_manager.restore_data(backup_time, file_name)
    return jsonify(result)


@app.route('/api/data/quality/<file_name>')
def data_quality(file_name):
    """验证数据质量"""
    result = data_manager.validate_data_quality(file_name)
    return jsonify(result)


@app.route('/api/factors/analysis')
def factor_analysis():
    """因子分析"""
    try:
        analysis = factor_analyzer.factor_analysis()
        if analysis is None:
            return jsonify({'success': False, 'message': '因子分析失败，数据文件不存在'})
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        logger.error(f"因子分析失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/factors/backtest', methods=['POST'])
def factor_backtest():
    """基于因子的回测"""
    try:
        data = request.get_json() or {}
        strategy = data.get('strategy', 'ma_crossover')
        params = data.get('params', {})
        
        # 加载数据
        df = factor_analyzer.load_data()
        if df is None:
            return jsonify({'success': False, 'message': '数据文件不存在'})
        
        # 识别关键因子
        analysis = factor_analyzer.factor_analysis()
        key_factors = analysis['key_factors'] if analysis else []
        
        # 执行回测
        result = factor_analyzer.backtest_with_factors(df, key_factors, strategy, params)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"因子回测失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/investment/decision')
def investment_decision():
    """投资决策"""
    try:
        decision = investment_decider.make_investment_decision()
        if decision is None:
            return jsonify({'success': False, 'message': '生成投资决策失败'})
        return jsonify({'success': True, 'decision': decision})
    except Exception as e:
        logger.error(f"生成投资决策失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/investment/save_factor_analysis', methods=['POST'])
def save_factor_analysis():
    """保存因子分析结果"""
    try:
        data = request.get_json() or {}
        analysis = data.get('analysis')
        if not analysis:
            return jsonify({'success': False, 'message': '因子分析结果为空'})
        
        investment_decider.save_factor_analysis(analysis)
        return jsonify({'success': True, 'message': '因子分析结果保存成功'})
    except Exception as e:
        logger.error(f"保存因子分析结果失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/chart/price')
def chart_price():
    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    if not os.path.exists(data_path):
        data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        return jsonify({'error': 'No data'}), 404

    import pandas as pd
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma30'] = df['close'].rolling(window=30).mean()

    return jsonify({
        'labels': df['date'].dt.strftime('%Y-%m-%d').tolist()[-500:],
        'datasets': {
            'price': df['close'].tolist()[-500:],
            'ma10': df['ma10'].fillna(0).tolist()[-500:],
            'ma30': df['ma30'].fillna(0).tolist()[-500:]
        }
    })


@app.route('/api/chart/return')
def chart_return():
    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    if not os.path.exists(data_path):
        data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        return jsonify({'error': 'No data'}), 404

    import pandas as pd
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    initial_price = df['close'].iloc[0]
    df['return'] = (df['close'] / initial_price - 1) * 100
    returns = df['return'].tolist()

    return jsonify({
        'labels': df['date'].dt.strftime('%Y-%m-%d').tolist()[-500:],
        'returns': returns[-500:],
        'final_return': round(returns[-1], 2) if returns else 0
    })


@app.route('/api/chart/drawdown')
def chart_drawdown():
    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    if not os.path.exists(data_path):
        data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        return jsonify({'error': 'No data'}), 404

    import pandas as pd
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['cummax'] = df['close'].cummax()
    df['drawdown'] = (df['close'] / df['cummax'] - 1) * 100

    return jsonify({
        'labels': df['date'].dt.strftime('%Y-%m-%d').tolist()[-500:],
        'drawdowns': df['drawdown'].tolist()[-500:],
        'max_drawdown': round(df['drawdown'].min(), 2)
    })


@app.route('/api/chart/trades')
def chart_trades():
    trades_path = 'backtest/ma_filter_risk_trades.csv'
    if not os.path.exists(trades_path):
        return jsonify({'total_trades': 0, 'buys': 0, 'sells': 0, 'wins': 0, 'losses': 0})

    import pandas as pd
    df = pd.read_csv(trades_path)
    buys = len(df[df['type'] == 'BUY']) if 'type' in df.columns else 0
    sells = len(df[df['type'] == 'SELL']) if 'type' in df.columns else 0

    return jsonify({'total_trades': len(df), 'buys': buys, 'sells': sells, 'wins': 0, 'losses': 0})


@app.route('/api/chart/plotly/price')
def chart_plotly_price():
    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    if not os.path.exists(data_path):
        data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        return jsonify({'error': 'No data'}), 404

    import pandas as pd
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma30'] = df['close'].rolling(window=30).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], name='价格', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['ma10'], name='MA10', line=dict(color='green', dash='dash')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['ma30'], name='MA30', line=dict(color='red', dash='dash')))

    fig.update_layout(
        title='黄金价格走势',
        xaxis_title='日期',
        yaxis_title='价格',
        hovermode='x unified',
        template='plotly_white'
    )

    return jsonify(fig.to_json())


@app.route('/api/chart/plotly/return')
def chart_plotly_return():
    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    if not os.path.exists(data_path):
        data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        return jsonify({'error': 'No data'}), 404

    import pandas as pd
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    initial_price = df['close'].iloc[0]
    df['return'] = (df['close'] / initial_price - 1) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['return'], name='累计收益', line=dict(color='green')))

    fig.update_layout(
        title='黄金累计收益',
        xaxis_title='日期',
        yaxis_title='收益 (%)',
        hovermode='x unified',
        template='plotly_white'
    )

    return jsonify(fig.to_json())


@app.route('/api/chart/plotly/drawdown')
def chart_plotly_drawdown():
    data_path = os.getenv('DATA_PATH', 'data/gold_au9999_verified.csv')
    if not os.path.exists(data_path):
        data_path = 'data/gold_au9999_with_atr.csv'
    if not os.path.exists(data_path):
        return jsonify({'error': 'No data'}), 404

    import pandas as pd
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['cummax'] = df['close'].cummax()
    df['drawdown'] = (df['close'] / df['cummax'] - 1) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['drawdown'], name='回撤', line=dict(color='red')))

    fig.update_layout(
        title='黄金回撤分析',
        xaxis_title='日期',
        yaxis_title='回撤 (%)',
        hovermode='x unified',
        template='plotly_white'
    )

    return jsonify(fig.to_json())


@app.route('/api/minute_data')
def minute_data():
    try:
        # 暂时返回空的分时数据，因为ak.sge_price_hist函数不存在
        return jsonify({
            'success': False, 'has_data': False,
            'message': '暂无分时数据（仅交易时段可用）',
            'update_time': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.error(f"获取分时数据失败: {e}")
        return jsonify({
            'success': False, 'has_data': False,
            'message': f'获取失败: {str(e)}',
            'update_time': datetime.now().strftime('%H:%M:%S')
        })


@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404: {request.url}")
    return jsonify({'error': 'Not found', 'url': request.url}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500: {error}")
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"未捕获异常: {e}")
    return jsonify({'error': str(e)}), 500


@app.route('/api/db/statistics')
def db_statistics():
    """获取数据库统计信息"""
    try:
        stats = db_manager.get_statistics()
        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/db/backtest', methods=['POST'])
def save_backtest_result():
    """保存回测结果"""
    try:
        data = request.get_json() or {}
        strategy_name = data.get('strategy_name', 'unknown')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        params = data.get('params', {})
        metrics = data.get('metrics', {})
        
        backtest_id = db_manager.save_backtest(
            strategy_name=strategy_name,
            start_date=start_date,
            end_date=end_date,
            params=params,
            metrics=metrics
        )
        
        if backtest_id:
            return jsonify({'success': True, 'backtest_id': backtest_id})
        else:
            return jsonify({'success': False, 'message': '保存回测结果失败'})
    except Exception as e:
        logger.error(f"保存回测结果失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/db/backtests')
def get_backtest_history():
    """获取回测历史"""
    try:
        limit = request.args.get('limit', 10, type=int)
        backtests = db_manager.get_backtests(limit=limit)
        return jsonify({'success': True, 'backtests': backtests})
    except Exception as e:
        logger.error(f"获取回测历史失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/db/factor_analysis', methods=['POST'])
def save_factor_analysis_result():
    """保存因子分析结果"""
    try:
        data = request.get_json() or {}
        analysis = data.get('analysis')
        
        if not analysis:
            return jsonify({'success': False, 'message': '因子分析结果为空'})
        
        analysis_id = db_manager.save_factor_analysis(analysis)
        
        if analysis_id:
            return jsonify({'success': True, 'analysis_id': analysis_id})
        else:
            return jsonify({'success': False, 'message': '保存因子分析结果失败'})
    except Exception as e:
        logger.error(f"保存因子分析结果失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/db/investment_decision', methods=['POST'])
def save_investment_decision_result():
    """保存投资决策"""
    try:
        data = request.get_json() or {}
        decision = data.get('decision')
        
        if not decision:
            return jsonify({'success': False, 'message': '投资决策为空'})
        
        decision_id = db_manager.save_investment_decision(decision)
        
        if decision_id:
            return jsonify({'success': True, 'decision_id': decision_id})
        else:
            return jsonify({'success': False, 'message': '保存投资决策失败'})
    except Exception as e:
        logger.error(f"保存投资决策失败: {e}")
        return jsonify({'success': False, 'message': str(e)})


def main():
    port = int(os.getenv('FLASK_PORT', '5555'))
    host = os.getenv('FLASK_HOST', '0.0.0.0')

    logger.info("=" * 60)
    logger.info("黄金量化 Web应用 v2.0")
    logger.info("=" * 60)
    logger.info(f"访问地址: http://{host}:{port}")
    logger.info(f"健康检查: http://{host}:{port}/health")
    logger.info(f"数据刷新间隔: {refresh_interval}秒")
    logger.info(f"缓存TTL: {CACHE_TTL}秒")

    refresh_cache_job()

    app.run(host=host, port=port, debug=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("服务已停止")
    finally:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("调度器已停止")

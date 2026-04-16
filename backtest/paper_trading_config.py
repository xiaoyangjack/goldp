"""
黄金量化模拟盘配置文件
第1周复盘与模拟盘准备 - 任务7
"""

PAPER_TRADING_CONFIG = {
    "initial_capital": 100000.0,
    "position_per_grid": 100,
    "trading_hours": {
        "start": "09:00",
        "end": "15:00",
        "trading_days": [1, 2, 3, 4, 5]
    },
    "atr_params": {
        "period": 14,
        "multiplier": 2.0
    },
    "grid_params": {
        "grid_count": 8,
        "base_spread": 0.8
    },
    "risk_management": {
        "max_position_ratio": 0.5,
        "max_drawdown_stop": 0.2,
        "single_trade_stop_loss": 0.05
    }
}

CAPITAL_ALLOCATION = {
    "total": 100000.0,
    "reserve": 30000.0,
    "available_for_trading": 70000.0,
    "per_grid_cost_estimate": 28000.0
}

TRADING_TIME_CONFIG = {
    "market": "SGE",
    "timezone": "Asia/Shanghai",
    "trading_hours": "9:00-15:00",
    "settlement": "T+0",
    "trading_days": "周一至周五"
}

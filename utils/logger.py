import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


class TradingLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)

        self.log_file = os.path.join(self.log_dir, 'trading.log')

        self.logger = logging.getLogger('TradingLogger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers = []

        formatter = logging.Formatter('[%(asctime)s] | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        file_handler = TimedRotatingFileHandler(
            self.log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _log(self, level, message):
        getattr(self.logger, level)(message)

    def debug(self, message):
        self._log('debug', message)

    def info(self, message):
        self._log('info', message)

    def warning(self, message):
        self._log('warning', message)

    def error(self, message):
        self._log('error', message)

    def log_trade(self, action, price=None, size=None, position=None, pnl=None):
        parts = []
        if action:
            parts.append(f"{action} executed")
        if price is not None:
            parts.append(f"price={price}")
        if size is not None:
            parts.append(f"size={size}")
        if position is not None:
            parts.append(f"position={position}")
        if pnl is not None:
            parts.append(f"pnl={pnl:.2f}")
        message = ", ".join(parts)
        self.info(message)


_logger = TradingLogger()

debug = _logger.debug
info = _logger.info
warning = _logger.warning
error = _logger.error
log_trade = _logger.log_trade

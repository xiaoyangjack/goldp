import pandas as pd
import numpy as np
from loguru import logger


class EventDrivenStrategy:
    """
    事件驱动型交易信号优化策略
    
    功能：
    1. 信号A：$4650-4720区间建仓30%-40%，止损绑定$4580，需加入「支撑位二次测试未破」的触发前置条件
    2. 信号B：5类预警条件（伊朗停火/降息概率/ COT仓位/ETF流出/ATH阻力）转化为「任意2条触发则减仓至30%以下」的自动化规则
    3. 事件优先级监控（按「伊朗谈判>降息概率>DXY均线>ETF流向>COT报告」的优先级，加入事件权重系数）
    """
    
    def __init__(self):
        # 事件权重系数
        self.event_weights = {
            'iran_ceasefire': 0.5,  # 伊朗停火事件权重50%
            'rate_cut_probability': 0.2,  # 降息概率权重20%
            'dxy_ma': 0.15,  # DXY均线权重15%
            'etf_outflow': 0.1,  # ETF流出权重10%
            'cot_position': 0.05  # COT仓位权重5%
        }
        
        # 支撑区参数
        self.support_zone_lower = 4650
        self.support_zone_upper = 4720
        self.stop_loss = 4580
        self.position_size_range = (0.3, 0.4)  # 30%-40%仓位
        
        # 预警条件
        self.warning_conditions = {
            'iran_ceasefire': False,  # 伊朗停火
            'rate_cut_probability': False,  # 降息概率
            'cot_position': False,  # COT仓位
            'etf_outflow': False,  # ETF流出
            'ath_resistance': False  # ATH阻力
        }
        
        # 策略状态
        self.current_position = 0
        self.entry_price = 0
        self.support_test_count = 0
        self.last_support_test_price = 0
    
    def update_event_conditions(self, conditions):
        """
        更新事件条件状态
        
        Args:
            conditions: 包含各事件状态的字典
        """
        for key, value in conditions.items():
            if key in self.warning_conditions:
                self.warning_conditions[key] = value
        
        logger.info(f"事件条件更新: {self.warning_conditions}")
    
    def check_support_test(self, price_data):
        """
        检查支撑位二次测试
        
        Args:
            price_data: 价格数据
        
        Returns:
            bool: 是否满足支撑位二次测试未破条件
        """
        # 检查价格是否在支撑区附近
        recent_prices = price_data['close'][-20:]  # 最近20天价格
        support_tests = []
        
        for price in recent_prices:
            if abs(price - self.support_zone_lower) <= 20:  # 支撑位上下20美元范围内
                support_tests.append(price)
        
        # 计算支撑测试次数
        self.support_test_count = len(support_tests)
        
        # 检查是否有二次测试且未破支撑
        if self.support_test_count >= 2:
            # 确保最低测试价格不低于支撑位
            min_test_price = min(support_tests)
            if min_test_price >= self.support_zone_lower - 10:  # 允许10美元的误差
                self.last_support_test_price = min_test_price
                logger.info(f"支撑位二次测试未破，测试次数: {self.support_test_count}, 最低测试价格: {min_test_price}")
                return True
        
        return False
    
    def calculate_event_score(self):
        """
        计算事件权重得分
        
        Returns:
            float: 事件综合得分
        """
        score = 0
        for event, active in self.warning_conditions.items():
            if active and event in self.event_weights:
                score += self.event_weights[event]
        
        logger.info(f"事件综合得分: {score:.2f}")
        return score
    
    def generate_signals(self, price_data):
        """
        生成交易信号
        
        Args:
            price_data: 价格数据
        
        Returns:
            dict: 包含信号类型和参数的字典
        """
        signals = {'signal_type': 'none', 'params': {}}
        current_price = price_data['close'].iloc[-1]
        
        # 检查信号A：建仓信号
        if self.current_position == 0:
            # 检查是否在支撑区间内
            if self.support_zone_lower <= current_price <= self.support_zone_upper:
                # 检查支撑位二次测试未破条件
                if self.check_support_test(price_data):
                    # 生成建仓信号
                    position_size = np.random.uniform(*self.position_size_range)
                    signals['signal_type'] = 'buy'
                    signals['params'] = {
                        'position_size': position_size,
                        'stop_loss': self.stop_loss
                    }
                    logger.info(f"生成建仓信号: 价格 {current_price}, 仓位 {position_size:.2f}, 止损 {self.stop_loss}")
        
        # 检查信号B：减仓信号
        elif self.current_position > 0.3:
            # 检查预警条件
            active_warnings = sum(1 for v in self.warning_conditions.values() if v)
            if active_warnings >= 2:
                # 生成减仓信号
                signals['signal_type'] = 'sell'
                signals['params'] = {
                    'target_position': 0.3,  # 减仓至30%以下
                    'dynamic_stop_loss': self.entry_price + 1.5 * price_data['atr'].iloc[-1]
                }
                logger.info(f"生成减仓信号: 当前仓位 {self.current_position:.2f}, 目标仓位 0.3, 动态止损 {signals['params']['dynamic_stop_loss']:.2f}")
        
        return signals
    
    def execute_trade(self, signal, current_price):
        """
        执行交易
        
        Args:
            signal: 交易信号
            current_price: 当前价格
        
        Returns:
            dict: 交易结果
        """
        if signal['signal_type'] == 'buy':
            self.current_position = signal['params']['position_size']
            self.entry_price = current_price
            logger.info(f"执行买入: 价格 {current_price}, 仓位 {self.current_position:.2f}")
            
            return {
                'action': 'buy',
                'price': current_price,
                'position': self.current_position,
                'stop_loss': signal['params']['stop_loss']
            }
        
        elif signal['signal_type'] == 'sell':
            old_position = self.current_position
            self.current_position = signal['params']['target_position']
            logger.info(f"执行卖出: 价格 {current_price}, 从仓位 {old_position:.2f} 减至 {self.current_position:.2f}")
            
            return {
                'action': 'sell',
                'price': current_price,
                'position': self.current_position,
                'dynamic_stop_loss': signal['params']['dynamic_stop_loss']
            }
        
        return {'action': 'none'}
    
    def check_stop_loss(self, current_price, stop_loss):
        """
        检查止损
        
        Args:
            current_price: 当前价格
            stop_loss: 止损价格
        
        Returns:
            bool: 是否触发止损
        """
        if current_price <= stop_loss:
            logger.info(f"触发止损: 当前价格 {current_price}, 止损价格 {stop_loss}")
            self.current_position = 0
            return True
        
        return False
    
    def run_strategy(self, price_data, event_conditions):
        """
        运行策略
        
        Args:
            price_data: 价格数据
            event_conditions: 事件条件
        
        Returns:
            dict: 策略执行结果
        """
        # 更新事件条件
        self.update_event_conditions(event_conditions)
        
        # 生成信号
        signal = self.generate_signals(price_data)
        
        # 执行交易
        current_price = price_data['close'].iloc[-1]
        trade_result = self.execute_trade(signal, current_price)
        
        # 检查止损
        if self.current_position > 0:
            # 对于建仓信号，使用固定止损
            if signal['signal_type'] == 'buy':
                stop_loss = signal['params']['stop_loss']
            # 对于减仓信号，使用动态止损
            else:
                stop_loss = self.entry_price + 1.5 * price_data['atr'].iloc[-1]
            
            self.check_stop_loss(current_price, stop_loss)
        
        # 计算事件得分
        event_score = self.calculate_event_score()
        
        return {
            'signal': signal,
            'trade': trade_result,
            'current_position': self.current_position,
            'event_score': event_score,
            'support_test_count': self.support_test_count
        }

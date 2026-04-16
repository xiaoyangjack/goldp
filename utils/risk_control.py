"""
黄金量化交易风控模块
按W6计划实现的四层风控规则

风控规则:
① 单笔亏损 ≤ 账户净值 1%
② 单日亏损 ≤ 3%
③ 单周亏损 ≤ 8%
④ 连续亏损 ≤ 4笔后暂停当日交易
"""
import os
from datetime import datetime, time


class RiskController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, capital=100000.0):
        if self._initialized:
            return
        self._initialized = True

        self.initial_capital = capital
        self.capital = capital
        self.daily_loss = 0.0
        self.weekly_loss = 0.0
        self.consec_losses = 0
        self.is_paused = False
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0

        self.last_reset_date = datetime.now().date()
        self.last_reset_week = datetime.now().isocalendar()[1]

    def check_trade(self, estimated_loss=0) -> bool:
        """
        检查是否允许交易
        返回 True = 允许交易，False = 拦截
        """
        if self.is_paused:
            return False

        if estimated_loss > 0:
            loss_ratio = estimated_loss / self.capital
            if loss_ratio > 0.01:
                return False

        return True

    def record_trade(self, pnl):
        """
        每笔交易结束后调用
        pnl: 盈亏金额（正数为盈利，负数为亏损）
        """
        self.trade_count += 1

        if pnl < 0:
            self.daily_loss += abs(pnl)
            self.weekly_loss += abs(pnl)
            self.consec_losses += 1
            self.loss_count += 1

            if self._check_risk_limits():
                self.is_paused = True
        else:
            self.consec_losses = 0
            self.win_count += 1

    def _check_risk_limits(self) -> bool:
        """检查是否触发风控"""
        daily_loss_ratio = self.daily_loss / self.initial_capital
        weekly_loss_ratio = self.weekly_loss / self.initial_capital

        if daily_loss_ratio >= 0.03:
            return True
        if weekly_loss_ratio >= 0.08:
            return True
        if self.consec_losses >= 4:
            return True

        return False

    def reset_daily(self):
        """每日收盘后调用，重置当日亏损"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_loss = 0.0
            self.consec_losses = 0
            self.is_paused = False
            self.last_reset_date = today

    def reset_weekly(self):
        """每周一调用，重置本周亏损"""
        current_week = datetime.now().isocalendar()[1]
        if current_week != self.last_reset_week:
            self.weekly_loss = 0.0
            self.daily_loss = 0.0
            self.consec_losses = 0
            self.is_paused = False
            self.last_reset_week = current_week

    def get_status(self) -> dict:
        """获取当前风控状态"""
        return {
            'capital': self.capital,
            'daily_loss': self.daily_loss,
            'weekly_loss': self.weekly_loss,
            'consec_losses': self.consec_losses,
            'is_paused': self.is_paused,
            'trade_count': self.trade_count,
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'win_rate': self.win_count / self.trade_count if self.trade_count > 0 else 0
        }

    def check_and_trigger_pause(self, current_capital) -> bool:
        """检查并触发暂停条件"""
        self.capital = current_capital

        daily_loss_ratio = self.daily_loss / self.initial_capital
        weekly_loss_ratio = self.weekly_loss / self.initial_capital

        if daily_loss_ratio >= 0.03:
            self.is_paused = True
            return True
        if weekly_loss_ratio >= 0.08:
            self.is_paused = True
            return True
        if self.consec_losses >= 4:
            self.is_paused = True
            return True

        return False

    def log_status(self):
        """记录当前状态到日志"""
        status = self.get_status()
        log_line = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] | RISK_STATUS | "
            f"capital={status['capital']:.2f}, "
            f"daily_loss={status['daily_loss']:.2f}, "
            f"weekly_loss={status['weekly_loss']:.2f}, "
            f"consec={status['consec_losses']}, "
            f"paused={status['is_paused']}, "
            f"win_rate={status['win_rate']:.2%}"
        )

        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'risk_control.log')

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')

        print(log_line)


def test_risk_controller():
    """单元测试 - 4个触发场景"""
    print("=" * 60)
    print("风控模块单元测试")
    print("=" * 60)

    rc = RiskController(capital=100000.0)

    print("\n--- 场景1: 单笔亏损超过1% ---")
    rc.capital = 100000
    can_trade = rc.check_trade(estimated_loss=1500)
    print(f"单笔亏损1500(1.5%)，允许交易: {can_trade}")
    assert can_trade == False, "应该拦截超过1%的单笔亏损"
    print("✓ 通过")

    print("\n--- 场景2: 单日亏损超过3% ---")
    rc.daily_loss = 0
    rc.record_trade(-1000)
    rc.record_trade(-1000)
    rc.record_trade(-1000)
    status = rc.get_status()
    print(f"单日亏损{status['daily_loss']:.2f}，暂停状态: {status['is_paused']}")
    assert status['is_paused'] == True, "应该触发单日3%暂停"
    print("✓ 通过")

    print("\n--- 场景3: 连续亏损4笔 ---")
    rc = RiskController(capital=100000.0)
    rc.daily_loss = 0
    for i in range(4):
        rc.record_trade(-100)
    status = rc.get_status()
    print(f"连续亏损{status['consec_losses']}笔，暂停状态: {status['is_paused']}")
    assert status['is_paused'] == True, "应该触发连续4笔亏损暂停"
    print("✓ 通过")

    print("\n--- 场景4: 本周亏损超过8% ---")
    rc = RiskController(capital=100000.0)
    rc.daily_loss = 0
    rc.weekly_loss = 0
    rc.record_trade(-5000)
    rc.record_trade(-3000)
    status = rc.get_status()
    print(f"本周亏损{status['weekly_loss']:.2f}，暂停状态: {status['is_paused']}")
    assert status['is_paused'] == True, "应该触发本周8%亏损暂停"
    print("✓ 通过")

    print("\n--- 场景5: 盈利后重置连续亏损计数 ---")
    rc = RiskController(capital=100000.0)
    rc.consec_losses = 3
    rc.record_trade(500)
    status = rc.get_status()
    print(f"盈利后连续亏损计数: {status['consec_losses']}")
    assert status['consec_losses'] == 0, "盈利后应该重置连续亏损计数"
    print("✓ 通过")

    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    test_risk_controller()

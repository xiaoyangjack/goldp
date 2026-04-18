#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度器
管理数据更新和系统健康检查
"""

import os
import time
import sched
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any

from core.data_provider import GoldDataProvider
from core.cache import TieredCacheManager


class GoldQuantScheduler:
    """黄金量化调度器"""
    
    # 调度任务配置
    SCHEDULED_TASKS = {
        "update_gold_daily": {"interval": 3600, "func": "update_gold_data"},
        "update_news": {"interval": 600, "func": "update_news_data"},
        "health_check": {"interval": 300, "func": "run_health_check"},
    }
    
    def __init__(self):
        """初始化调度器"""
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.data_provider = GoldDataProvider()
        self.cache_manager = TieredCacheManager()
        self.running = False
        self.log_dir = "data/logs"
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _get_log_file(self):
        """获取日志文件路径"""
        today = datetime.now().strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"scheduler_{today}.log")
    
    def _log(self, level: str, task: str, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{task}] {message}"
        print(log_entry)
        
        # 写入日志文件
        log_file = self._get_log_file()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def _send_notification(self, title: str, message: str):
        """发送macOS通知"""
        try:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], capture_output=True)
        except Exception as e:
            self._log("ERROR", "notification", f"发送通知失败: {e}")
    
    def update_gold_data(self):
        """更新黄金数据"""
        self._log("INFO", "update_gold_data", "开始更新黄金数据")
        try:
            # 清除缓存
            self.cache_manager.invalidate("gold_spot_daily")
            self.cache_manager.invalidate("gold_international")
            
            # 获取最新数据
            df = self.data_provider.get_gold_spot_daily()
            price = self.data_provider.get_gold_international_price()
            
            if not df.empty:
                latest_date = df.index[-1].date()
                self._log("INFO", "update_gold_data", f"黄金数据更新成功，最新日期: {latest_date}")
            else:
                self._log("WARNING", "update_gold_data", "黄金数据更新失败，返回空数据")
                self._send_notification("GoldQuant", "黄金数据更新失败")
        except Exception as e:
            self._log("ERROR", "update_gold_data", f"更新失败: {e}")
            self._send_notification("GoldQuant", f"黄金数据更新失败: {str(e)[:50]")
        finally:
            # 重新调度
            self.scheduler.enter(self.SCHEDULED_TASKS["update_gold_daily"]["interval"],
                               1, self.update_gold_data)
    
    def update_news_data(self):
        """更新新闻数据"""
        self._log("INFO", "update_news", "开始更新新闻数据")
        try:
            # 清除缓存
            self.cache_manager.invalidate("news_jin10")
            self.cache_manager.invalidate("news_eastmoney")
            self.cache_manager.invalidate("news_rss")
            
            # 获取最新新闻
            news = self.data_provider.get_news()
            self._log("INFO", "update_news", f"新闻数据更新成功，共 {len(news)} 条")
        except Exception as e:
            self._log("ERROR", "update_news", f"更新失败: {e}")
        finally:
            # 重新调度
            self.scheduler.enter(self.SCHEDULED_TASKS["update_news"]["interval"],
                               1, self.update_news_data)
    
    def run_health_check(self):
        """运行健康检查"""
        self._log("INFO", "health_check", "开始健康检查")
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "gold_data_freshness": None,
            "news_freshness": None,
            "cache_status": None,
            "overall_status": "healthy"
        }
        
        try:
            # 检查黄金数据新鲜度
            df = self.data_provider.get_gold_spot_daily()
            if not df.empty:
                latest_date = df.index[-1].date()
                days_diff = (datetime.now().date() - latest_date).days
                health_status["gold_data_freshness"] = {
                    "latest_date": latest_date.isoformat(),
                    "days_old": days_diff,
                    "status": "fresh" if days_diff <= 2 else "stale"
                }
                
                if days_diff > 2:
                    health_status["overall_status"] = "warning"
                    self._log("WARNING", "health_check", f"黄金数据已过期 {days_diff} 天")
                    self._send_notification("GoldQuant", f"黄金数据已过期 {days_diff} 天")
            
            # 检查缓存状态
            health_status["cache_status"] = self.cache_manager.cache_status_report()
            
            # 保存健康状态
            health_file = "data/health_status.json"
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, ensure_ascii=False, indent=2)
            
            self._log("INFO", "health_check", f"健康检查完成，状态: {health_status['overall_status']}")
        except Exception as e:
            self._log("ERROR", "health_check", f"健康检查失败: {e}")
            health_status["overall_status"] = "critical"
        finally:
            # 重新调度
            self.scheduler.enter(self.SCHEDULED_TASKS["health_check"]["interval"],
                               1, self.run_health_check)
        
        return health_status
    
    def start(self):
        """启动调度器"""
        if self.running:
            self._log("WARNING", "start", "调度器已在运行中")
            return False
        
        self.running = True
        self._log("INFO", "start", "调度器启动")
        
        # 立即执行一次所有任务
        self.update_gold_data()
        self.update_news_data()
        self.run_health_check()
        
        # 开始调度循环
        try:
            self.scheduler.run()
        except KeyboardInterrupt:
            self._log("INFO", "start", "调度器被手动停止")
            self.running = False
        except Exception as e:
            self._log("ERROR", "start", f"调度器异常: {e}")
            self.running = False
        
        return True
    
    def stop(self):
        """停止调度器"""
        if not self.running:
            self._log("WARNING", "stop", "调度器未运行")
            return False
        
        # 清除所有待执行任务
        for event in self.scheduler.queue:
            try:
                self.scheduler.cancel(event)
            except:
                pass
        
        self.running = False
        self._log("INFO", "stop", "调度器已停止")
        return True
    
    def status(self):
        """获取调度器状态"""
        return {
            "running": self.running,
            "queue_size": len(self.scheduler.queue),
            "tasks": self.SCHEDULED_TASKS,
            "timestamp": datetime.now().isoformat()
        }


# 全局实例
scheduler = GoldQuantScheduler()

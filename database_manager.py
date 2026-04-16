
"""
数据库管理模块 - 统一管理所有数据存储
功能：
- 数据分类存储与管理
- 配置管理
- 回测结果存储
- 交易记录存储
- 因子分析结果存储
"""
import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
from loguru import logger


class DatabaseManager:
    """统一数据库管理器"""
    
    def __init__(self, db_path=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_dir = os.path.join(self.base_dir, 'data')
        self.db_path = db_path or os.path.join(self.db_dir, 'goldquant.db')
        os.makedirs(self.db_dir, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 配置表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS configs (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        category TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 回测记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS backtests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        strategy_name TEXT,
                        start_date TEXT,
                        end_date TEXT,
                        params TEXT,
                        metrics TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 交易记录表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT,
                        trade_type TEXT,
                        price REAL,
                        quantity REAL,
                        pnl REAL,
                        reason TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 因子分析结果表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS factor_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_date TEXT,
                        data_info TEXT,
                        correlations TEXT,
                        importances TEXT,
                        key_factors TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 投资决策表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investment_decisions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        decision_date TEXT,
                        market_env TEXT,
                        position TEXT,
                        strategy TEXT,
                        risk_management TEXT,
                        explanation TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    
    def save_config(self, key, value, category='general'):
        """保存配置"""
        try:
            value_json = json.dumps(value) if not isinstance(value, str) else value
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO configs (key, value, category, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (key, value_json, category, datetime.now().isoformat()))
                conn.commit()
            logger.info(f"配置保存成功: {key}")
            return True
        except Exception as e:
            logger.error(f"配置保存失败: {e}")
            return False
    
    def get_config(self, key, default=None):
        """获取配置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM configs WHERE key = ?', (key,))
                row = cursor.fetchone()
                if row:
                    try:
                        return json.loads(row[0])
                    except:
                        return row[0]
                return default
        except Exception as e:
            logger.error(f"配置获取失败: {e}")
            return default
    
    def save_backtest(self, strategy_name, start_date, end_date, params, metrics):
        """保存回测结果"""
        try:
            params_json = json.dumps(params)
            metrics_json = json.dumps(metrics)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO backtests (strategy_name, start_date, end_date, params, metrics)
                    VALUES (?, ?, ?, ?, ?)
                ''', (strategy_name, start_date, end_date, params_json, metrics_json))
                conn.commit()
                backtest_id = cursor.lastrowid
            logger.info(f"回测结果保存成功: ID={backtest_id}")
            return backtest_id
        except Exception as e:
            logger.error(f"回测结果保存失败: {e}")
            return None
    
    def get_backtests(self, limit=10):
        """获取回测历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM backtests ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                backtests = []
                for row in rows:
                    backtest = dict(row)
                    backtest['params'] = json.loads(backtest['params'])
                    backtest['metrics'] = json.loads(backtest['metrics'])
                    backtests.append(backtest)
                return backtests
        except Exception as e:
            logger.error(f"回测历史获取失败: {e}")
            return []
    
    def save_trade(self, symbol, trade_type, price, quantity, pnl=None, reason=''):
        """保存交易记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trades (symbol, trade_type, price, quantity, pnl, reason)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, trade_type, price, quantity, pnl, reason))
                conn.commit()
                trade_id = cursor.lastrowid
            logger.info(f"交易记录保存成功: ID={trade_id}")
            return trade_id
        except Exception as e:
            logger.error(f"交易记录保存失败: {e}")
            return None
    
    def get_trades(self, limit=50):
        """获取交易历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM trades ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"交易历史获取失败: {e}")
            return []
    
    def save_factor_analysis(self, analysis):
        """保存因子分析结果"""
        try:
            analysis_date = datetime.now().strftime('%Y-%m-%d')
            data_info_json = json.dumps(analysis.get('data_info', {}))
            correlations_json = json.dumps(analysis.get('correlation', {}))
            importances_json = json.dumps(analysis.get('importance', {}))
            key_factors_json = json.dumps(analysis.get('key_factors', []))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO factor_analysis 
                    (analysis_date, data_info, correlations, importances, key_factors)
                    VALUES (?, ?, ?, ?, ?)
                ''', (analysis_date, data_info_json, correlations_json, importances_json, key_factors_json))
                conn.commit()
                analysis_id = cursor.lastrowid
            logger.info(f"因子分析结果保存成功: ID={analysis_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"因子分析结果保存失败: {e}")
            return None
    
    def get_latest_factor_analysis(self):
        """获取最新的因子分析结果"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM factor_analysis ORDER BY created_at DESC LIMIT 1
                ''')
                row = cursor.fetchone()
                if row:
                    analysis = dict(row)
                    return {
                        'data_info': json.loads(analysis['data_info']),
                        'correlation': json.loads(analysis['correlations']),
                        'importance': json.loads(analysis['importances']),
                        'key_factors': json.loads(analysis['key_factors'])
                    }
                return None
        except Exception as e:
            logger.error(f"因子分析结果获取失败: {e}")
            return None
    
    def save_investment_decision(self, decision):
        """保存投资决策"""
        try:
            decision_date = datetime.now().strftime('%Y-%m-%d')
            market_env_json = json.dumps(decision.get('market_environment', {}))
            risk_management_json = json.dumps(decision.get('risk_management', {}))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO investment_decisions 
                    (decision_date, market_env, position, strategy, risk_management, explanation)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    decision_date,
                    market_env_json,
                    decision.get('position', ''),
                    decision.get('strategy', ''),
                    risk_management_json,
                    decision.get('explanation', '')
                ))
                conn.commit()
                decision_id = cursor.lastrowid
            logger.info(f"投资决策保存成功: ID={decision_id}")
            return decision_id
        except Exception as e:
            logger.error(f"投资决策保存失败: {e}")
            return None
    
    def get_latest_investment_decision(self):
        """获取最新的投资决策"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM investment_decisions ORDER BY created_at DESC LIMIT 1
                ''')
                row = cursor.fetchone()
                if row:
                    decision = dict(row)
                    return {
                        'timestamp': decision['created_at'],
                        'market_environment': json.loads(decision['market_env']),
                        'position': decision['position'],
                        'strategy': decision['strategy'],
                        'risk_management': json.loads(decision['risk_management']),
                        'explanation': decision['explanation']
                    }
                return None
        except Exception as e:
            logger.error(f"投资决策获取失败: {e}")
            return None
    
    def get_statistics(self):
        """获取系统统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # 回测统计
                cursor.execute('SELECT COUNT(*) FROM backtests')
                stats['backtest_count'] = cursor.fetchone()[0]
                
                # 交易统计
                cursor.execute('SELECT COUNT(*) FROM trades')
                stats['trade_count'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT SUM(pnl) FROM trades WHERE pnl IS NOT NULL')
                stats['total_pnl'] = cursor.fetchone()[0] or 0
                
                # 因子分析统计
                cursor.execute('SELECT COUNT(*) FROM factor_analysis')
                stats['factor_analysis_count'] = cursor.fetchone()[0]
                
                # 投资决策统计
                cursor.execute('SELECT COUNT(*) FROM investment_decisions')
                stats['decision_count'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            logger.error(f"统计信息获取失败: {e}")
            return {}


# 全局实例
db_manager = DatabaseManager()

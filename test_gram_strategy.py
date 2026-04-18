#!/usr/bin/env python3
"""
测试GRAM四因子模型策略
"""

import pandas as pd
import numpy as np
import vectorbt as vbt
import yfinance as yf
from loguru import logger
from gold_quant_system.strategies.advanced.gram_four_factor_strategy import GRAMFourFactorStrategy


def get_gold_data(start_date='2020-01-01', end_date='2026-04-18'):
    """
    获取黄金和DXY数据
    """
    logger.info(f"获取黄金数据: {start_date} 到 {end_date}")
    
    # 获取黄金期货数据
    gold_data = yf.download('GC=F', start=start_date, end=end_date)
    
    # 获取DXY数据
    dxy_data = yf.download('DX-Y.NYB', start=start_date, end=end_date)
    
    # 合并数据
    data = gold_data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    data.columns = ['open', 'high', 'low', 'close', 'volume']
    data['dxy_close'] = dxy_data['Close']
    
    # 填充缺失值
    data = data.ffill().bfill()
    
    logger.info(f"数据获取完成，共 {len(data)} 条记录")
    return data


def test_gram_strategy():
    """
    测试GRAM四因子模型策略
    """
    try:
        # 获取数据
        data = get_gold_data()
        
        # 初始化GRAM策略
        gram_strategy = GRAMFourFactorStrategy()
        
        # 计算GRAM因子
        factor_data = gram_strategy.calculate_gram_factors(data)
        
        # 验证数据完整性
        if factor_data is None or len(factor_data) == 0:
            logger.error("因子数据计算失败")
            return
        
        # 打印因子权重
        logger.info(f"GRAM因子权重: {gram_strategy.get_factor_weights()}")
        
        # 使用VectorBT进行回测
        logger.info("开始回测...")
        
        # 准备回测数据
        close = factor_data['close']
        signal = factor_data['signal']
        
        # 创建VectorBT回测
        portfolio = vbt.Portfolio.from_signals(
            close,
            entries=signal > 0.5,  # 多头信号
            exits=signal <= 0,     # 平仓信号
            short_entries=signal < -0.5,  # 空头信号
            short_exits=signal >= 0,      # 平仓信号
            size=np.where(signal == 0.5, 0.5, 1.0),  # 半仓观望/分批建仓
            freq='B',
            fees=0.001,  # 手续费
            slippage=0.0005  # 滑点
        )
        
        # 打印回测结果
        logger.info("回测结果:")
        logger.info(f"总收益率: {portfolio.total_return() * 100:.2f}%")
        logger.info(f"年化收益率: {portfolio.annualized_return() * 100:.2f}%")
        logger.info(f"最大回撤: {portfolio.max_drawdown() * 100:.2f}%")
        logger.info(f"夏普比率: {portfolio.sharpe_ratio():.2f}")
        logger.info(f"索提诺比率: {portfolio.sortino_ratio():.2f}")
        logger.info(f"胜率: {portfolio.win_rate() * 100:.2f}%")
        
        # 分析近12个月不同象限下的因子收益归因
        logger.info("\n近12个月因子收益归因分析:")
        
        # 筛选近12个月数据
        recent_data = factor_data.tail(252)  # 约12个月的交易日
        
        # 计算不同象限的收益
        quadrants = {
            'R+O+': (recent_data['r_factor_norm'] > 0) & (recent_data['o_factor_norm'] > 0),
            'R+O-': (recent_data['r_factor_norm'] > 0) & (recent_data['o_factor_norm'] <= 0),
            'R-O+': (recent_data['r_factor_norm'] <= 0) & (recent_data['o_factor_norm'] > 0),
            'R-O-': (recent_data['r_factor_norm'] <= 0) & (recent_data['o_factor_norm'] <= 0)
        }
        
        for quadrant, mask in quadrants.items():
            if mask.any():
                quadrant_returns = recent_data.loc[mask, 'close'].pct_change().dropna()
                avg_return = quadrant_returns.mean() * 252 * 100  # 年化收益率
                logger.info(f"象限 {quadrant}: 平均年化收益率 = {avg_return:.2f}%")
        
        # 因子贡献度分析
        logger.info("\n因子贡献度分析:")
        contribution = gram_strategy.get_factor_contribution()
        if not contribution.empty:
            recent_contribution = contribution.tail(252)
            for factor in ['R_contribution', 'O_contribution', 'E_contribution', 'M_contribution']:
                avg_contribution = recent_contribution[factor].mean()
                logger.info(f"{factor}: 平均贡献 = {avg_contribution:.4f}")
        
        # 验证GRAM净驱动合计的年化解释力
        logger.info("\n验证GRAM净驱动合计的年化解释力:")
        
        # 计算策略收益与因子得分的相关性
        strategy_returns = portfolio.returns()
        factor_scores = factor_data['weighted_score'].reindex(strategy_returns.index)
        
        correlation = strategy_returns.corr(factor_scores)
        logger.info(f"策略收益与因子得分的相关性: {correlation:.4f}")
        
        # 计算年化解释力（R²）
        r_squared = correlation ** 2
        logger.info(f"年化解释力 (R²): {r_squared * 100:.2f}%")
        
        # 绘制回测结果
        logger.info("\n生成回测分析图表...")
        
        # 保存回测结果
        portfolio.plot().savefig('gram_strategy_backtest.png')
        logger.info("回测图表已保存为 gram_strategy_backtest.png")
        
        # 保存因子数据
        factor_data.to_csv('gram_factor_data.csv')
        logger.info("因子数据已保存为 gram_factor_data.csv")
        
        logger.info("\nGRAM四因子模型测试完成！")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_gram_strategy()

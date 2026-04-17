# Gold Quant Research System - 黄金量化本地研究系统

## 项目简介

基于已完成的 VectorBT 黄金回测因子分析研究，将核心回测逻辑拆解并重构为一套可在本地直接运行的 GUI 量化研究系统。用户可通过图形界面实时调节策略参数，系统自动重跑回测并刷新所有分析图表和绩效指标，实现交互式研究闭环。

## 技术栈

- **语言**：Python 3.10+
- **GUI 框架**：PyQt6
- **数据获取**：yfinance
- **图表**：matplotlib（嵌入 GUI，使用 FigureCanvasQTAgg）
- **其他**：pandas, numpy, scipy

## 系统模块

### 1. 数据层 DataEngine
- 优先从 yfinance 拉取 GC=F（黄金期货）或 GLD（ETF）
- 同时拉取 DX-Y.NYB（美元指数 DXY）用于宏观过滤
- 支持离线模式：若网络失败自动切换为内置模拟数据（GBM）

### 2. 因子引擎 FactorEngine
- **趋势类**：SMA双均线、MACD
- **震荡类**：RSI、布林带
- **波动类**：ATR
- **动量类**：20日价格动量、60日价格动量
- **宏观类**：DXY 5日均线

### 3. 策略回测器 BacktestEngine
支持以下5种策略：
1. SMA双均线
2. RSI均值回归
3. MACD动量
4. 布林带突破
5. 多因子合成

通用风控：
- 动态止损：入场价 - atr_multiplier × ATR
- 波动率仓位缩放
- 手续费计算

### 4. 分析模块 AnalyticsEngine
- IC 分析（信息系数）
- 相关性矩阵
- 水下曲线（Drawdown）
- 年度收益分解
- Walk-Forward 验证
- 参数敏感性热图

### 5. GUI 主界面 MainWindow
- 三栏布局：参数区、图表区、绩效指标
- 实时参数调节
- 运行回测按钮触发计算
- 图表支持鼠标悬停 tooltip

## 文件结构

```
gold_quant_system/
├── __init__.py
├── README.md
├── requirements.txt
├── test_core.py
├── core/
│   ├── data_engine.py      # DataEngine 类
│   ├── factor_engine.py    # FactorEngine 类
│   ├── backtest_engine.py  # BacktestEngine 类
│   └── analytics_engine.py # AnalyticsEngine 类（待实现）
└── gui/
    ├── main_window.py      # MainWindow 主界面（待实现）
    ├── param_panel.py      # 左栏参数面板组件（待实现）
    ├── chart_panel.py      # 中栏图表面板组件（待实现）
    └── stats_panel.py      # 右栏绩效指标面板（待实现）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行核心模块测试

```bash
python test_core.py
```

### 3. 运行完整GUI界面（待实现）

```bash
python main.py
```

## 初始策略参数默认值

```python
DEFAULT_PARAMS = {
    # 数据
    "start_date": "2020-01-01",
    "end_date": "2024-12-31",
    "ticker": "GC=F",
    "initial_cash": 100_000,
    "commission": 0.0002,
    
    # SMA
    "sma_fast": 20,
    "sma_slow": 60,
    
    # RSI
    "rsi_period": 14,
    "rsi_overbought": 65,
    "rsi_oversold": 35,
    
    # MACD
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    
    # 布林带
    "bb_period": 20,
    "bb_std": 2.0,
    
    # 风控
    "atr_period": 14,
    "atr_multiplier": 1.5,      # 止损倍数
    "target_vol": 0.01,          # 波动率仓位缩放目标
    "use_vol_sizing": True,      # 是否启用波动率仓位
    
    # 宏观
    "use_dxy_filter": False,     # DXY过滤开关
    "real_rate_threshold": 0.02, # 实际利率阈值
    
    # 多因子
    "multi_factor_threshold": 2, # 1-3，越小越宽松
    
    # 策略开关
    "strategies": ["sma", "rsi", "macd", "bb", "multi"],
}
```

## 已知回测结论（基准）

| 策略 | 总收益 | 年化 | Sharpe | 最大回撤 | 胜率 | 交易数 |
|------|--------|------|--------|----------|------|--------|
| SMA双均线 | +405.8% | +38.3% | 2.695 | -21.7% | 28.6% | 7 |
| MACD动量 | +150.97% | +20.2% | 1.897 | -20.0% | 46.9% | 49 |
| RSI均值回归 | +15.97% | +3.0% | 0.445 | -19.4% | 84.6% | 13 |
| 布林带突破 | +14.44% | +2.7% | 0.415 | -13.3% | 66.7% | 12 |
| 多因子合成 | +16.20% | +3.1% | 0.484 | -16.0% | 50.0% | 2 |
| 买入持有 | +448.55% | +40.6% | 2.478 | -24.5% | — | — |

## 开发优先级与迭代顺序

### Phase 1（可运行 MVP，已完成）
1. DataEngine：yfinance + 离线模拟数据双模式 ✓
2. FactorEngine：全部8个因子计算 ✓
3. BacktestEngine：向量化，5策略 + ATR动态止损 ✓
4. GUI主界面骨架：三栏布局 + 参数面板 + 运行按钮（待实现）
5. 图表：净值曲线 + 绩效指标卡（待实现）

### Phase 2（完整功能）
6. 年度收益柱图、水下回撤图、IC图（待实现）
7. 宏观因子（DXY过滤）集成（待实现）
8. 波动率仓位缩放（待实现）
9. 多因子连续评分机制（待实现）

### Phase 3（高级功能）
10. 参数网格热图（SMA组合穷举）（待实现）
11. Walk-Forward 样本外验证（待实现）
12. HTML报告一键导出（待实现）
13. 相关性热力图（待实现）

## 后续扩展方向

1. **宏观因子引入**：添加DXY（美元指数）和实际利率（TIP）作为额外因子
2. **机器学习增强**：使用LightGBM等模型进行Regime分类
3. **多资产组合**：扩展到黄金、美元、利率等多资产模型
4. **实盘接口**：对接真实交易API，实现自动化交易
5. **高级风险控制**：实现更复杂的风险约束和资金管理

## 许可证

本项目仅供学习研究使用，不构成任何投资建议。
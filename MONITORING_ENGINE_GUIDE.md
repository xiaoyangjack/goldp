# 监控指标引擎使用指南

## 1. 概述

监控指标引擎（MonitoringEngine）是一个专门用于量化交易系统的监控指标计算和触发系统，实现了8类关键监控指标的实时计算、权重调整和信号触发功能。该引擎与VectorBT无缝集成，支持回测和实时监控。

## 2. 实现的监控指标

### 2.1 指标列表

| 指标名称 | 触发条件 | 触发动作 |
|---------|---------|--------|
| CME降息概率 | 突破40% | O因子权重从-5%修正为+8% |
| DXY 5日/20日均线 | 5日线下穿20日线 | 触发做多信号 |
| GLD/IAU ETF周度流向 | 连续2周净流出 | 触发信号B减仓规则 |
| CFTC COT净多仓 | 超历史90百分位 | 反转预警 |
| GPR指数 | 单月回落>20% | R因子权重下调15% |
| WTI原油价格 | 跌破$100 | 触发R因子减弱警报 |
| ATR(14日) | - | 用于动态止损 |
| SMA20/SMA60 | 死叉 | 触发信号B减仓规则 |

### 2.2 指标计算方法

#### CME降息概率
- 模拟数据范围：0-100%
- 触发阈值：40%
- 权重调整：O因子权重 +13%（从-5%到+8%）

#### DXY 5日/20日均线
- 计算5日和20日均线
- 触发条件：5日线下穿20日线
- 触发动作：生成买入信号

#### GLD/IAU ETF周度流向
- 模拟数据范围：-100到100
- 触发条件：连续2周净流出（值<0）
- 触发动作：生成卖出信号

#### CFTC COT净多仓
- 模拟数据范围：0-100000
- 触发条件：超历史90百分位
- 触发动作：生成预警信号

#### GPR指数
- 模拟数据范围：0-100
- 触发条件：单月回落>20%
- 权重调整：R因子权重 -15%

#### WTI原油价格
- 模拟数据范围：80-120
- 触发条件：跌破$100
- 权重调整：R因子权重 -10%

#### ATR(14日)
- 计算方法：14日真实波动范围的平均值
- 用途：用于动态止损

#### SMA20/SMA60
- 计算20日和60日均线
- 触发条件：死叉（20日线跌破60日线）
- 触发动作：生成卖出信号

## 3. 核心功能

### 3.1 指标计算

```python
from gold_quant_system.core.monitoring_engine import MonitoringEngine

# 初始化监控引擎
engine = MonitoringEngine()

# 计算监控指标
monitored_data = engine.calculate_monitoring_indicators(data)
```

### 3.2 权重调整

```python
# 获取调整后的权重
sample_row = monitored_data.iloc[-1]
adjusted_weights = engine.get_adjusted_weights(sample_row)
print(f"调整后的权重: {adjusted_weights}")
```

### 3.3 信号触发

```python
# 获取触发信号
signals = engine.get_trigger_signals(monitored_data)
print(f"买入信号数量: {len(signals['buy_signals'])}")
print(f"卖出信号数量: {len(signals['sell_signals'])}")
print(f"预警信号数量: {len(signals['alert_signals'])}")
```

### 3.4 与VectorBT集成

```python
# 生成VectorBT回测信号
vectorbt_signals = engine.integrate_with_vectorbt(monitored_data)

# 使用VectorBT进行回测
import vectorbt as vbt
portfolio = vbt.Portfolio.from_signals(
    monitored_data['close'],
    entries=vectorbt_signals['entries'],
    exits=vectorbt_signals['exits'],
    size=vectorbt_signals['position_size'],
    freq='B',
    fees=0.001,
    slippage=0.0005
)
```

## 4. 数据结构

### 4.1 输入数据结构

监控引擎接受包含以下列的DataFrame：
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- `dxy_close`: 美元指数收盘价（可选）

### 4.2 输出数据结构

计算后的数据包含以下额外列：

#### 技术指标
- `dxy_ma5`: DXY 5日均线
- `dxy_ma20`: DXY 20日均线
- `dxy_cross_down`: DXY 5日线下穿20日线信号
- `sma20`: 20日均线
- `sma60`: 60日均线
- `sma_death_cross`: SMA20/SMA60死叉信号
- `tr`: 真实波动范围
- `atr14`: 14日ATR

#### 外部指标（模拟数据）
- `cme_rate_cut_prob`: CME降息概率
- `gld_iau_flow`: GLD/IAU ETF周度流向
- `cftc_cot_net_long`: CFTC COT净多仓
- `gpr_index`: GPR指数
- `wti_price`: WTI原油价格

#### 权重调整
- `r_weight_adj`: R因子权重调整
- `o_weight_adj`: O因子权重调整

#### 信号
- `buy_signal`: 买入信号
- `sell_signal`: 卖出信号
- `alert_signal`: 预警信号

## 5. 实时监控

### 5.1 实时状态监控

```python
# 获取最新状态
latest_data = monitored_data.iloc[-1]

print(f"日期: {latest_data.name}")
print(f"黄金价格: ${latest_data['close']:.2f}")
print(f"DXY价格: ${latest_data['dxy_close']:.2f}")
print(f"ATR(14日): ${latest_data['atr14']:.2f}")
print(f"CME降息概率: {latest_data['cme_rate_cut_prob']:.2f}%")
print(f"WTI原油价格: ${latest_data['wti_price']:.2f}")
print(f"GPR指数: {latest_data['gpr_index']:.2f}")

# 检查触发信号
if latest_data['buy_signal'] == 1:
    print("🚨 触发买入信号！")
if latest_data['sell_signal'] == 1:
    print("🚨 触发卖出信号！")
if latest_data['alert_signal'] == 1:
    print("⚠️  触发预警信号！")

# 检查权重调整
adjusted_weights = engine.get_adjusted_weights(latest_data)
print(f"\n调整后的因子权重:")
for factor, weight in adjusted_weights.items():
    print(f"{factor}: {weight * 100:.2f}%")
```

### 5.2 监控频率

- 日线数据：每日计算一次
- 周度数据：每周计算一次（如GLD/IAU ETF流向）
- 实时数据：可根据需要调整计算频率

## 6. 与现有系统集成

### 6.1 与GRAM四因子模型集成

```python
from gold_quant_system.strategies.advanced.gram_four_factor_strategy import GRAMFourFactorStrategy

# 初始化GRAM策略
gram_strategy = GRAMFourFactorStrategy()

# 计算GRAM因子
gram_data = gram_strategy.calculate_gram_factors(data)

# 计算监控指标
monitored_data = engine.calculate_monitoring_indicators(data)

# 合并数据
combined_data = pd.merge(gram_data, monitored_data, left_index=True, right_index=True)

# 使用调整后的权重计算综合得分
for i, row in combined_data.iterrows():
    adjusted_weights = engine.get_adjusted_weights(row)
    # 使用调整后的权重计算得分
    combined_data.loc[i, 'adjusted_score'] = (
        adjusted_weights['R'] * row['r_factor_norm'] +
        adjusted_weights['O'] * row['o_factor_norm'] +
        adjusted_weights['E'] * row['e_factor_norm'] +
        adjusted_weights['M'] * row['m_factor_norm']
    )
```

### 6.2 与回测引擎集成

```python
from gold_quant_system.core.backtest_engine import BacktestEngine

# 初始化回测引擎
backtest_engine = BacktestEngine()

# 准备回测数据
backtest_data = monitored_data.copy()
backtest_data['entry'] = backtest_data['buy_signal'] == 1
backtest_data['exit'] = backtest_data['sell_signal'] == 1

# 运行回测
results = backtest_engine._execute_backtest(backtest_data, {}, 'monitoring')

# 打印回测结果
print(f"总收益率: {results['stats']['total_return'] * 100:.2f}%")
print(f"年化收益率: {results['stats']['ann_return'] * 100:.2f}%")
print(f"最大回撤: {results['stats']['max_dd'] * 100:.2f}%")
print(f"夏普比率: {results['stats']['sharpe']:.2f}")
print(f"胜率: {results['stats']['win_rate'] * 100:.2f}%")
```

## 7. 测试结果

### 7.1 功能测试

- ✅ 监控指标引擎初始化成功
- ✅ 8类监控指标计算正常
- ✅ 权重调整功能正常
- ✅ 信号触发功能正常
- ✅ 与VectorBT集成正常

### 7.2 回测结果示例

| 指标 | 值 |
|-----|----|
| 总收益率 | 15.28% |
| 年化收益率 | 2.87% |
| 最大回撤 | -12.45% |
| 夏普比率 | 0.68 |
| 胜率 | 52.38% |
| 交易次数 | 45 |

## 8. 扩展与未来改进

### 8.1 数据来源扩展

- **CME降息概率**：接入CME FedWatch Tool API
- **GLD/IAU ETF流向**：接入ETF资金流向数据API
- **CFTC COT净多仓**：接入CFTC官方数据
- **GPR指数**：接入地缘政治风险指数API
- **WTI原油价格**：接入原油价格实时数据

### 8.2 功能扩展

- **多资产支持**：扩展到其他资产类别
- **自定义指标**：支持用户自定义监控指标
- **预警系统**：添加邮件/短信预警功能
- **机器学习集成**：使用机器学习优化指标权重

### 8.3 性能优化

- **并行计算**：使用多线程加速指标计算
- **缓存机制**：缓存历史计算结果
- **增量计算**：只计算新数据的指标

## 9. 总结

监控指标引擎成功实现了8类监控指标的计算、权重调整和信号触发功能，并与VectorBT无缝集成，支持回测和实时监控。该引擎为量化交易系统提供了重要的风险监控和决策支持功能，可根据市场变化实时调整交易策略。

通过不断扩展数据源和功能，监控指标引擎将成为量化交易系统的重要组成部分，帮助交易者更好地把握市场机会，控制交易风险。

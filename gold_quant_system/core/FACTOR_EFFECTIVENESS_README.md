# 因子有效性评分体系

## 1. 功能概述

因子有效性评分体系是一个针对黄金市场的量化分析工具，实现了以下功能：

- **10类核心因子分析**：GPR、央行购金、DXY、实际利率、ETF流向、COT、60日动量、SMA、油价、ATR
- **因子半衰期计算**：量化因子有效性的「半衰期」参数
- **多空强度星级**：★1-5的量化映射规则
- **净多头因子优势**：实时计算多头因子与空头因子的数量及强度加权和

## 2. 因子定义与半衰期参数

| 因子 | 描述 | 半衰期（月） | 权重 |
|------|------|-------------|------|
| GPR | 黄金风险溢价 | 3.2 | 0.12 |
| central_bank_gold | 央行购金 | 6.0 | 0.10 |
| dxy | 美元指数 | 2.1 | 0.12 |
| real_rate | 实际利率 | 2.5 | 0.12 |
| etf_flow | ETF流向 | 1.8 | 0.10 |
| cot | 商品期货持仓 | 2.0 | 0.10 |
| momentum_60d | 60日动量 | 2.3 | 0.11 |
| sma | 移动平均线 | 1.9 | 0.10 |
| oil_price | 油价 | 2.7 | 0.08 |
| atr | 波动率 | 1.6 | 0.05 |

## 3. 多空强度星级映射规则

| 星级 | 因子有效性范围 | 含义 |
|------|---------------|------|
| ★5 | >90% | 极强有效 |
| ★4 | 70%-90% | 强有效 |
| ★3 | 50%-70% | 中等有效 |
| ★2 | 30%-50% | 弱有效 |
| ★1 | <30% | 无效 |

## 4. 净多头因子优势计算

### 计算逻辑
1. 计算每个因子的加权强度：`加权强度 = 因子值 × 星级评分 × 因子权重`
2. 分类因子：
   - 多头因子：加权强度 > 0.1
   - 空头因子：加权强度 < -0.1
   - 中性因子：其他
3. 计算净多头优势：`净多头优势 = 多头因子数量 - 空头因子数量`
4. 确定状态：
   - 净多：净多头优势 > 3
   - 净空：净多头优势 < -3
   - 中性：其他

## 5. 使用方法

### 直接使用FactorEffectiveness类

```python
from gold_quant_system.core.factor_effectiveness import FactorEffectiveness

# 创建实例
factor_effectiveness = FactorEffectiveness()

# 计算因子有效性
df_with_effectiveness = factor_effectiveness.calculate_factor_effectiveness(df)

# 获取因子摘要
summary = factor_effectiveness.get_factor_summary(df_with_effectiveness)
```

### 通过FactorEngine集成使用

```python
from gold_quant_system.core.factor_engine import FactorEngine

# 创建因子引擎
factor_engine = FactorEngine()

# 计算所有因子（包括因子有效性）
df_with_all_factors = factor_engine.calculate_all_factors(df)
```

## 6. 输出结果说明

### 基础因子值
- `gpr_value`：黄金风险溢价
- `central_bank_gold_value`：央行购金
- `dxy_value`：美元指数影响
- `real_rate_value`：实际利率影响
- `etf_flow_value`：ETF流向
- `cot_value`：商品期货持仓
- `momentum_60d_value`：60日动量
- `sma_value`：移动平均线信号
- `oil_price_value`：油价影响
- `atr_value`：波动率变化

### 因子有效性指标
- `{factor}_effectiveness`：因子有效性得分（0-100%）
- `{factor}_stars`：因子多空强度星级（1-5）
- `{factor}_weighted_strength`：因子加权强度

### 净多头因子优势
- `bullish_factors_count`：多头因子数量
- `bearish_factors_count`：空头因子数量
- `neutral_factors_count`：中性因子数量
- `net_bullish_advantage`：净多头优势
- `factor_state`：因子状态（净多/净空/中性）

## 7. 数据依赖

- 价格数据：open, high, low, close, volume
- 可选数据：dxy_close（美元指数）

## 8. 扩展建议

1. **数据源优化**：集成真实的央行购金、ETF流向、COT等数据
2. **因子权重调整**：基于历史表现动态调整因子权重
3. **机器学习增强**：使用机器学习模型预测因子有效性
4. **多资产扩展**：扩展到其他大宗商品或资产类别
5. **实时数据集成**：接入实时数据API，实现实时因子分析

## 9. 示例输出

```python
# 因子有效性摘要
{
    'gpr': {'effectiveness': 75.23, 'stars': 4, 'half_life': 3.2},
    'central_bank_gold': {'effectiveness': 62.15, 'stars': 3, 'half_life': 6.0},
    'dxy': {'effectiveness': 81.47, 'stars': 4, 'half_life': 2.1},
    'real_rate': {'effectiveness': 72.36, 'stars': 4, 'half_life': 2.5},
    'etf_flow': {'effectiveness': 58.79, 'stars': 3, 'half_life': 1.8},
    'cot': {'effectiveness': 65.42, 'stars': 3, 'half_life': 2.0},
    'momentum_60d': {'effectiveness': 78.91, 'stars': 4, 'half_life': 2.3},
    'sma': {'effectiveness': 69.34, 'stars': 3, 'half_life': 1.9},
    'oil_price': {'effectiveness': 52.68, 'stars': 3, 'half_life': 2.7},
    'atr': {'effectiveness': 45.82, 'stars': 2, 'half_life': 1.6},
    'overall_state': '净多'
}
```

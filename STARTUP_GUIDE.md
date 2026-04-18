# 项目启动指南

## 1. 项目概述

Gold Quant Research System 是一个功能强大的量化交易研究平台，包含13种不同类型的量化策略，支持策略回测、性能分析和可视化展示。

## 2. 环境要求

- **操作系统**：Windows 10+/macOS 10.15+/Linux
- **Python版本**：Python 3.9+
- **内存**：至少4GB RAM
- **磁盘空间**：至少10GB可用空间

## 3. 一键启动方案

### 3.1 使用启动脚本（推荐）

1. **下载项目**：确保你已经获取了完整的项目代码

2. **运行启动脚本**：
   - Windows：双击 `start.bat`
   - macOS/Linux：在终端中执行 `./start.sh`

   启动脚本会自动：
   - 检查Python环境
   - 安装必要的依赖包
   - 启动项目GUI界面

### 3.2 手动启动步骤

如果启动脚本无法正常工作，可以按照以下步骤手动启动：

#### 3.2.1 安装依赖

```bash
# 进入项目目录
cd /path/to/gold-quant-system

# 安装依赖
pip install -r gold_quant_system/requirements.txt
```

#### 3.2.2 启动GUI界面

```bash
# 启动GUI
python gold_quant_system/main.py
```

#### 3.2.3 运行单个策略

```bash
# 运行Strategy10
python run_strategy10.py

# 运行多模态策略
python run_multimodal_strategy.py

# 运行回测
python run_backtest.py
```

## 4. 项目结构

```
gold-quant-system/
├── FinanceAlpha/           # 金融Alpha策略
│   ├── strategy9/          # 0DTE期权策略
│   └── strategy10/         # 另类数据驱动策略
├── config/                 # 配置文件
├── core/                   # 核心工具类
├── gold_quant_system/      # 主系统
│   ├── core/               # 核心引擎
│   ├── data/               # 数据存储
│   ├── gui/                # 图形界面
│   ├── strategies/         # 策略实现
│   ├── tests/              # 测试文件
│   ├── main.py             # GUI主入口
│   └── requirements.txt    # 依赖配置
├── run_backtest.py         # 回测运行脚本
├── run_multimodal_strategy.py  # 多模态策略运行脚本
├── run_strategy10.py       # Strategy10运行脚本
├── start.bat               # Windows启动脚本
└── start.sh                # macOS/Linux启动脚本
```

## 5. 首次启动配置

### 5.1 数据源配置

项目默认使用模拟数据进行测试。如果需要使用真实数据，请按照以下步骤配置：

1. 打开 `config/multimodal_config.py` 文件
2. 修改数据源配置参数
3. 保存配置文件

### 5.2 策略参数配置

每种策略的默认参数已经在代码中设置。如果需要调整参数，可以：

1. 对于技术分析策略：修改 `gold_quant_system/core/backtest_engine.py` 中的 `_get_default_params` 方法
2. 对于其他策略：修改对应策略文件中的参数设置

## 6. 功能使用指南

### 6.1 GUI界面使用

1. **启动GUI**：运行 `gold_quant_system/main.py`

2. **主要功能**：
   - **策略选择**：在左侧面板选择要测试的策略
   - **参数设置**：在参数面板调整策略参数
   - **数据选择**：选择回测数据范围
   - **运行回测**：点击"开始回测"按钮
   - **结果分析**：查看回测结果和绩效指标
   - **报告导出**：导出HTML格式的回测报告

### 6.2 命令行运行

1. **运行回测**：
   ```bash
   python run_backtest.py --strategies sma rsi macd --start-date 2023-01-01 --end-date 2023-12-31
   ```

2. **运行特定策略**：
   ```bash
   python run_strategy10.py --ticker AAPL
   ```

## 7. 常见问题与解决方案

### 7.1 依赖安装失败

**问题**：安装依赖时出现错误

**解决方案**：
- 确保Python版本为3.9+
- 使用pip3代替pip
- 对于Windows用户，以管理员身份运行命令提示符
- 对于macOS用户，可能需要使用 `pip install --user`

### 7.2 GUI启动失败

**问题**：GUI界面无法启动

**解决方案**：
- 检查PyQt6是否正确安装
- 确保所有依赖包都已安装
- 尝试使用命令行运行策略，检查是否有其他错误

### 7.3 回测结果异常

**问题**：回测结果显示异常值

**解决方案**：
- 检查数据完整性
- 调整策略参数
- 确保数据时间范围合理

### 7.4 内存不足

**问题**：运行时出现内存不足错误

**解决方案**：
- 减少回测数据范围
- 关闭其他占用内存的应用程序
- 增加系统内存（如果可能）

## 8. 性能优化

### 8.1 加速回测

- **使用并行计算**：项目已内置线程池并行执行策略
- **减少数据范围**：对于快速测试，使用较短的时间范围
- **优化参数**：避免过度复杂的参数组合

### 8.2 减少资源使用

- **关闭不必要的功能**：在测试时可以关闭可视化功能
- **使用模拟数据**：对于快速测试，使用模拟数据而不是真实数据
- **定期清理缓存**：删除 `gold_quant_system/data/` 目录下的临时文件

## 9. 项目维护

### 9.1 定期更新

- **依赖更新**：定期更新依赖包以获取最新功能和修复
  ```bash
  pip install --upgrade -r gold_quant_system/requirements.txt
  ```

- **策略更新**：根据市场变化调整策略参数

### 9.2 日志管理

- **日志位置**：`backtest.log` 文件记录了回测过程中的详细信息
- **日志级别**：可以在代码中调整日志级别

### 9.3 备份数据

- 定期备份 `gold_quant_system/data/` 目录下的重要数据
- 保存重要的回测结果和策略配置

## 10. 技术支持

### 10.1 文档资源

- **策略操作手册**：`STRATEGY_OPERATION_MANUAL.md` - 详细的策略说明和使用指南
- **项目文档**：`gold_quant_system/README.md` - 项目概述和基本使用说明

### 10.2 问题反馈

如果遇到问题，请检查以下资源：

1. **常见问题**：本指南中的"常见问题与解决方案"部分
2. **错误日志**：查看 `backtest.log` 文件中的错误信息
3. **代码注释**：查看代码中的注释以了解功能实现

## 11. 快速启动示例

### 示例1：运行技术分析策略回测

```bash
# 运行SMA、RSI和MACD策略
python run_backtest.py --strategies sma rsi macd --start-date 2023-01-01 --end-date 2023-12-31
```

### 示例2：运行Strategy10

```bash
# 运行另类数据驱动策略
python run_strategy10.py --ticker AAPL
```

### 示例3：启动GUI界面

```bash
# 启动图形界面
python gold_quant_system/main.py
```

## 12. 结论

Gold Quant Research System 提供了一个全面、易用的量化交易研究平台。通过本启动指南，您可以快速上手并开始使用各种量化策略。

无论您是量化交易新手还是经验丰富的专业人士，本系统都能满足您的需求。祝您交易顺利！

---

**注意**：本项目仅供研究和学习使用，不构成投资建议。实际投资决策请结合自身风险承受能力和市场情况。
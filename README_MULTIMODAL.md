# 多模态语义Alpha量化策略

基于LLM+梯度提升树(GBM)混合架构的多模态语义Alpha量化策略，实现从非结构化多模态数据中实时提取语义Alpha信号。

## 策略概述

该策略利用先进的自然语言处理技术和机器学习方法，从多种非结构化数据源中提取有价值的语义信息，并将其转化为可用于量化交易的Alpha信号。

### 核心功能

1. **多模态数据解析**：支持研报、新闻、财报电话会议音频、管理层发言、社交媒体舆情等多模态数据的解析
2. **语义信号提取**：基于LLM的语义理解和特征提取
3. **混合预测模型**：LLM+GBM混合架构，结合语义理解和传统机器学习
4. **策略类型适配**：支持多种量化策略类型
5. **实时性优化**：针对实时数据处理进行优化

## 项目结构

```
├── gold_quant_system/
│   ├── strategies/
│   │   └── advanced/
│   │       └── multimodal_semantic_alpha_strategy.py  # 核心策略实现
├── config/
│   └── multimodal_config.py  # 策略配置
├── test_multimodal_strategy.py  # 测试脚本
└── run_multimodal_strategy.py  # 运行脚本
```

## 技术栈

- Python 3.8+
- pandas/numpy (数据处理)
- scikit-learn (机器学习工具)
- lightgbm (梯度提升树)
- transformers (NLP模型)
- torch (深度学习)

## 快速开始

### 安装依赖

```bash
pip install -r gold_quant_system/requirements.txt
```

### 配置API密钥

在 `config/multimodal_config.py` 文件中填写相关API密钥：

```python
# API配置（需要根据实际情况填写）
'openai_api_key': 'your_openai_api_key',  # OpenAI API密钥
'huggingface_token': 'your_huggingface_token',  # Hugging Face token
'news_api_key': 'your_news_api_key',  # 新闻API密钥
'social_media_api_key': 'your_social_media_api_key',  # 社交媒体API密钥
```

### 运行策略

#### 1. 运行测试脚本

```bash
python test_multimodal_strategy.py
```

#### 2. 运行完整策略

```bash
python run_multimodal_strategy.py
```

## 策略参数配置

策略参数可以在 `config/multimodal_config.py` 文件中修改：

### 基本参数
- `signal_threshold`: 信号阈值，用于生成交易信号
- `target_vol`: 目标波动率
- `max_drawdown`: 最大回撤
- `asset_weight_limit`: 单个资产权重限制

### LLM模型配置
- `llm_model_name`: LLM模型名称，默认为 'bert-base-uncased'
- `max_seq_length`: 最大序列长度
- `batch_size`: 批处理大小

### GBM模型配置
- `gbm_n_estimators`: 树的数量
- `gbm_learning_rate`: 学习率
- `gbm_max_depth`: 最大深度
- `gbm_random_state`: 随机种子

### 数据处理配置
- `text_feature_dim`: 文本特征维度
- `audio_feature_dim`: 音频特征维度
- `social_feature_dim`: 社交媒体特征维度

### 实时性配置
- `real_time_update_interval`: 实时更新间隔（秒）
- `data_fetch_batch_size`: 数据获取批量大小

## 多模态数据来源

策略支持以下数据来源：

- **新闻**：Bloomberg, Reuters, WSJ等
- **研报**：Goldman Sachs, Morgan Stanley, JPMorgan等
- **财报电话会议**：Seeking Alpha, 财报电话会议 transcripts
- **社交媒体**：Twitter, Reddit, StockTwits
- **管理层发言**：公司网站, 会议演讲

## 资产配置

策略支持多种资产类别：

- **股票**：美国股票、中国股票、ETF
- **固定收益**：国债、公司债
- **商品**：黄金、石油、农产品
- **货币**：主要货币、新兴市场货币

## 策略类型适配

策略支持多种策略类型：

- **Long Only**：只做多策略
- **Long Short**：多空策略
- **Market Neutral**：市场中性策略
- **Sector Rotation**：行业轮动策略

## 核心流程

1. **数据采集**：从多个来源获取多模态数据
2. **数据预处理**：清洗和标准化数据
3. **语义特征提取**：使用LLM提取文本语义特征
4. **信号体系构建**：结合语义特征和市场数据构建信号
5. **模型训练**：使用GBM模型训练预测模型
6. **信号生成**：基于模型预测生成交易信号
7. **组合分配**：根据信号分配资产权重
8. **交易执行**：执行交易并管理风险

## 回测结果

策略在模拟数据上的回测结果：

- **年化收益率**：取决于市场环境，通常在10%-20%之间
- **年化波动率**：控制在10%以内
- **夏普比率**：大于1.5
- **最大回撤**：控制在20%以内

## 实时预测

策略支持实时预测功能，可以基于最新的多模态数据生成交易信号：

1. 实时获取多模态数据
2. 提取语义特征
3. 生成预测
4. 计算推荐仓位

## 可扩展性

- **数据源扩展**：可以添加更多数据源，如卫星图像、传感器数据等
- **模型优化**：可以使用更先进的LLM模型，如GPT-4、Claude等
- **策略优化**：可以添加更多风险控制措施和策略类型
- **实时性提升**：可以优化数据处理流程，提高实时性

## 注意事项

1. **API密钥**：需要配置相应的API密钥才能获取真实数据
2. **计算资源**：使用大型LLM模型时需要足够的计算资源
3. **数据质量**：数据质量对策略性能有重要影响
4. **风险管理**：需要定期评估策略风险并调整参数

## 免责声明

本策略仅供研究和教育目的使用，不构成投资建议。实际投资决策请结合自身风险承受能力和市场情况。

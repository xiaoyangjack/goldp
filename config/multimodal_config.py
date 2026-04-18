#!/usr/bin/env python3
"""
多模态语义Alpha策略配置文件
"""

# 策略配置
MULTIMODAL_STRATEGY_CONFIG = {
    # 策略基本参数
    'signal_threshold': 0.01,  # 信号阈值
    'target_vol': 0.01,  # 目标波动率
    'max_drawdown': 0.2,  # 最大回撤
    'asset_weight_limit': 0.4,  # 单个资产权重限制
    
    # LLM模型配置
    'llm_model_name': 'bert-base-uncased',  # LLM模型名称
    'max_seq_length': 512,  # 最大序列长度
    'batch_size': 32,  # 批处理大小
    
    # GBM模型配置
    'gbm_n_estimators': 100,  # 树的数量
    'gbm_learning_rate': 0.1,  # 学习率
    'gbm_max_depth': 5,  # 最大深度
    'gbm_random_state': 42,  # 随机种子
    
    # 数据处理配置
    'text_feature_dim': 100,  # 文本特征维度
    'audio_feature_dim': 10,  # 音频特征维度
    'social_feature_dim': 10,  # 社交媒体特征维度
    
    # 回测配置
    'initial_cash': 1000000,  # 初始资金
    'transaction_cost': 0.001,  # 交易成本
    'lookback_period': 10,  # 回溯期
    
    # 实时性配置
    'real_time_update_interval': 60,  # 实时更新间隔（秒）
    'data_fetch_batch_size': 100,  # 数据获取批量大小
    
    # API配置（需要根据实际情况填写）
    'openai_api_key': '',  # OpenAI API密钥
    'huggingface_token': '',  # Hugging Face token
    'news_api_key': '',  # 新闻API密钥
    'social_media_api_key': '',  # 社交媒体API密钥
}

# 多模态数据来源配置
DATA_SOURCES = {
    'news': {
        'enabled': True,
        'sources': ['bloomberg', 'reuters', 'wsj'],
        'update_frequency': 'hourly',
    },
    'reports': {
        'enabled': True,
        'sources': ['goldman', 'morgan_stanley', 'jpmorgan'],
        'update_frequency': 'daily',
    },
    'earnings_calls': {
        'enabled': True,
        'sources': ['seeking_alpha', 'earnings_call_transcripts'],
        'update_frequency': 'daily',
    },
    'social_media': {
        'enabled': True,
        'sources': ['twitter', 'reddit', 'stocktwits'],
        'update_frequency': '15min',
    },
    'management_speeches': {
        'enabled': True,
        'sources': ['company_website', 'conference_calls'],
        'update_frequency': 'weekly',
    },
}

# 资产配置
ASSETS = {
    'equity': {
        'us_stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
        'china_stocks': ['0700.HK', '9988.HK', '3690.HK', '1810.HK', '0939.HK'],
        'etfs': ['SPY', 'QQQ', 'IWM', 'TLT', 'GLD'],
    },
    'fixed_income': {
        'treasuries': ['TLT', 'IEF', 'SHY'],
        'corporate_bonds': ['LQD', 'VCSH', 'VCIT'],
    },
    'commodities': {
        'gold': ['GLD', 'IAU'],
        'oil': ['USO', 'XLE'],
        'agriculture': ['DBA', 'WEAT'],
    },
    'currencies': {
        'major': ['UUP', 'FXE', 'FXY', 'FXB'],
        'emerging': ['CEW', 'EMB'],
    },
}

# 策略类型适配
STRATEGY_TYPES = {
    'long_only': {
        'enabled': True,
        'constraints': {'short_allowed': False},
    },
    'long_short': {
        'enabled': True,
        'constraints': {'short_allowed': True, 'net_exposure': 0.5},
    },
    'market_neutral': {
        'enabled': True,
        'constraints': {'short_allowed': True, 'net_exposure': 0.1},
    },
    'sector_rotation': {
        'enabled': True,
        'constraints': {'sector_exposure_limit': 0.3},
    },
}

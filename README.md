# 黄金量化交易系统 - 使用说明

## Trae 优化版快速启动

### 一键启动（推荐）

```bash
# 克隆项目
git clone https://github.com/xiaoyangjack/goldp.git
cd goldp/GoldQuant

# 启动服务
./start_server.sh
# 或双击 GoldQuantWeb.app（macOS）
```

访问地址: <http://127.0.0.1:5555>

***

## 环境配置

### 1. 配置文件

复制环境配置模板：

```bash
cp .env.example .env
```

主要配置项（.env）：

```env
FLASK_PORT=5555          # 服务端口
DATA_REFRESH_INTERVAL=60 # 数据刷新间隔（秒）
LOG_LEVEL=INFO           # 日志级别
WEBHOOK_WECHAT=          # 企业微信webhook
WEBHOOK_FEISHU=           # 飞书webhook
```

### 2. 依赖安装

```bash
pip install -r requirements.txt
```

主要依赖：

- `flask` - Web框架
- `pandas` - 数据处理
- `akshare` - 金融数据
- `vectorbt` - 量化回测
- `apscheduler` - 定时任务
- `loguru` - 日志系统
- `plotly` - 数据可视化
- `requests` - HTTP请求

***

## 高级功能（Phase 3）

### 1. 实时模拟交易

- 模拟持仓线程：自动管理持仓状态
- 浮动盈亏计算：实时显示当前盈亏
- 信号状态跟踪：记录交易信号历史
- 每分钟更新：根据最新数据自动更新模拟账户

### 2. 交易告警系统

- 信号触发告警：BUY/SELL信号触发时推送
- 回撤阈值告警：账户回撤超过10%时推送
- 数据异常告警：数据获取失败时推送
- 多渠道推送：支持企业微信和飞书webhook

### 3. 可视化与前端升级

- VectorBT交互图表：集成Plotly图表库
- 移动端适配：Bootstrap 5响应式设计
- 策略参数面板：实时调整快慢线、止损比例
- 实时数据刷新：60秒自动更新所有数据

### 4. 部署与打包

- Docker部署：提供Dockerfile和docker-compose.yml
- macOS应用：GoldQuantWeb.app双击启动
- 一键启动脚本：start\_server.sh自动处理环境配置

***

## 功能模块

### 1. 实时行情

- 当前金价
- ATR指标（波动率）
- MA10/MA30移动平均线
- 趋势判断（多头/空头/横盘）

### 2. 交易信号

- BUY（买入信号）
- SELL（卖出信号）
- WATCH（观望）
- 策略状态指示（ACTIVE/PAUSE）

### 3. 数据管理

- 自动获取：从akshare API获取SGE实时数据
- 增量更新：仅获取新数据，避免重复
- 缓存机制：减少API调用
- 数据验证：完整性、一致性、合理性检查
- 手动刷新：支持60秒自动刷新

### 4. 回测报告

- 固定网格策略报告
- MA过滤策略报告
- MA过滤+风控策略报告
- 压力测试报告

### 5. 图表可视化

- 价格走势图（含MA10/MA30）
- 收益率曲线
- 回撤分析图
- 交易统计图表

### 6. 模拟持仓配置

- 持仓数量设置
- 持仓价格设置
- 持仓时间记录
- 实时盈亏计算

### 7. 策略参数调整

- 快速均线：5-50可调
- 慢速均线：10-60可调
- 止损比例：0-20%可调
- ATR阈值：10-50可调
- 信号阈值：0.1-2.0可调

***

## API接口

| 接口                     | 方法       | 说明     |
| ---------------------- | -------- | ------ |
| `/`                    | GET      | Web首页  |
| `/health`              | GET      | 健康检查   |
| `/api/market_data`     | GET      | 实时行情   |
| `/api/signal`          | GET      | 交易信号   |
| `/api/portfolio`       | GET/POST | 持仓管理   |
| `/api/fetch_data`      | POST     | 获取数据   |
| `/api/status`          | GET      | 系统状态   |
| `/api/reports`         | GET      | 报告列表   |
| `/api/report/{name}`   | GET      | 报告内容   |
| `/api/chart/*`         | GET      | 图表数据   |
| `/api/minute_data`     | GET      | 分时数据   |
| `/api/strategy_params` | GET/POST | 策略参数管理 |

***

## 目录结构

```
GoldQuant/
├── web_app.py              # Flask Web应用（含APScheduler）
├── data_fetcher.py         # 数据获取模块（缓存+增量）
├── requirements.txt         # 依赖包
├── .env                    # 环境配置
├── .env.example            # 配置模板
├── Dockerfile              # Docker构建文件
├── docker-compose.yml      # Docker-compose配置
├── start_server.sh        # 启动脚本
│
├── templates/
│   └── index.html         # 前端页面
│
├── static/
│   └── style.css          # 样式文件
│
├── backtest/              # 回测脚本
│   └── *.md               # 回测报告
│
├── strategies/            # 量化策略
│
├── utils/
│   └── risk_control.py    # 风控模块
│
├── data/                  # 数据文件
│
├── logs/                  # 日志文件
│
└── GoldQuantWeb.app/      # macOS应用
```

***

## 数据说明

- 数据来源：上海黄金交易所（SGE）Au99.99
- 数据范围：2019-01-01 至今
- 更新方式：自动增量更新
- 缓存策略：本地CSV缓存，60秒刷新
- 数据验证：三重验证（完整性、一致性、合理性）

***

## 日志查看

```bash
# 实时查看日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log

# 查看告警日志
grep 告警 logs/app.log
```

***

## Docker部署

### 1. 构建镜像

```bash
docker build -t goldquant:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name goldquant \
  -p 5555:5555 \
  -e FLASK_PORT=5555 \
  -e DATA_REFRESH_INTERVAL=60 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  goldquant:latest
```

### 3. 使用docker-compose

```bash
docker-compose up -d
```

***

## 移动端使用

- **响应式设计**：适配手机、平板、桌面端
- **触摸优化**：支持触摸操作和手势
- **快速访问**：优化移动端加载速度
- **功能完整**：移动端支持所有核心功能

***

## 策略参数调整

1. 在Web界面的"策略参数"面板中调整参数
2. 点击"保存参数"按钮
3. 系统会立即应用新的参数
4. 新参数会影响交易信号的生成

***

## 告警系统配置

1. 在`.env`文件中配置webhook地址：
   - `WEBHOOK_WECHAT`：企业微信webhook
   - `WEBHOOK_FEISHU`：飞书webhook
2. 告警触发条件：
   - 交易信号触发（BUY/SELL）
   - 账户回撤超过10%
   - 数据异常（获取失败）

***

## 性能优化

- **数据缓存**：本地CSV缓存，减少API调用
- **增量更新**：只获取新数据，提高效率
- **多线程**：模拟交易使用独立线程
- **异步处理**：数据获取和处理异步进行
- **资源管理**：自动清理过期数据和日志

***

## 安全注意事项

- **API密钥**：不要在代码中硬编码API密钥
- **Webhook地址**：不要在公开代码中暴露webhook地址
- **数据备份**：定期备份数据文件
- **日志管理**：定期清理日志文件
- **端口安全**：在生产环境中设置防火墙

***

## 常见问题

### 1. 端口被占用

```bash
# 修改 .env 中的端口
FLASK_PORT=5556
```

### 2. 数据获取失败

```bash
# 强制刷新数据
curl -X POST http://127.0.0.1:5555/api/fetch_data?force_refresh=true
```

### 3. 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 单独安装失败包
pip install flask
pip install pandas
```

### 4. Docker构建失败

```bash
# 检查网络连接
docker build --network=host -t goldquant:latest .
```

### 5. 告警不推送

```bash
# 检查webhook配置
cat .env | grep WEBHOOK

# 查看告警日志
grep 告警 logs/app.log
```

***

## 技术架构

### 核心模块

1. **数据层**：DataFetcher + 缓存机制
2. **策略层**：MA过滤策略 + 风控规则
3. **交易层**：模拟交易 + 告警系统
4. **展示层**：Flask + Plotly + Bootstrap 5

### 数据流

1. 数据获取 → 数据验证 → 数据存储
2. 数据读取 → 策略计算 → 信号生成
3. 信号触发 → 交易执行 → 告警推送
4. 数据处理 → 图表生成 → 前端展示

***

## 版本更新

### v2.0（Phase 3）

- ✅ 实时模拟交易
- ✅ 交易告警系统
- ✅ VectorBT交互图表
- ✅ 移动端适配
- ✅ 策略参数面板
- ✅ Docker部署
- ✅ macOS应用打包

### v1.0（Phase 1-2）

- ✅ 实时行情显示
- ✅ 交易信号生成
- ✅ 数据管理系统
- ✅ 回测报告查看
- ✅ 基础图表可视化
- ✅ 模拟持仓配置


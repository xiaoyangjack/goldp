# GoldQuant 前端项目

## 项目介绍
专业级量化投研与交易平台前端，基于 Vue3 + TypeScript + Element Plus + ECharts 构建。

## 技术栈
- Vue 3
- TypeScript
- Element Plus
- ECharts
- Vue Router
- Pinia

## 项目结构
```
frontend/
├── src/
│   ├── components/     # 组件
│   ├── views/          # 页面
│   ├── router/         # 路由
│   ├── store/          # 状态管理
│   ├── api/            # API接口
│   ├── utils/          # 工具函数
│   ├── assets/         # 静态资源
│   ├── styles/         # 样式
│   ├── main.ts         # 入口文件
│   └── App.vue         # 根组件
├── public/             # 公共资源
├── package.json        # 依赖配置
├── vite.config.ts      # Vite配置
├── tsconfig.json       # TypeScript配置
└── index.html          # HTML模板
```

## 如何运行
1. 安装依赖
```bash
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

3. 构建生产版本
```bash
npm run build
```

4. 预览生产构建
```bash
npm run preview
```

## 核心功能
- 首页：平台概览、新手引导、快速开始
- 数据中心：行情数据、基本面数据、资金流数据、行业数据、新闻舆情
- 因子研究：因子库、因子计算、因子预处理、因子有效性分析、因子筛选
- 策略开发：策略模板库、策略编辑器、参数配置、策略调试
- 回测引擎：回测任务管理、回测执行、回测报告、参数优化
- 模拟交易：模拟账户总览、交易下单、持仓管理、委托记录、成交明细
- 绩效分析：收益分析、风险分析、归因分析、持仓分析、交易行为分析
- 系统设置：账户设置、API配置、行情设置、交易规则设置

## 响应式设计
- 移动端：<768px，侧边栏折叠为抽屉式导航，单列布局
- 平板端：768px-1200px，侧边栏可折叠/展开，双列栅格布局
- 桌面端：1200px-1920px，侧边栏固定展开，12列栅格布局
- 大屏端：>1920px，内容区最大宽度约束，居中布局
import express from 'express'
import cors from 'cors'

const app = express()
const port = 3003

app.use(cors())
app.use(express.json())

// 模拟数据
const mockData = {
  // 账户信息
  account: {
    totalAsset: 1000000,
    availableCash: 850000,
    positionValue: 150000,
    totalPnl: 50000
  },
  // 最近回测
  backtests: [
    { name: '沪深300多因子', status: 'completed', return: 15.2 },
    { name: '中证500动量', status: 'completed', return: 8.7 },
    { name: '行业轮动', status: 'pending', return: 0 }
  ],
  // 市场概览
  market: [
    { name: '上证指数', value: 3200.00, change: 1.20 },
    { name: '深证成指', value: 12500.00, change: 0.80 },
    { name: '创业板指', value: 2500.00, change: -0.30 },
    { name: '沪深300', value: 4100.00, change: 1.00 }
  ],
  // 收益曲线数据
  equityCurve: {
    account: [2.1, 3.5, 5.2, 7.8, 10.5, 12.3, 14.7, 16.2, 18.9, 20.5, 22.3, 25.1],
    benchmark: [1.2, 2.5, 3.8, 5.1, 6.5, 7.8, 9.2, 10.5, 11.8, 13.2, 14.5, 15.8],
    months: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  }
}

// API接口
app.get('/api/account', (req, res) => {
  res.json({
    code: 200,
    data: mockData.account,
    message: 'success'
  })
})

app.get('/api/backtests', (req, res) => {
  res.json({
    code: 200,
    data: mockData.backtests,
    message: 'success'
  })
})

app.get('/api/market', (req, res) => {
  res.json({
    code: 200,
    data: mockData.market,
    message: 'success'
  })
})

app.get('/api/equity-curve', (req, res) => {
  res.json({
    code: 200,
    data: mockData.equityCurve,
    message: 'success'
  })
})

// 数据中心API
app.get('/api/data/market', (req, res) => {
  res.json({
    code: 200,
    data: [
      { date: '2024-01-01', open: 3000, high: 3050, low: 2980, close: 3020, volume: 100000000000, amount: 500000000000 },
      { date: '2024-01-02', open: 3020, high: 3080, low: 3000, close: 3060, volume: 120000000000, amount: 600000000000 },
      { date: '2024-01-03', open: 3060, high: 3100, low: 3040, close: 3080, volume: 150000000000, amount: 750000000000 }
    ],
    message: 'success'
  })
})

// 因子研究API
app.get('/api/factor/library', (req, res) => {
  res.json({
    code: 200,
    data: [
      { id: 1, name: 'PE', category: '估值', description: '市盈率', formula: '市值/净利润' },
      { id: 2, name: 'PB', category: '估值', description: '市净率', formula: '市值/净资产' },
      { id: 3, name: 'ROE', category: '盈利', description: '净资产收益率', formula: '净利润/净资产' },
      { id: 4, name: 'Momentum', category: '动量', description: '动量因子', formula: '过去12个月收益率' },
      { id: 5, name: 'Volatility', category: '波动率', description: '波动率因子', formula: '过去20日标准差' }
    ],
    message: 'success'
  })
})

// 策略开发API
app.get('/api/strategy/templates', (req, res) => {
  res.json({
    code: 200,
    data: [
      { id: 1, name: '沪深300多因子选股', description: '基于沪深300成分股的多因子选股策略', parameters: { factors: ['PE', 'PB', 'ROE'], weights: [0.3, 0.3, 0.4] } },
      { id: 2, name: '中证500动量反转', description: '基于中证500成分股的动量反转策略', parameters: { lookbackPeriod: 12, holdingPeriod: 3 } },
      { id: 3, name: '行业轮动', description: '基于行业表现的轮动策略', parameters: { lookbackPeriod: 6, topN: 3 } },
      { id: 4, name: '均线趋势', description: '基于均线交叉的趋势策略', parameters: { shortPeriod: 20, longPeriod: 60 } },
      { id: 5, name: '网格交易', description: '基于价格区间的网格交易策略', parameters: { basePrice: 3000, gridSize: 50, gridCount: 10 } }
    ],
    message: 'success'
  })
})

// 回测引擎API
app.post('/api/backtest/run', (req, res) => {
  const { strategyId, startDate, endDate, initialCapital, parameters } = req.body
  res.json({
    code: 200,
    data: {
      backtestId: 'bt-' + Date.now(),
      status: 'completed',
      metrics: {
        annualReturn: 15.2,
        totalReturn: 45.6,
        sharpeRatio: 1.8,
        maxDrawdown: 12.5,
        winRate: 65,
        profitFactor: 1.5,
        turnover: 0.8
      }
    },
    message: 'success'
  })
})

// 模拟交易API
app.get('/api/trading/account', (req, res) => {
  res.json({
    code: 200,
    data: {
      totalAsset: 1000000,
      availableCash: 850000,
      positionValue: 150000,
      totalPnl: 50000,
      todayPnl: 5000
    },
    message: 'success'
  })
})

app.get('/api/trading/positions', (req, res) => {
  res.json({
    code: 200,
    data: [
      { id: 1, symbol: '600000', name: '浦发银行', quantity: 10000, availableQuantity: 10000, costPrice: 8.5, currentPrice: 9.2, marketValue: 92000, unrealizedPnl: 7000 },
      { id: 2, symbol: '601318', name: '中国平安', quantity: 5000, availableQuantity: 5000, costPrice: 45.0, currentPrice: 48.5, marketValue: 242500, unrealizedPnl: 17500 }
    ],
    message: 'success'
  })
})

app.post('/api/trading/order', (req, res) => {
  const { symbol, direction, type, price, quantity } = req.body
  res.json({
    code: 200,
    data: {
      orderId: 'order-' + Date.now(),
      status: 'filled',
      filledPrice: price,
      filledQuantity: quantity,
      filledAt: new Date().toISOString()
    },
    message: 'success'
  })
})

// 绩效分析API
app.post('/api/performance/analyze', (req, res) => {
  const { startDate, endDate, accountId } = req.body
  res.json({
    code: 200,
    data: {
      returnAnalysis: {
        totalReturn: 45.6,
        annualReturn: 15.2,
        monthlyReturns: [2.1, 3.5, 5.2, 7.8, 10.5, 12.3, 14.7, 16.2, 18.9, 20.5, 22.3, 25.1],
        benchmarkReturn: 15.8
      },
      riskAnalysis: {
        maxDrawdown: 12.5,
        volatility: 18.2,
        sharpeRatio: 1.8,
        sortinoRatio: 2.1,
        calmarRatio: 1.2
      }
    },
    message: 'success'
  })
})

// 黄金相关API
app.get('/api/gold/prices', (req, res) => {
  res.json({
    code: 200,
    data: {
      currentPrice: 2023.50,
      openPrice: 2018.20,
      highPrice: 2025.80,
      lowPrice: 2015.30,
      change: 5.30,
      changePercent: 0.26
    },
    message: 'success'
  })
})

app.get('/api/gold/price-history', (req, res) => {
  const { period = '1m' } = req.query
  // 生成模拟数据
  const dates = []
  const prices = []
  const now = new Date()
  
  for (let i = 30; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
    prices.push(2000 + Math.random() * 50)
  }
  
  res.json({
    code: 200,
    data: {
      dates,
      prices
    },
    message: 'success'
  })
})

app.get('/api/gold/strategies', (req, res) => {
  res.json({
    code: 200,
    data: [
      { id: 1, name: '黄金趋势跟踪', description: '基于移动平均线的趋势跟踪策略', parameters: { shortPeriod: 20, longPeriod: 60 } },
      { id: 2, name: '黄金震荡区间', description: '基于布林带的震荡区间策略', parameters: { period: 20, stdDev: 2 } },
      { id: 3, name: '黄金动量突破', description: '基于动量指标的突破策略', parameters: { lookbackPeriod: 14, threshold: 0.02 } }
    ],
    message: 'success'
  })
})

app.post('/api/gold/backtest', (req, res) => {
  const { strategyId, startDate, endDate, initialCapital, parameters } = req.body
  res.json({
    code: 200,
    data: {
      backtestId: 'gold-bt-' + Date.now(),
      status: 'completed',
      metrics: {
        annualReturn: 12.5,
        totalReturn: 37.5,
        sharpeRatio: 1.5,
        maxDrawdown: 10.2,
        winRate: 62,
        profitFactor: 1.4,
        turnover: 0.6
      },
      equityCurve: {
        dates: ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11', '2023-12'],
        account: [100000, 102500, 105200, 108900, 112500, 116200, 119800, 123500, 127200, 130900, 134600, 137500],
        benchmark: [100000, 101200, 102500, 103800, 105100, 106400, 107700, 109000, 110300, 111600, 112900, 114200]
      }
    },
    message: 'success'
  })
})

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`)
})

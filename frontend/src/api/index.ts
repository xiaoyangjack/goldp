// API服务层

const API_BASE_URL = 'http://localhost:3003/api'

// 基础请求方法
async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data as T
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

// 账户相关API
export const accountApi = {
  getAccountInfo: () => request<{ code: number; data: any; message: string }>('/account')
}

// 回测相关API
export const backtestApi = {
  getRecentBacktests: () => request<{ code: number; data: any[]; message: string }>('/backtests')
}

// 市场相关API
export const marketApi = {
  getMarketOverview: () => request<{ code: number; data: any[]; message: string }>('/market')
}

// 收益曲线API
export const equityApi = {
  getEquityCurve: () => request<{ code: number; data: any; message: string }>('/equity-curve')
}

// 数据中心API
export const dataApi = {
  getMarketData: (symbol: string, startDate: string, endDate: string) => 
    request<{ code: number; data: any[]; message: string }>(`/data/market?symbol=${symbol}&startDate=${startDate}&endDate=${endDate}`)
}

// 因子研究API
export const factorApi = {
  getFactorLibrary: () => request<{ code: number; data: any[]; message: string }>('/factor/library')
}

// 策略开发API
export const strategyApi = {
  getStrategyTemplates: () => request<{ code: number; data: any[]; message: string }>('/strategy/templates')
}

// 回测引擎API
export const backtestEngineApi = {
  runBacktest: (data: any) => 
    request<{ code: number; data: any; message: string }>('/backtest/run', {
      method: 'POST',
      body: JSON.stringify(data)
    })
}

// 模拟交易API
export const tradingApi = {
  getTradingAccount: () => request<{ code: number; data: any; message: string }>('/trading/account'),
  getPositions: () => request<{ code: number; data: any[]; message: string }>('/trading/positions'),
  placeOrder: (data: any) => 
    request<{ code: number; data: any; message: string }>('/trading/order', {
      method: 'POST',
      body: JSON.stringify(data)
    })
}

// 绩效分析API
export const performanceApi = {
  analyzePerformance: (data: any) => 
    request<{ code: number; data: any; message: string }>('/performance/analyze', {
      method: 'POST',
      body: JSON.stringify(data)
    })
}

// 黄金相关API
export const goldApi = {
  getGoldPrices: () => request<{ code: number; data: any; message: string }>('/gold/prices'),
  getGoldPriceHistory: (period: string = '1m') => 
    request<{ code: number; data: any; message: string }>(`/gold/price-history?period=${period}`),
  getGoldStrategies: () => request<{ code: number; data: any[]; message: string }>('/gold/strategies'),
  runGoldBacktest: (data: any) => 
    request<{ code: number; data: any; message: string }>('/gold/backtest', {
      method: 'POST',
      body: JSON.stringify(data)
    })
}

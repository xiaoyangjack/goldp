// 情景配置文件
const scenarios = {
  // 情景A：战争升级
  scenarioA: {
    name: '战争升级',
    rFactorWeight: 0.5, // R因子权重50%
    targetPriceRange: {
      min: 5200,
      max: 5500
    },
    takeProfitLevels: [
      { price: 5200, percentage: 0.3 }, // 30%仓位在$5200止盈
      { price: 5350, percentage: 0.3 }, // 30%仓位在$5350止盈
      { price: 5500, percentage: 0.4 }  // 40%仓位在$5500止盈
    ],
    strategy: 'trend_following',
    emergencyRules: false
  },
  
  // 情景B：胶着震荡
  scenarioB: {
    name: '胶着震荡',
    rFactorWeight: 0.3, // 默认基准参数
    priceRange: {
      min: 4600,
      max: 5000
    },
    gridTrading: {
      enabled: true,
      gridCount: 10,
      profitTargetPerGrid: 0.01 // 每个网格1%利润
    },
    strategy: 'grid_trading',
    emergencyRules: false
  },
  
  // 情景C：全面停火
  scenarioC: {
    name: '全面停火',
    rFactorWeight: 0.2, // 默认基准参数
    emergencyRules: true,
    emergencySellPercentage: 0.7, // 紧急减仓70%
    bounceArbitrage: {
      enabled: true,
      buyThreshold: -0.05, // 超跌5%触发买入
      sellThreshold: 0.03   // 反弹3%触发卖出
    },
    strategy: 'bounce_arbitrage'
  }
};

module.exports = scenarios;
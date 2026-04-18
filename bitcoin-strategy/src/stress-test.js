// 压力测试模块
const scenarios = require('./config/scenarios');

class StressTest {
  constructor(initialBalance = 10000, initialPrice = 4800) {
    this.initialBalance = initialBalance;
    this.initialPrice = initialPrice;
  }

  // 模拟价格波动
  simulatePriceMovement(scenario, days = 30) {
    const pricePath = [];
    let currentPrice = this.initialPrice;
    
    for (let i = 0; i < days; i++) {
      let volatility;
      let trend;
      
      switch (scenario) {
        case 'scenarioA':
          // 战争升级：高波动，上升趋势
          volatility = 0.03; // 3%每日波动
          trend = 0.01; // 1%每日上升
          break;
        case 'scenarioB':
          // 胶着震荡：中等波动，无明显趋势
          volatility = 0.02; // 2%每日波动
          trend = 0; // 无趋势
          break;
        case 'scenarioC':
          // 全面停火：低波动，下降趋势
          volatility = 0.015; // 1.5%每日波动
          trend = -0.005; // 0.5%每日下降
          break;
        default:
          volatility = 0.02;
          trend = 0;
      }
      
      // 生成随机价格变动
      const randomChange = (Math.random() - 0.5) * 2 * volatility;
      currentPrice = currentPrice * (1 + trend + randomChange);
      pricePath.push(currentPrice);
    }
    
    return pricePath;
  }

  // 测试策略在特定情景下的表现
  testStrategy(scenarioKey, pricePath) {
    const scenario = scenarios[scenarioKey];
    let balance = this.initialBalance;
    let bitcoin = 0;
    let actions = [];
    
    // 初始买入
    if (balance > 0) {
      const initialBuyAmount = balance * 0.5 / pricePath[0];
      bitcoin += initialBuyAmount;
      balance -= initialBuyAmount * pricePath[0];
      actions.push({ day: 0, action: 'initial_buy', price: pricePath[0], amount: initialBuyAmount, balance });
    }
    
    pricePath.forEach((price, day) => {
      switch (scenario.strategy) {
        case 'trend_following':
          // 趋势跟踪策略
          if (price >= scenario.targetPriceRange.min) {
            // 止盈逻辑
            scenario.takeProfitLevels.forEach(level => {
              if (price >= level.price && bitcoin > 0) {
                const sellAmount = bitcoin * level.percentage;
                balance += sellAmount * price;
                bitcoin -= sellAmount;
                actions.push({ day, action: 'sell', price, amount: sellAmount, balance });
              }
            });
          }
          break;
        
        case 'grid_trading':
          // 网格交易策略
          if (scenario.gridTrading.enabled) {
            const gridSize = (scenario.priceRange.max - scenario.priceRange.min) / scenario.gridTrading.gridCount;
            const currentGrid = Math.floor((price - scenario.priceRange.min) / gridSize);
            
            // 简化的网格交易逻辑
            if (price <= scenario.priceRange.min && balance > 0) {
              // 买入
              const buyAmount = balance * 0.1 / price;
              bitcoin += buyAmount;
              balance -= buyAmount * price;
              actions.push({ day, action: 'buy', price, amount: buyAmount, balance });
            } else if (price >= scenario.priceRange.max && bitcoin > 0) {
              // 卖出
              const sellAmount = bitcoin * 0.1;
              balance += sellAmount * price;
              bitcoin -= sellAmount;
              actions.push({ day, action: 'sell', price, amount: sellAmount, balance });
            }
          }
          break;
        
        case 'bounce_arbitrage':
          // 超跌反弹套利策略
          if (scenario.emergencyRules && day === 0 && bitcoin > 0) {
            // 紧急减仓
            const sellAmount = bitcoin * scenario.emergencySellPercentage;
            balance += sellAmount * price;
            bitcoin -= sellAmount;
            actions.push({ day, action: 'emergency_sell', price, amount: sellAmount, balance });
          }
          
          // 超跌买入，反弹卖出
          if (day > 0) {
            const priceChange = (price - pricePath[day - 1]) / pricePath[day - 1];
            
            if (priceChange <= scenario.bounceArbitrage.buyThreshold && balance > 0) {
              // 超跌买入
              const buyAmount = balance * 0.2 / price;
              bitcoin += buyAmount;
              balance -= buyAmount * price;
              actions.push({ day, action: 'buy', price, amount: buyAmount, balance });
            } else if (priceChange >= scenario.bounceArbitrage.sellThreshold && bitcoin > 0) {
              // 反弹卖出
              const sellAmount = bitcoin * 0.2;
              balance += sellAmount * price;
              bitcoin -= sellAmount;
              actions.push({ day, action: 'sell', price, amount: sellAmount, balance });
            }
          }
          break;
      }
    });
    
    // 计算最终资产价值
    const finalAssetValue = balance + bitcoin * pricePath[pricePath.length - 1];
    const returnRate = (finalAssetValue - this.initialBalance) / this.initialBalance;
    
    return {
      scenario: scenario.name,
      initialBalance: this.initialBalance,
      finalAssetValue,
      returnRate,
      actionCount: actions.length,
      maxDrawdown: this.calculateMaxDrawdown(pricePath),
      actions
    };
  }

  // 计算最大回撤
  calculateMaxDrawdown(pricePath) {
    let maxPrice = pricePath[0];
    let maxDrawdown = 0;
    
    for (const price of pricePath) {
      if (price > maxPrice) {
        maxPrice = price;
      }
      const drawdown = (maxPrice - price) / maxPrice;
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown;
      }
    }
    
    return maxDrawdown;
  }

  // 运行所有情景的压力测试
  runAllScenarios() {
    const results = {};
    
    Object.keys(scenarios).forEach(scenarioKey => {
      const pricePath = this.simulatePriceMovement(scenarioKey);
      results[scenarioKey] = this.testStrategy(scenarioKey, pricePath);
    });
    
    return results;
  }
}

module.exports = StressTest;
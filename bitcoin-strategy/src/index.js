// 主索引文件
const ScenarioProbability = require('./scenario-probability');
const StressTest = require('./stress-test');
const scenarios = require('./config/scenarios');

class BitcoinStrategy {
  constructor() {
    this.scenarioProbability = new ScenarioProbability();
    this.stressTest = new StressTest();
  }

  // 运行策略
  async run() {
    console.log('=== Bitcoin 策略运行 ===\n');
    
    // 更新情景概率
    console.log('1. 更新情景概率...');
    const probabilities = await this.scenarioProbability.updateProbabilities();
    console.log('当前情景概率:', probabilities);
    
    // 运行压力测试
    console.log('\n2. 运行压力测试...');
    const testResults = this.stressTest.runAllScenarios();
    
    // 显示测试结果
    console.log('\n3. 压力测试结果:');
    Object.keys(testResults).forEach(key => {
      const result = testResults[key];
      console.log(`\n${result.scenario}:`);
      console.log(`  初始资金: $${result.initialBalance}`);
      console.log(`  最终资产: $${result.finalAssetValue.toFixed(2)}`);
      console.log(`  收益率: ${(result.returnRate * 100).toFixed(2)}%`);
      console.log(`  最大回撤: ${(result.maxDrawdown * 100).toFixed(2)}%`);
      console.log(`  交易次数: ${result.actionCount}`);
    });
    
    // 基于概率和测试结果计算综合表现
    console.log('\n4. 综合分析:');
    let weightedReturn = 0;
    let weightedDrawdown = 0;
    
    Object.keys(testResults).forEach(key => {
      const result = testResults[key];
      const probability = probabilities[key];
      weightedReturn += result.returnRate * probability;
      weightedDrawdown += result.maxDrawdown * probability;
    });
    
    console.log(`基于情景概率的加权收益率: ${(weightedReturn * 100).toFixed(2)}%`);
    console.log(`基于情景概率的加权最大回撤: ${(weightedDrawdown * 100).toFixed(2)}%`);
    
    console.log('\n=== 策略运行完成 ===');
  }
}

// 导出模块
module.exports = BitcoinStrategy;

// 如果直接运行此文件
if (require.main === module) {
  const strategy = new BitcoinStrategy();
  strategy.run().catch(console.error);
}
// 测试文件
const BitcoinStrategy = require('../src/index');
const ScenarioProbability = require('../src/scenario-probability');
const StressTest = require('../src/stress-test');

async function runTests() {
  console.log('=== 开始测试 ===\n');
  
  // 测试情景概率模块
  console.log('1. 测试情景概率模块...');
  const scenarioProbability = new ScenarioProbability();
  const probabilities = await scenarioProbability.updateProbabilities();
  console.log('情景概率更新成功:', probabilities);
  
  // 测试压力测试模块
  console.log('\n2. 测试压力测试模块...');
  const stressTest = new StressTest();
  const testResults = stressTest.runAllScenarios();
  console.log('压力测试完成，测试结果数量:', Object.keys(testResults).length);
  
  // 测试完整策略
  console.log('\n3. 测试完整策略...');
  const strategy = new BitcoinStrategy();
  await strategy.run();
  
  console.log('\n=== 测试完成 ===');
}

runTests().catch(console.error);
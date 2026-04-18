// 情景概率更新模块
const axios = require('axios');

class ScenarioProbability {
  constructor() {
    // 初始概率权重
    this.probabilities = {
      scenarioA: 0.33,
      scenarioB: 0.34,
      scenarioC: 0.33
    };
    this.lastUpdateDate = null;
  }

  // 检查是否需要更新概率
  shouldUpdate() {
    if (!this.lastUpdateDate) return true;
    
    const now = new Date();
    const daysSinceLastUpdate = (now - this.lastUpdateDate) / (1000 * 60 * 60 * 24);
    return daysSinceLastUpdate >= 7; // 每周更新一次
  }

  // 获取最新事件数据（模拟）
  async getLatestEvents() {
    // 这里可以替换为真实的API调用
    // 模拟事件数据
    return [
      { type: 'conflict', severity: 'high', impact: 0.8 },
      { type: 'diplomacy', severity: 'medium', impact: 0.5 },
      { type: 'economic', severity: 'low', impact: 0.3 }
    ];
  }

  // 更新情景概率
  async updateProbabilities() {
    if (!this.shouldUpdate()) {
      console.log('概率更新未到时间');
      return this.probabilities;
    }

    try {
      const events = await this.getLatestEvents();
      
      // 基于事件计算新的概率
      let scenarioAScore = 0;
      let scenarioBScore = 0;
      let scenarioCScore = 0;

      events.forEach(event => {
        if (event.type === 'conflict') {
          scenarioAScore += event.impact * 0.8;
          scenarioBScore += event.impact * 0.2;
        } else if (event.type === 'diplomacy') {
          scenarioBScore += event.impact * 0.6;
          scenarioCScore += event.impact * 0.4;
        } else if (event.type === 'economic') {
          scenarioBScore += event.impact * 0.5;
          scenarioCScore += event.impact * 0.5;
        }
      });

      // 归一化概率
      const totalScore = scenarioAScore + scenarioBScore + scenarioCScore;
      
      this.probabilities = {
        scenarioA: totalScore > 0 ? scenarioAScore / totalScore : 0.33,
        scenarioB: totalScore > 0 ? scenarioBScore / totalScore : 0.34,
        scenarioC: totalScore > 0 ? scenarioCScore / totalScore : 0.33
      };

      this.lastUpdateDate = new Date();
      console.log('情景概率已更新:', this.probabilities);
      
      return this.probabilities;
    } catch (error) {
      console.error('更新概率时出错:', error);
      return this.probabilities;
    }
  }

  // 获取当前概率
  getCurrentProbabilities() {
    return this.probabilities;
  }
}

module.exports = ScenarioProbability;
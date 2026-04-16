<template>
  <div class="gold-strategy-container">
    <el-card class="strategy-card">
      <template #header>
        <div class="card-header">
          <span>黄金策略分析</span>
          <el-button type="primary" size="small" @click="refreshStrategies">
            <el-icon><Refresh /></el-icon>
            刷新策略
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="strategy-list-card" shadow="hover">
            <template #header>
              <span>黄金策略库</span>
            </template>
            <el-table :data="strategies" stripe style="width: 100%">
              <el-table-column prop="name" label="策略名称" />
              <el-table-column prop="type" label="策略类型">
                <template #default="scope">
                  <el-tag :type="getStrategyTypeTag(scope.row.type)">
                    {{ scope.row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="return" label="历史收益">
                <template #default="scope">
                  <span :class="scope.row.return >= 0 ? 'positive' : 'negative'">
                    {{ scope.row.return >= 0 ? '+' : '' }}{{ scope.row.return }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="sharpe" label="夏普比率" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="selectStrategy(scope.row)">
                    选择
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="strategy-detail-card" shadow="hover">
            <template #header>
              <span>策略详情</span>
            </template>
            <div v-if="selectedStrategy" class="strategy-detail">
              <h3>{{ selectedStrategy.name }}</h3>
              <el-divider />
              <div class="detail-item">
                <span class="label">策略类型:</span>
                <span class="value">{{ selectedStrategy.type }}</span>
              </div>
              <div class="detail-item">
                <span class="label">策略描述:</span>
                <span class="value">{{ selectedStrategy.description }}</span>
              </div>
              <div class="detail-item">
                <span class="label">参数配置:</span>
                <el-table :data="selectedStrategy.parameters" stripe style="width: 100%; margin-top: 10px;">
                  <el-table-column prop="name" label="参数名" />
                  <el-table-column prop="value" label="值" />
                  <el-table-column prop="description" label="描述" />
                </el-table>
              </div>
              <el-button type="success" style="margin-top: 20px;" @click="runBacktest">
                运行回测
              </el-button>
            </div>
            <div v-else class="no-selection">
              <el-empty description="请从左侧选择一个策略" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="backtest-result-card" style="margin-top: 20px;" v-if="backtestResult">
        <template #header>
          <span>回测结果</span>
        </template>
        <div class="backtest-result">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-label">年化收益</div>
                <div class="metric-value">{{ backtestResult.annualReturn }}%</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-label">总收益</div>
                <div class="metric-value">{{ backtestResult.totalReturn }}%</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-label">夏普比率</div>
                <div class="metric-value">{{ backtestResult.sharpeRatio }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-label">最大回撤</div>
                <div class="metric-value">{{ backtestResult.maxDrawdown }}%</div>
              </div>
            </el-col>
          </el-row>
          <div class="chart-container" style="margin-top: 20px;">
            <div ref="equityChartRef" class="chart" style="height: 300px;"></div>
          </div>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { goldApi } from '../../api'
import { ElMessage } from 'element-plus'

// 响应式数据
const equityChartRef = ref<HTMLElement>()
const equityChart = ref<echarts.ECharts>()
const strategies = ref<any[]>([])
const selectedStrategy = ref<any>(null)
const backtestResult = ref<any>(null)

// 策略类型标签
const getStrategyTypeTag = (type: string) => {
  const tagMap: Record<string, string> = {
    '趋势跟踪': 'primary',
    '均值回归': 'success',
    '网格交易': 'warning',
    '套利策略': 'info',
    '高频交易': 'danger'
  }
  return tagMap[type] || 'info'
}

// 刷新策略列表
const refreshStrategies = async () => {
  try {
    const response = await goldApi.getGoldStrategies()
    if (response.code === 200) {
      strategies.value = response.data
    }
  } catch (error) {
    console.error('Failed to get strategies:', error)
    ElMessage.error('获取策略列表失败')
  }
}

// 选择策略
const selectStrategy = (strategy: any) => {
  selectedStrategy.value = strategy
  backtestResult.value = null
}

// 运行回测
const runBacktest = async () => {
  if (!selectedStrategy.value) {
    ElMessage.warning('请先选择一个策略')
    return
  }
  
  try {
    const response = await goldApi.runGoldBacktest({
      strategyId: selectedStrategy.value.id,
      startDate: '2023-01-01',
      endDate: '2023-12-31',
      initialCapital: 100000,
      parameters: selectedStrategy.value.parameters
    })
    if (response.code === 200) {
      backtestResult.value = response.data.metrics
      initEquityChart(response.data.equityCurve)
    }
  } catch (error) {
    console.error('Failed to run backtest:', error)
    ElMessage.error('运行回测失败')
  }
}

// 初始化收益曲线图表
const initEquityChart = (data?: any) => {
  if (equityChartRef.value) {
    equityChart.value = echarts.init(equityChartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: function(params: any) {
          return `${params[0].name}<br/>策略收益: ${params[0].value.toFixed(2)}%<br/>基准收益: ${params[1].value.toFixed(2)}%`
        }
      },
      legend: {
        data: ['策略收益', '基准收益']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: data?.dates || []
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '策略收益',
          type: 'line',
          data: data?.account.map((value: number, index: number) => ((value / 100000) - 1) * 100) || [],
          smooth: true,
          lineStyle: {
            color: '#165DFF'
          }
        },
        {
          name: '基准收益',
          type: 'line',
          data: data?.benchmark.map((value: number, index: number) => ((value / 100000) - 1) * 100) || [],
          smooth: true,
          lineStyle: {
            color: '#67C23A'
          }
        }
      ]
    }
    equityChart.value.setOption(option)
  }
}

// 处理窗口resize
const handleResize = () => {
  equityChart.value?.resize()
}

// 初始化
onMounted(async () => {
  await refreshStrategies()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.gold-strategy-container {
  padding: 20px;
}

.strategy-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-list-card,
.strategy-detail-card {
  height: 100%;
}

.strategy-detail {
  padding: 20px 0;
}

.strategy-detail h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.detail-item {
  margin-bottom: 15px;
}

.label {
  color: #606266;
  margin-right: 10px;
}

.value {
  font-weight: bold;
}

.no-selection {
  padding: 40px 0;
  text-align: center;
}

.backtest-result-card {
  margin-top: 20px;
}

.metric-card {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.metric-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.chart-container {
  margin-top: 20px;
}

.chart {
  width: 100%;
  height: 300px;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

@media (max-width: 768px) {
  .gold-strategy-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .chart {
    height: 250px;
  }
}
</style>

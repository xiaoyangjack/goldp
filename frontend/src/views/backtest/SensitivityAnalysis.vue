<template>
  <div class="sensitivity-analysis-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>敏感性分析配置</span>
          <el-button type="primary" @click="startAnalysis" :disabled="analyzing">
            <el-icon><VideoPlay /></el-icon>
            {{ analyzing ? '分析中...' : '开始分析' }}
          </el-button>
        </div>
      </template>
      <el-form :model="analysisForm" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="基准策略">
              <el-select v-model="analysisForm.strategy" style="width: 100%;">
                <el-option label="双均线策略" value="dual-ma" />
                <el-option label="MACD策略" value="macd" />
                <el-option label="RSI策略" value="rsi" />
                <el-option label="布林带策略" value="bollinger" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="目标指标">
              <el-select v-model="analysisForm.targetMetric" style="width: 100%;">
                <el-option label="夏普比率" value="sharpe" />
                <el-option label="年化收益率" value="return" />
                <el-option label="最大回撤" value="maxDrawdown" />
                <el-option label="卡尔马比率" value="calmar" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="变动范围%">
              <el-input-number v-model="analysisForm.variationRange" :min="5" :max="100" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-divider content-position="left">参数选择</el-divider>
      <el-table :data="parameters" border style="width: 100%;">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="参数名称" />
        <el-table-column prop="baseValue" label="基准值" />
        <el-table-column prop="minValue" label="最小值" />
        <el-table-column prop="maxValue" label="最大值" />
      </el-table>
    </el-card>

    <el-card class="progress-card" style="margin-top: 20px;" v-if="analyzing">
      <template #header>
        <span>分析进度</span>
      </template>
      <el-progress :percentage="analysisProgress" />
      <div class="progress-info">
        <span>当前参数: {{ currentParameter }}</span>
        <span>剩余时间: {{ remainingTime }}秒</span>
      </div>
    </el-card>

    <el-card class="results-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>敏感性分析结果</span>
          <el-button type="primary" size="small" @click="exportResults" :disabled="sensitivityResults.length === 0">
            <el-icon><Download /></el-icon>
            导出结果
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="敏感性排序" name="ranking">
          <div ref="sensitivityChartRef" class="chart-container"></div>
        </el-tab-pane>
        
        <el-tab-pane label="参数曲线" name="curves">
          <div ref="curvesChartRef" class="chart-container"></div>
        </el-tab-pane>
        
        <el-tab-pane label="详细结果" name="table">
          <el-table :data="sensitivityResults" stripe style="width: 100%">
            <el-table-column prop="rank" label="排名" width="80" />
            <el-table-column prop="parameter" label="参数名称" width="150" />
            <el-table-column prop="sensitivity" label="敏感性系数" width="150" sortable>
              <template #default="{ row }">
                <el-tag :type="getSensitivityType(row.sensitivity)">
                  {{ row.sensitivity.toFixed(4) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="impact" label="影响程度" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.impact" :status="getImpactStatus(row.impact)" />
              </template>
            </el-table-column>
            <el-table-column prop="direction" label="影响方向" width="100">
              <template #default="{ row }">
                <el-tag :type="row.direction === 'positive' ? 'success' : 'danger'">
                  {{ row.direction === 'positive' ? '正向' : '负向' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card class="summary-card" style="margin-top: 20px;">
      <template #header>
        <span>分析总结</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="最敏感参数">
            <template #suffix>
              <el-tag type="danger">{{ mostSensitiveParam }}</el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="敏感性系数">
            <template #suffix>{{ maxSensitivity.toFixed(4) }}</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="高敏感参数数量">
            <template #suffix>
              <el-tag type="warning">{{ highSensitiveCount }}</el-tag>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="分析参数总数">
            <template #suffix>{{ totalParams }}</template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { VideoPlay, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('ranking')
const analyzing = ref(false)
const analysisProgress = ref(0)
const currentParameter = ref('')
const remainingTime = ref(0)

const sensitivityChartRef = ref<HTMLElement>()
const curvesChartRef = ref<HTMLElement>()
let sensitivityChart: echarts.ECharts | null = null
let curvesChart: echarts.ECharts | null = null

const analysisForm = ref({
  strategy: 'dual-ma',
  targetMetric: 'sharpe',
  variationRange: 30
})

const parameters = ref([
  { name: '短期均线周期', baseValue: 5, minValue: 3, maxValue: 30 },
  { name: '长期均线周期', baseValue: 20, minValue: 10, maxValue: 100 },
  { name: '止损阈值%', baseValue: 5, minValue: 1, maxValue: 20 },
  { name: '止盈阈值%', baseValue: 10, minValue: 5, maxValue: 50 },
  { name: '仓位比例%', baseValue: 80, minValue: 10, maxValue: 100 }
])

const sensitivityResults = ref([
  { rank: 1, parameter: '长期均线周期', sensitivity: 0.8235, impact: 95, direction: 'positive', description: '对策略收益影响最大' },
  { rank: 2, parameter: '短期均线周期', sensitivity: 0.6124, impact: 78, direction: 'positive', description: '影响交易频率' },
  { rank: 3, parameter: '止损阈值%', sensitivity: 0.4589, impact: 62, direction: 'negative', description: '影响最大回撤' },
  { rank: 4, parameter: '仓位比例%', sensitivity: 0.3215, impact: 48, direction: 'positive', description: '影响资金利用率' },
  { rank: 5, parameter: '止盈阈值%', sensitivity: 0.1892, impact: 28, direction: 'positive', description: '影响单笔收益' }
])

const mostSensitiveParam = computed(() => sensitivityResults.value[0]?.parameter || '-')
const maxSensitivity = computed(() => sensitivityResults.value[0]?.sensitivity || 0)
const highSensitiveCount = computed(() => sensitivityResults.value.filter(r => r.impact >= 70).length)
const totalParams = computed(() => sensitivityResults.value.length)

const getSensitivityType = (value: number) => {
  if (value >= 0.6) return 'danger'
  if (value >= 0.3) return 'warning'
  return 'success'
}

const getImpactStatus = (value: number) => {
  if (value >= 70) return 'exception'
  if (value >= 40) return 'warning'
  return ''
}

const startAnalysis = () => {
  analyzing.value = true
  analysisProgress.value = 0
  currentParameter.value = parameters.value[0].name
  remainingTime.value = 30
  
  const interval = setInterval(() => {
    if (analysisProgress.value >= 100) {
      clearInterval(interval)
      analyzing.value = false
      ElMessage.success('敏感性分析完成')
      return
    }
    
    analysisProgress.value += Math.floor(Math.random() * 5)
    const paramIndex = Math.floor((analysisProgress.value / 100) * parameters.value.length)
    currentParameter.value = parameters.value[Math.min(paramIndex, parameters.value.length - 1)].name
    remainingTime.value = Math.max(0, 30 - Math.floor(analysisProgress.value / 3.33))
  }, 200)
}

const exportResults = () => {
  ElMessage.success('结果导出成功')
}

const initSensitivityChart = () => {
  if (!sensitivityChartRef.value) return
  sensitivityChart = echarts.init(sensitivityChartRef.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '敏感性系数'
    },
    yAxis: {
      type: 'category',
      data: sensitivityResults.value.map(r => r.parameter).reverse()
    },
    visualMap: {
      show: false,
      min: 0,
      max: 1,
      inRange: {
        color: ['#67C23A', '#E6A23C', '#F56C6C']
      }
    },
    series: [{
      name: '敏感性系数',
      type: 'bar',
      data: sensitivityResults.value.map(r => r.sensitivity).reverse(),
      label: {
        show: true,
        position: 'right',
        formatter: '{c:.4f}'
      },
      itemStyle: {
        borderRadius: [0, 4, 4, 0]
      }
    }]
  }

  sensitivityChart.setOption(option)
}

const initCurvesChart = () => {
  if (!curvesChartRef.value) return
  curvesChart = echarts.init(curvesChartRef.value)
  
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  const series = sensitivityResults.value.map((param, index) => {
    const data = []
    const baseValue = parameters.value.find(p => p.name === param.parameter)?.baseValue || 10
    for (let i = -50; i <= 50; i += 10) {
      const variation = i / 100
      const value = 1 + param.sensitivity * variation + (Math.random() - 0.5) * 0.1
      data.push([i, parseFloat(value.toFixed(3))])
    }
    return {
      name: param.parameter,
      type: 'line',
      data: data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2,
        color: colors[index % colors.length]
      },
      itemStyle: {
        color: colors[index % colors.length]
      }
    }
  })

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: sensitivityResults.value.map(r => r.parameter),
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '参数变动 (%)'
    },
    yAxis: {
      type: 'value',
      name: '相对绩效'
    },
    series: series
  }

  curvesChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initSensitivityChart()
    initCurvesChart()
  })
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    sensitivityChart?.resize()
    curvesChart?.resize()
  })
})
</script>

<style scoped>
.sensitivity-analysis-container {
  padding: 20px;
}

.config-card,
.progress-card,
.results-card,
.summary-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: #606266;
}

.chart-container {
  height: 400px;
  width: 100%;
}

@media (max-width: 768px) {
  .sensitivity-analysis-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>

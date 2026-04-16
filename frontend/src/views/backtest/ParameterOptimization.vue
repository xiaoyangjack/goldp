<template>
  <div class="parameter-optimization-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>参数优化配置</span>
          <el-button type="primary" @click="startOptimization" :disabled="optimizing">
            <el-icon><VideoPlay /></el-icon>
            {{ optimizing ? '优化中...' : '开始优化' }}
          </el-button>
        </div>
      </template>
      <el-form :model="optimizationForm" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="优化目标">
              <el-select v-model="optimizationForm.objective" style="width: 100%;">
                <el-option label="夏普比率" value="sharpe" />
                <el-option label="年化收益率" value="return" />
                <el-option label="卡尔马比率" value="calmar" />
                <el-option label="索提诺比率" value="sortino" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优化算法">
              <el-select v-model="optimizationForm.algorithm" style="width: 100%;">
                <el-option label="网格搜索" value="grid" />
                <el-option label="遗传算法" value="genetic" />
                <el-option label="贝叶斯优化" value="bayesian" />
                <el-option label="随机搜索" value="random" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最大迭代次数">
              <el-input-number v-model="optimizationForm.maxIterations" :min="10" :max="1000" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-divider content-position="left">参数范围配置</el-divider>
      <el-table :data="parameterRanges" border style="width: 100%;">
        <el-table-column prop="name" label="参数名称" width="150" />
        <el-table-column label="最小值">
          <template #default="scope">
            <el-input-number v-model="scope.row.min" :min="0" :max="1000" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="最大值">
          <template #default="scope">
            <el-input-number v-model="scope.row.max" :min="0" :max="1000" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="步长">
          <template #default="scope">
            <el-input-number v-model="scope.row.step" :min="1" :max="100" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="danger" size="small" link @click="removeParameter(scope.$index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button type="primary" size="small" style="margin-top: 15px;" @click="addParameter">
        <el-icon><Plus /></el-icon>
        添加参数
      </el-button>
    </el-card>

    <el-card class="progress-card" style="margin-top: 20px;" v-if="optimizing">
      <template #header>
        <span>优化进度</span>
      </template>
      <el-progress :percentage="optimizationProgress" :status="optimizationStatus" />
      <div class="progress-info">
        <span>当前迭代: {{ currentIteration }} / {{ optimizationForm.maxIterations }}</span>
        <span>当前最佳: {{ currentBestObjective?.toFixed(3) }}</span>
      </div>
    </el-card>

    <el-card class="results-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>优化结果</span>
          <el-button type="primary" size="small" @click="exportResults" :disabled="optimizationResults.length === 0">
            <el-icon><Download /></el-icon>
            导出结果
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="最佳参数" name="best">
          <el-descriptions :column="2" border v-if="bestParams">
            <el-descriptions-item v-for="(value, key) in bestParams" :key="key" :label="key">
              {{ value }}
            </el-descriptions-item>
          </el-descriptions>
          <el-empty v-else description="运行优化后查看结果" />
        </el-tab-pane>
        
        <el-tab-pane label="参数热力图" name="heatmap">
          <div ref="heatmapChartRef" class="chart-container"></div>
        </el-tab-pane>
        
        <el-tab-pane label="优化历史" name="history">
          <div ref="historyChartRef" class="chart-container"></div>
        </el-tab-pane>
        
        <el-tab-pane label="详细结果" name="table">
          <el-table :data="optimizationResults" stripe style="width: 100%">
            <el-table-column prop="iteration" label="迭代" width="80" sortable />
            <el-table-column prop="sharpe" label="夏普比率" width="120" sortable>
              <template #default="{ row }">
                <span :style="{ color: row.sharpe >= 1 ? '#67C23A' : '#F56C6C' }">
                  {{ row.sharpe?.toFixed(3) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="return" label="收益率%" width="100" sortable>
              <template #default="{ row }">
                <span :style="{ color: row.return >= 0 ? '#67C23A' : '#F56C6C' }">
                  {{ row.return?.toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="maxDrawdown" label="最大回撤%" width="120" sortable />
            <el-table-column prop="params" label="参数">
              <template #default="{ row }">
                <el-tag v-for="(value, key) in row.params" :key="key" size="small" style="margin-right: 5px;">
                  {{ key }}: {{ value }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { VideoPlay, Plus, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('best')
const optimizing = ref(false)
const optimizationProgress = ref(0)
const optimizationStatus = ref('')
const currentIteration = ref(0)
const currentBestObjective = ref(0)

const heatmapChartRef = ref<HTMLElement>()
const historyChartRef = ref<HTMLElement>()
let heatmapChart: echarts.ECharts | null = null
let historyChart: echarts.ECharts | null = null

const optimizationForm = ref({
  objective: 'sharpe',
  algorithm: 'grid',
  maxIterations: 100
})

const parameterRanges = ref([
  { name: '短期均线周期', min: 3, max: 30, step: 1 },
  { name: '长期均线周期', min: 20, max: 100, step: 5 }
])

const optimizationResults = ref([
  { iteration: 1, sharpe: 1.25, return: 18.5, maxDrawdown: -12.3, params: { '短期均线': 5, '长期均线': 20 } },
  { iteration: 2, sharpe: 1.32, return: 20.1, maxDrawdown: -11.8, params: { '短期均线': 6, '长期均线': 25 } },
  { iteration: 3, sharpe: 1.18, return: 16.8, maxDrawdown: -13.2, params: { '短期均线': 4, '长期均线': 30 } },
  { iteration: 4, sharpe: 1.45, return: 22.3, maxDrawdown: -10.5, params: { '短期均线': 7, '长期均线': 22 } },
  { iteration: 5, sharpe: 1.38, return: 21.0, maxDrawdown: -11.2, params: { '短期均线': 8, '长期均线': 28 } }
])

const bestParams = ref({
  '短期均线周期': 7,
  '长期均线周期': 22,
  '夏普比率': 1.45,
  '年化收益率': '22.3%',
  '最大回撤': '-10.5%'
})

const addParameter = () => {
  parameterRanges.value.push({ name: '新参数', min: 0, max: 100, step: 1 })
}

const removeParameter = (index: number) => {
  parameterRanges.value.splice(index, 1)
}

const startOptimization = () => {
  optimizing.value = true
  optimizationProgress.value = 0
  currentIteration.value = 0
  currentBestObjective.value = 0
  
  const interval = setInterval(() => {
    if (currentIteration.value >= optimizationForm.value.maxIterations) {
      clearInterval(interval)
      optimizing.value = false
      optimizationStatus.value = 'success'
      ElMessage.success('优化完成')
      return
    }
    
    currentIteration.value++
    optimizationProgress.value = Math.round((currentIteration.value / optimizationForm.value.maxIterations) * 100)
    
    const newSharpe = 1 + Math.random() * 1
    if (newSharpe > currentBestObjective.value) {
      currentBestObjective.value = newSharpe
    }
    
    if (currentIteration.value % 20 === 0) {
      optimizationResults.value.unshift({
        iteration: currentIteration.value,
        sharpe: newSharpe,
        return: 15 + Math.random() * 15,
        maxDrawdown: -15 + Math.random() * 5,
        params: {
          '短期均线': Math.floor(3 + Math.random() * 27),
          '长期均线': Math.floor(20 + Math.random() * 80)
        }
      })
    }
  }, 100)
}

const exportResults = () => {
  ElMessage.success('结果导出成功')
}

const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  heatmapChart = echarts.init(heatmapChartRef.value)
  
  const data: number[][] = []
  const shortMa = []
  const longMa = []
  
  for (let i = 3; i <= 30; i++) {
    shortMa.push(i)
  }
  for (let i = 20; i <= 100; i += 5) {
    longMa.push(i)
  }
  
  for (let i = 0; i < shortMa.length; i++) {
    for (let j = 0; j < longMa.length; j++) {
      const value = 0.8 + Math.random() * 1.2
      data.push([i, j, parseFloat(value.toFixed(2))])
    }
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => `短期均线: ${shortMa[params.data[0]]}<br/>长期均线: ${longMa[params.data[1]]}<br/>夏普比率: ${params.data[2]}`
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: shortMa,
      splitArea: { show: true },
      name: '短期均线'
    },
    yAxis: {
      type: 'category',
      data: longMa,
      splitArea: { show: true },
      name: '长期均线'
    },
    visualMap: {
      min: 0.5,
      max: 2,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A']
      }
    },
    series: [{
      name: '夏普比率',
      type: 'heatmap',
      data: data,
      label: { show: false },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  heatmapChart.setOption(option)
}

const initHistoryChart = () => {
  if (!historyChartRef.value) return
  historyChart = echarts.init(historyChartRef.value)
  
  const iterations = []
  const bestValues = []
  const currentValues = []
  let best = 0
  
  for (let i = 1; i <= 50; i++) {
    iterations.push(i)
    const current = 0.8 + Math.random() * 1.2
    currentValues.push(parseFloat(current.toFixed(3)))
    if (current > best) best = current
    bestValues.push(parseFloat(best.toFixed(3)))
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['当前值', '最佳值']
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
      data: iterations,
      name: '迭代次数'
    },
    yAxis: {
      type: 'value',
      name: '目标函数值'
    },
    series: [
      {
        name: '当前值',
        type: 'line',
        data: currentValues,
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: '最佳值',
        type: 'line',
        data: bestValues,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          width: 3
        }
      }
    ]
  }

  historyChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initHeatmapChart()
    initHistoryChart()
  })
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    heatmapChart?.resize()
    historyChart?.resize()
  })
})
</script>

<style scoped>
.parameter-optimization-container {
  padding: 20px;
}

.config-card,
.progress-card,
.results-card {
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
  .parameter-optimization-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>

<template>
  <div class="factor-visualization-container">
    <el-card class="control-card">
      <template #header>
        <div class="card-header">
          <span>可视化配置</span>
          <el-button type="primary" size="small" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <el-form :inline="true" :model="visualForm" class="visual-form">
        <el-form-item label="选择因子">
          <el-select v-model="visualForm.factors" multiple placeholder="请选择因子" style="width: 400px;">
            <el-option v-for="factor in factorList" :key="factor.id" :label="factor.name" :value="factor.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="visualForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>因子IC时序图</span>
          </template>
          <div ref="icChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>因子收益率分布</span>
          </template>
          <div ref="distributionChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span>因子相关性热力图</span>
          </template>
          <div ref="heatmapChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>因子累积收益率</span>
          </template>
          <div ref="cumReturnChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>因子分位数表现</span>
          </template>
          <div ref="quantileChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const icChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()
const heatmapChartRef = ref<HTMLElement>()
const cumReturnChartRef = ref<HTMLElement>()
const quantileChartRef = ref<HTMLElement>()

let icChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null
let cumReturnChart: echarts.ECharts | null = null
let quantileChart: echarts.ECharts | null = null

const factorList = [
  { id: 'F001', name: '动量因子' },
  { id: 'F002', name: '反转因子' },
  { id: 'F003', name: '波动率因子' },
  { id: 'F004', name: '市盈率因子' },
  { id: 'F005', name: '市净率因子' },
  { id: 'F006', name: 'ROE因子' }
]

const visualForm = ref({
  factors: ['F001', 'F004', 'F006'],
  dateRange: []
})

const generateDates = (count: number) => {
  const dates = []
  const today = new Date()
  for (let i = count - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(date.toISOString().split('T')[0])
  }
  return dates
}

const dates = generateDates(60)

const generateICData = () => {
  const data: Record<string, number[]> = {}
  factorList.forEach(factor => {
    data[factor.id] = []
    let value = 0.05
    for (let i = 0; i < 60; i++) {
      value += (Math.random() - 0.5) * 0.03
      value = Math.max(-0.3, Math.min(0.3, value))
      data[factor.id].push(value)
    }
  })
  return data
}

const icData = generateICData()

const initICChart = () => {
  if (!icChartRef.value) return
  icChart = echarts.init(icChartRef.value)
  
  const series = visualForm.value.factors.map(factorId => {
    const factor = factorList.find(f => f.id === factorId)
    return {
      name: factor?.name,
      type: 'line',
      data: icData[factorId],
      smooth: true
    }
  })

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: visualForm.value.factors.map(id => factorList.find(f => f.id === id)?.name)
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
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series
  }

  icChart.setOption(option)
}

const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  distributionChart = echarts.init(distributionChartRef.value)
  
  const bins = [-0.3, -0.25, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
  const histogramData = [5, 8, 12, 18, 25, 35, 40, 35, 25, 18, 12, 8, 5]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: bins.map(b => b.toFixed(2))
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '频数',
      type: 'bar',
      data: histogramData,
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }

  distributionChart.setOption(option)
}

const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  heatmapChart = echarts.init(heatmapChartRef.value)
  
  const factorNames = visualForm.value.factors.map(id => factorList.find(f => f.id === id)?.name || '')
  const data: number[][] = []
  
  for (let i = 0; i < factorNames.length; i++) {
    for (let j = 0; j < factorNames.length; j++) {
      let value: number
      if (i === j) {
        value = 1
      } else {
        value = 0.3 + Math.random() * 0.4
        if ((i + j) % 3 === 0) value = -value
      }
      data.push([i, j, parseFloat(value.toFixed(2))])
    }
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        return `${factorNames[params.data[0]]} vs ${factorNames[params.data[1]]}<br/>相关系数: ${params.data[2]}`
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      data: factorNames,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: factorNames,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#F56C6C', '#FFFFFF', '#67C23A']
      }
    },
    series: [{
      name: '相关性',
      type: 'heatmap',
      data: data,
      label: {
        show: true
      },
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

const initCumReturnChart = () => {
  if (!cumReturnChartRef.value) return
  cumReturnChart = echarts.init(cumReturnChartRef.value)
  
  const series = visualForm.value.factors.map(factorId => {
    const factor = factorList.find(f => f.id === factorId)
    const data: number[] = []
    let cumReturn = 0
    for (let i = 0; i < 60; i++) {
      cumReturn += (Math.random() - 0.45) * 0.02
      data.push((cumReturn * 100).toFixed(2))
    }
    return {
      name: factor?.name,
      type: 'line',
      data: data,
      smooth: true
    }
  })

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let result = params[0].axisValue + '<br/>'
        params.forEach((param: any) => {
          result += `${param.seriesName}: ${param.value}%<br/>`
        })
        return result
      }
    },
    legend: {
      data: visualForm.value.factors.map(id => factorList.find(f => f.id === id)?.name)
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
      data: dates
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series
  }

  cumReturnChart.setOption(option)
}

const initQuantileChart = () => {
  if (!quantileChartRef.value) return
  quantileChart = echarts.init(quantileChartRef.value)
  
  const quantiles = ['Q1 (最小)', 'Q2', 'Q3', 'Q4', 'Q5 (最大)']
  const returns = [-5.2, -1.8, 2.1, 5.6, 12.3]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        return `${params[0].name}<br/>收益率: ${params[0].value}%`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: quantiles
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: '收益率',
      type: 'bar',
      data: returns.map((val, idx) => ({
        value: val,
        itemStyle: {
          color: val >= 0 ? '#67C23A' : '#F56C6C'
        }
      }))
    }]
  }

  quantileChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initICChart()
    initDistributionChart()
    initHeatmapChart()
    initCumReturnChart()
    initQuantileChart()
  })
}

const handleRefresh = () => {
  ElMessage.info('正在刷新图表...')
  initAllCharts()
  setTimeout(() => {
    ElMessage.success('图表已刷新')
  }, 500)
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    icChart?.resize()
    distributionChart?.resize()
    heatmapChart?.resize()
    cumReturnChart?.resize()
    quantileChart?.resize()
  })
})
</script>

<style scoped>
.factor-visualization-container {
  padding: 20px;
}

.control-card,
.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.visual-form {
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .factor-visualization-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>

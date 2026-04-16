<template>
  <div class="position-analysis-container">
    <el-card class="overview-card">
      <template #header>
        <span>持仓概览</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总持仓市值</div>
            <div class="stat-value">¥{{ totalPositionValue.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">持仓品种数</div>
            <div class="stat-value">{{ positionCount }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总持仓盈亏</div>
            <div class="stat-value" :class="{ 'profit': totalPnL >= 0, 'loss': totalPnL < 0 }">
              ¥{{ totalPnL >= 0 ? '+' : '' }}{{ totalPnL.toLocaleString() }}
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">持仓盈亏比例</div>
            <div class="stat-value" :class="{ 'profit': pnlRatio >= 0, 'loss': pnlRatio < 0 }">
              {{ pnlRatio >= 0 ? '+' : '' }}{{ pnlRatio.toFixed(2) }}%
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>持仓市值分布</span>
          </template>
          <div ref="pieChartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>行业分布</span>
          </template>
          <div ref="barChartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>盈亏分布</span>
          </template>
          <div ref="pnlChartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>持仓时间分布</span>
          </template>
          <div ref="timeChartRef" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="list-card" style="margin-top: 20px;">
      <template #header>
        <span>持仓明细</span>
      </template>
      <el-table :data="positionList" stripe style="width: 100%">
        <el-table-column prop="symbol" label="合约代码" width="120" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="industry" label="行业" width="120" />
        <el-table-column prop="direction" label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'long' ? 'success' : 'danger'">
              {{ row.direction === 'long' ? '做多' : '做空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="持仓数量" width="100" sortable />
        <el-table-column prop="avgCost" label="持仓成本" width="120" sortable />
        <el-table-column prop="currentPrice" label="当前价格" width="120" sortable />
        <el-table-column prop="marketValue" label="市值" width="140" sortable>
          <template #default="{ row }">
            ¥{{ row.marketValue.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="pnl" label="持仓盈亏" width="120" sortable>
          <template #default="{ row }">
            <span :class="{ 'profit': row.pnl >= 0, 'loss': row.pnl < 0 }">
              ¥{{ row.pnl >= 0 ? '+' : '' }}{{ row.pnl.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="pnlRatio" label="盈亏比例" width="100" sortable>
          <template #default="{ row }">
            <span :class="{ 'profit': row.pnlRatio >= 0, 'loss': row.pnlRatio < 0 }">
              {{ row.pnlRatio >= 0 ? '+' : '' }}{{ row.pnlRatio.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="holdingDays" label="持仓天数" width="100" sortable />
        <el-table-column prop="weight" label="权重" width="100">
          <template #default="{ row }">
            {{ row.weight.toFixed(2) }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Position {
  symbol: string
  name: string
  industry: string
  direction: string
  quantity: number
  avgCost: number
  currentPrice: number
  marketValue: number
  pnl: number
  pnlRatio: number
  holdingDays: number
  weight: number
}

const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
const pnlChartRef = ref<HTMLElement>()
const timeChartRef = ref<HTMLElement>()

let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let pnlChart: echarts.ECharts | null = null
let timeChart: echarts.ECharts | null = null

const mockPositions: Position[] = [
  { symbol: 'AU.SHF', name: '黄金', industry: '贵金属', direction: 'long', quantity: 20, avgCost: 720.5, currentPrice: 735.8, marketValue: 147160, pnl: 3060, pnlRatio: 2.12, holdingDays: 15, weight: 32.7 },
  { symbol: 'AG.SHF', name: '白银', industry: '贵金属', direction: 'short', quantity: 100, avgCost: 5750, currentPrice: 5680, marketValue: 568000, pnl: 7000, pnlRatio: 1.22, holdingDays: 8, weight: 25.2 },
  { symbol: 'CU.SHF', name: '铜', industry: '有色金属', direction: 'long', quantity: 10, avgCost: 68500, currentPrice: 69200, marketValue: 692000, pnl: 7000, pnlRatio: 1.02, holdingDays: 12, weight: 23.1 },
  { symbol: 'RU.SHF', name: '橡胶', industry: '化工', direction: 'long', quantity: 15, avgCost: 12600, currentPrice: 12850, marketValue: 192750, pnl: 3750, pnlRatio: 1.98, holdingDays: 5, weight: 8.5 },
  { symbol: 'NI.SHF', name: '镍', industry: '有色金属', direction: 'short', quantity: 3, avgCost: 145000, currentPrice: 142500, marketValue: 427500, pnl: 7500, pnlRatio: 1.72, holdingDays: 3, weight: 10.5 }
]

const positionList = ref<Position[]>(mockPositions)

const totalPositionValue = computed(() => positionList.value.reduce((sum, item) => sum + item.marketValue, 0))
const positionCount = computed(() => positionList.value.length)
const totalPnL = computed(() => positionList.value.reduce((sum, item) => sum + item.pnl, 0))
const pnlRatio = computed(() => (totalPnL.value / (totalPositionValue.value - totalPnL.value)) * 100)

const initPieChart = () => {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '持仓市值',
        type: 'pie',
        radius: '50%',
        data: positionList.value.map(item => ({
          value: item.marketValue,
          name: item.symbol
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  pieChart.setOption(option)
}

const initBarChart = () => {
  if (!barChartRef.value) return
  barChart = echarts.init(barChartRef.value)
  const industryData: Record<string, number> = {}
  positionList.value.forEach(item => {
    industryData[item.industry] = (industryData[item.industry] || 0) + item.marketValue
  })
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: ¥{c}'
    },
    xAxis: {
      type: 'category',
      data: Object.keys(industryData)
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '行业市值',
        type: 'bar',
        data: Object.values(industryData),
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  barChart.setOption(option)
}

const initPnlChart = () => {
  if (!pnlChartRef.value) return
  pnlChart = echarts.init(pnlChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: positionList.value.map(item => item.symbol)
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        name: '持仓盈亏',
        type: 'bar',
        data: positionList.value.map(item => item.pnl),
        itemStyle: {
          color: (params: any) => params.value >= 0 ? '#67C23A' : '#F56C6C'
        }
      }
    ]
  }
  pnlChart.setOption(option)
}

const initTimeChart = () => {
  if (!timeChartRef.value) return
  timeChart = echarts.init(timeChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: positionList.value.map(item => item.symbol)
    },
    yAxis: {
      type: 'value',
      name: '持仓天数'
    },
    series: [
      {
        name: '持仓天数',
        type: 'line',
        data: positionList.value.map(item => item.holdingDays),
        smooth: true,
        areaStyle: {
          color: 'rgba(64, 158, 255, 0.3)'
        },
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  timeChart.setOption(option)
}

const handleResize = () => {
  pieChart?.resize()
  barChart?.resize()
  pnlChart?.resize()
  timeChart?.resize()
}

onMounted(() => {
  setTimeout(() => {
    initPieChart()
    initBarChart()
    initPnlChart()
    initTimeChart()
  }, 100)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  pieChart?.dispose()
  barChart?.dispose()
  pnlChart?.dispose()
  timeChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.position-analysis-container {
  padding: 20px;
}

.overview-card,
.chart-card,
.list-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.profit {
  color: #67C23A;
}

.stat-value.loss {
  color: #F56C6C;
}

.profit {
  color: #67C23A;
}

.loss {
  color: #F56C6C;
}

@media (max-width: 768px) {
  .position-analysis-container {
    padding: 10px;
  }
}
</style>

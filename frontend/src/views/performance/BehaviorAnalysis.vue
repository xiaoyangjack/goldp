<template>
  <div class="behavior-analysis-container">
    <el-card class="overview-card">
      <template #header>
        <span>交易行为概览</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总交易次数</div>
            <div class="stat-value">{{ totalTrades }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">盈利次数</div>
            <div class="stat-value">{{ profitableTrades }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">亏损次数</div>
            <div class="stat-value">{{ losingTrades }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">胜率</div>
            <div class="stat-value" :class="{ 'profit': winRate >= 50 }">{{ winRate.toFixed(2) }}%</div>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均持仓时间</div>
            <div class="stat-value">{{ avgHoldingTime }}天</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均盈利</div>
            <div class="stat-value profit">¥{{ avgProfit.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均亏损</div>
            <div class="stat-value loss">¥{{ avgLoss.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">盈亏比</div>
            <div class="stat-value" :class="{ 'profit': profitLossRatio >= 1 }">{{ profitLossRatio.toFixed(2) }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>交易频率分布</span>
          </template>
          <div ref="frequencyChartRef" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>盈亏分布</span>
          </template>
          <div ref="pnlDistChartRef" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>月度交易统计</span>
          </template>
          <div ref="monthlyChartRef" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>品种交易分布</span>
          </template>
          <div ref="symbolChartRef" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="list-card" style="margin-top: 20px;">
      <template #header>
        <span>交易记录明细</span>
      </template>
      <el-table :data="tradeList" stripe style="width: 100%">
        <el-table-column prop="tradeId" label="交易ID" width="120" />
        <el-table-column prop="symbol" label="合约代码" width="120" />
        <el-table-column prop="direction" label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'long' ? 'success' : 'danger'">
              {{ row.direction === 'long' ? '做多' : '做空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="openPrice" label="开仓价" width="100" />
        <el-table-column prop="closePrice" label="平仓价" width="100" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="pnl" label="盈亏" width="120" sortable>
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
        <el-table-column prop="openTime" label="开仓时间" width="180" />
        <el-table-column prop="closeTime" label="平仓时间" width="180" />
      </el-table>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: center;" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Trade {
  tradeId: string
  symbol: string
  direction: string
  openPrice: number
  closePrice: number
  quantity: number
  pnl: number
  pnlRatio: number
  holdingDays: number
  openTime: string
  closeTime: string
}

const frequencyChartRef = ref<HTMLElement>()
const pnlDistChartRef = ref<HTMLElement>()
const monthlyChartRef = ref<HTMLElement>()
const symbolChartRef = ref<HTMLElement>()

let frequencyChart: echarts.ECharts | null = null
let pnlDistChart: echarts.ECharts | null = null
let monthlyChart: echarts.ECharts | null = null
let symbolChart: echarts.ECharts | null = null

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const mockTrades: Trade[] = [
  { tradeId: 'T001', symbol: 'AU.SHF', direction: 'long', openPrice: 720.5, closePrice: 735.8, quantity: 10, pnl: 1530, pnlRatio: 2.12, holdingDays: 5, openTime: '2024-04-01 09:30:00', closeTime: '2024-04-08 14:45:00' },
  { tradeId: 'T002', symbol: 'AG.SHF', direction: 'short', openPrice: 5750, closePrice: 5680, quantity: 50, pnl: 3500, pnlRatio: 1.22, holdingDays: 3, openTime: '2024-04-02 10:15:00', closeTime: '2024-04-05 13:20:00' },
  { tradeId: 'T003', symbol: 'CU.SHF', direction: 'long', openPrice: 68500, closePrice: 69200, quantity: 5, pnl: 3500, pnlRatio: 1.02, holdingDays: 8, openTime: '2024-04-03 09:45:00', closeTime: '2024-04-11 11:30:00' },
  { tradeId: 'T004', symbol: 'AU.SHF', direction: 'short', openPrice: 732.2, closePrice: 728.8, quantity: 8, pnl: 272, pnlRatio: 0.46, holdingDays: 2, openTime: '2024-04-08 14:20:00', closeTime: '2024-04-10 10:05:00' },
  { tradeId: 'T005', symbol: 'RU.SHF', direction: 'long', openPrice: 12600, closePrice: 12850, quantity: 10, pnl: 2500, pnlRatio: 1.98, holdingDays: 4, openTime: '2024-04-09 11:00:00', closeTime: '2024-04-13 15:00:00' },
  { tradeId: 'T006', symbol: 'AG.SHF', direction: 'long', openPrice: 5720, closePrice: 5650, quantity: 30, pnl: -2100, pnlRatio: -1.22, holdingDays: 6, openTime: '2024-04-10 09:30:00', closeTime: '2024-04-16 10:45:00' },
  { tradeId: 'T007', symbol: 'AU.SHF', direction: 'long', openPrice: 728.8, closePrice: 735.5, quantity: 15, pnl: 1005, pnlRatio: 0.92, holdingDays: 3, openTime: '2024-04-11 14:00:00', closeTime: '2024-04-14 13:15:00' },
  { tradeId: 'T008', symbol: 'CU.SHF', direction: 'short', openPrice: 69500, closePrice: 69800, quantity: 3, pnl: -900, pnlRatio: -0.43, holdingDays: 1, openTime: '2024-04-15 10:30:00', closeTime: '2024-04-16 09:45:00' }
]

const tradeList = ref<Trade[]>(mockTrades)

const totalTrades = computed(() => tradeList.value.length)
const profitableTrades = computed(() => tradeList.value.filter(t => t.pnl >= 0).length)
const losingTrades = computed(() => tradeList.value.filter(t => t.pnl < 0).length)
const winRate = computed(() => (profitableTrades.value / totalTrades.value) * 100)
const avgHoldingTime = computed(() => tradeList.value.reduce((sum, t) => sum + t.holdingDays, 0) / totalTrades.value)
const avgProfit = computed(() => {
  const profits = tradeList.value.filter(t => t.pnl >= 0).map(t => t.pnl)
  return profits.length > 0 ? profits.reduce((a, b) => a + b, 0) / profits.length : 0
})
const avgLoss = computed(() => {
  const losses = tradeList.value.filter(t => t.pnl < 0).map(t => Math.abs(t.pnl))
  return losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / losses.length : 0
})
const profitLossRatio = computed(() => avgLoss.value > 0 ? avgProfit.value / avgLoss.value : 0)

const initFrequencyChart = () => {
  if (!frequencyChartRef.value) return
  frequencyChart = echarts.init(frequencyChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五']
    },
    yAxis: {
      type: 'value',
      name: '交易次数'
    },
    series: [
      {
        name: '交易次数',
        type: 'bar',
        data: [12, 8, 15, 10, 18],
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  frequencyChart.setOption(option)
}

const initPnlDistChart = () => {
  if (!pnlDistChartRef.value) return
  pnlDistChart = echarts.init(pnlDistChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['<-5%', '-5%~-2%', '-2%~0', '0~2%', '2%~5%', '>5%']
    },
    yAxis: {
      type: 'value',
      name: '交易次数'
    },
    series: [
      {
        name: '交易次数',
        type: 'bar',
        data: [3, 5, 8, 12, 10, 6],
        itemStyle: {
          color: (params: any) => params.dataIndex < 3 ? '#F56C6C' : '#67C23A'
        }
      }
    ]
  }
  pnlDistChart.setOption(option)
}

const initMonthlyChart = () => {
  if (!monthlyChartRef.value) return
  monthlyChart = echarts.init(monthlyChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['盈利交易', '亏损交易']
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月']
    },
    yAxis: {
      type: 'value',
      name: '交易次数'
    },
    series: [
      {
        name: '盈利交易',
        type: 'bar',
        stack: 'total',
        data: [15, 18, 12, 5],
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '亏损交易',
        type: 'bar',
        stack: 'total',
        data: [8, 6, 10, 3],
        itemStyle: {
          color: '#F56C6C'
        }
      }
    ]
  }
  monthlyChart.setOption(option)
}

const initSymbolChart = () => {
  if (!symbolChartRef.value) return
  symbolChart = echarts.init(symbolChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}次 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '交易次数',
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: 25, name: 'AU.SHF' },
          { value: 20, name: 'AG.SHF' },
          { value: 15, name: 'CU.SHF' },
          { value: 10, name: 'RU.SHF' },
          { value: 8, name: 'NI.SHF' }
        ]
      }
    ]
  }
  symbolChart.setOption(option)
}

const handleResize = () => {
  frequencyChart?.resize()
  pnlDistChart?.resize()
  monthlyChart?.resize()
  symbolChart?.resize()
}

onMounted(() => {
  total.value = mockTrades.length
  setTimeout(() => {
    initFrequencyChart()
    initPnlDistChart()
    initMonthlyChart()
    initSymbolChart()
  }, 100)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  frequencyChart?.dispose()
  pnlDistChart?.dispose()
  monthlyChart?.dispose()
  symbolChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.behavior-analysis-container {
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

.profit {
  color: #67C23A;
}

.loss {
  color: #F56C6C;
}

@media (max-width: 768px) {
  .behavior-analysis-container {
    padding: 10px;
  }
}
</style>

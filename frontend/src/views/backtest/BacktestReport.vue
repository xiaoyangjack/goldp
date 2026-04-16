<template>
  <div class="backtest-report-container">
    <el-card class="header-card">
      <div class="report-header">
        <div class="report-title">
          <h2>回测报告</h2>
          <p class="report-subtitle">策略: {{ reportData.strategyName }} | 标的: {{ reportData.symbol }} | 周期: {{ reportData.startDate }} ~ {{ reportData.endDate }}</p>
        </div>
        <div class="report-actions">
          <el-button-group>
            <el-button type="primary" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出报告
            </el-button>
            <el-button type="success" @click="handlePrint">
              <el-icon><Printer /></el-icon>
              打印
            </el-button>
            <el-button @click="handleCompare">
              <el-icon><ScaleToOriginal /></el-icon>
              对比
            </el-button>
          </el-button-group>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6" v-for="metric in performanceMetrics" :key="metric.key">
        <el-card class="metric-card" :class="`metric-${metric.type}`">
          <div class="metric-icon">
            <el-icon :size="40"><component :is="metric.icon" /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-value">{{ metric.value }}</div>
            <div class="metric-change" :class="metric.change >= 0 ? 'up' : 'down'">
              <el-icon><component :is="metric.change >= 0 ? Top : Bottom" /></el-icon>
              {{ Math.abs(metric.change).toFixed(2) }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>资金曲线</span>
              <el-radio-group v-model="equityChartType" size="small">
                <el-radio-button value="equity">资金曲线</el-radio-button>
                <el-radio-button value="drawdown">回撤曲线</el-radio-button>
                <el-radio-button value="both">叠加显示</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="equityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>收益率分布</span>
          </template>
          <div ref="distributionChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>月度收益</span>
          </template>
          <div ref="monthlyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>持仓分析</span>
          </template>
          <div ref="positionChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="detail-card" style="margin-top: 20px;">
      <template #header>
        <span>详细指标</span>
      </template>
      <el-tabs v-model="activeDetailTab">
        <el-tab-pane label="收益指标" name="return">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="累计收益率">{{ (reportData.totalReturn * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="年化收益率">{{ (reportData.annualizedReturn * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="基准收益率">{{ (reportData.benchmarkReturn * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="超额收益率">{{ (reportData.excessReturn * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="日胜率">{{ (reportData.dailyWinRate * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="月胜率">{{ (reportData.monthlyWinRate * 100).toFixed(2) }}%</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="风险指标" name="risk">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="最大回撤">{{ (reportData.maxDrawdown * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="回撤开始时间">{{ reportData.drawdownStartDate }}</el-descriptions-item>
            <el-descriptions-item label="回撤结束时间">{{ reportData.drawdownEndDate }}</el-descriptions-item>
            <el-descriptions-item label="波动率">{{ (reportData.volatility * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="下行波动率">{{ (reportData.downsideVolatility * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="VaR(95%)">{{ (reportData.var95 * 100).toFixed(2) }}%</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="风险调整收益" name="riskAdjusted">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="夏普比率">{{ reportData.sharpeRatio.toFixed(3) }}</el-descriptions-item>
            <el-descriptions-item label="索提诺比率">{{ reportData.sortinoRatio.toFixed(3) }}</el-descriptions-item>
            <el-descriptions-item label="卡玛比率">{{ reportData.calmarRatio.toFixed(3) }}</el-descriptions-item>
            <el-descriptions-item label="信息比率">{{ reportData.informationRatio.toFixed(3) }}</el-descriptions-item>
            <el-descriptions-item label="欧米伽比率">{{ reportData.omegaRatio.toFixed(3) }}</el-descriptions-item>
            <el-descriptions-item label="特雷诺比率">{{ reportData.treynorRatio.toFixed(3) }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="交易统计" name="trading">
          <el-descriptions :column="3" border>
            <el-descriptions-item label="总交易次数">{{ reportData.totalTrades }}</el-descriptions-item>
            <el-descriptions-item label="盈利交易次数">{{ reportData.winningTrades }}</el-descriptions-item>
            <el-descriptions-item label="亏损交易次数">{{ reportData.losingTrades }}</el-descriptions-item>
            <el-descriptions-item label="交易胜率">{{ (reportData.tradeWinRate * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="平均盈利">{{ (reportData.avgWin * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="平均亏损">{{ (reportData.avgLoss * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="盈亏比">{{ reportData.profitLossRatio.toFixed(2) }}</el-descriptions-item>
            <el-descriptions-item label="平均持仓天数">{{ reportData.avgHoldDays.toFixed(1) }}</el-descriptions-item>
            <el-descriptions-item label="最大连续盈利次数">{{ reportData.maxWinStreak }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card class="trades-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>交易记录</span>
          <el-button type="primary" size="small" @click="handleExportTrades">
            <el-icon><Download /></el-icon>
            导出交易记录
          </el-button>
        </div>
      </template>
      <el-table :data="tradeRecords" stripe style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.type === '买入' ? 'success' : 'danger'" size="small">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="120" sortable />
        <el-table-column prop="amount" label="数量" width="100" sortable />
        <el-table-column prop="value" label="金额" width="120" sortable />
        <el-table-column prop="commission" label="手续费" width="100" />
        <el-table-column prop="pnl" label="盈亏" width="120" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.pnl >= 0 ? '#67C23A' : '#F56C6C' }">
              {{ row.pnl?.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="pnlPercent" label="盈亏%" width="100" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.pnlPercent >= 0 ? '#67C23A' : '#F56C6C' }">
              {{ row.pnlPercent >= 0 ? '+' : '' }}{{ row.pnlPercent?.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { Download, Printer, ScaleToOriginal, Top, Bottom, Trophy, TrendCharts, Warning, Coin } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeDetailTab = ref('return')
const equityChartType = ref('equity')

const equityChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()
const monthlyChartRef = ref<HTMLElement>()
const positionChartRef = ref<HTMLElement>()

let equityChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let monthlyChart: echarts.ECharts | null = null
let positionChart: echarts.ECharts | null = null

const reportData = ref({
  strategyName: '均线交叉策略',
  symbol: 'AU.SHF',
  startDate: '2023-01-01',
  endDate: '2024-04-15',
  totalReturn: 0.358,
  annualizedReturn: 0.285,
  benchmarkReturn: 0.152,
  excessReturn: 0.206,
  dailyWinRate: 0.532,
  monthlyWinRate: 0.615,
  maxDrawdown: -0.125,
  drawdownStartDate: '2023-06-15',
  drawdownEndDate: '2023-09-20',
  volatility: 0.235,
  downsideVolatility: 0.152,
  var95: -0.028,
  sharpeRatio: 1.582,
  sortinoRatio: 2.145,
  calmarRatio: 2.280,
  informationRatio: 1.325,
  omegaRatio: 1.852,
  treynorRatio: 0.185,
  totalTrades: 128,
  winningTrades: 72,
  losingTrades: 56,
  tradeWinRate: 0.562,
  avgWin: 0.032,
  avgLoss: -0.018,
  profitLossRatio: 1.78,
  avgHoldDays: 8.5,
  maxWinStreak: 8
})

const performanceMetrics = ref([
  { key: 'totalReturn', label: '累计收益率', value: '+35.80%', type: 'primary', icon: Trophy, change: 12.5 },
  { key: 'annualReturn', label: '年化收益率', value: '+28.50%', type: 'success', icon: TrendCharts, change: 8.3 },
  { key: 'maxDrawdown', label: '最大回撤', value: '-12.50%', type: 'warning', icon: Warning, change: -3.2 },
  { key: 'sharpe', label: '夏普比率', value: '1.58', type: 'info', icon: Coin, change: 0.15 }
])

const tradeRecords = ref([
  { date: '2024-04-10', type: '卖出', price: 205.50, amount: 100, value: 20550, commission: 6.17, pnl: 320.50, pnlPercent: 1.58 },
  { date: '2024-04-05', type: '买入', price: 202.30, amount: 100, value: 20230, commission: 6.07, pnl: null, pnlPercent: null },
  { date: '2024-03-28', type: '卖出', price: 198.80, amount: 100, value: 19880, commission: 5.96, pnl: -180.30, pnlPercent: -0.90 },
  { date: '2024-03-20', type: '买入', price: 200.60, amount: 100, value: 20060, commission: 6.02, pnl: null, pnlPercent: null },
  { date: '2024-03-15', type: '卖出', price: 203.20, amount: 100, value: 20320, commission: 6.10, pnl: 280.80, pnlPercent: 1.40 }
])

const initEquityChart = () => {
  if (!equityChartRef.value) return
  equityChart = echarts.init(equityChartRef.value)
  
  const dates = []
  const equity = []
  const benchmark = []
  const drawdown = []
  let value = 100000
  let benchmarkValue = 100000
  let maxEquity = 100000
  
  for (let i = 0; i < 300; i++) {
    const date = new Date('2023-01-01')
    date.setDate(date.getDate() + i)
    dates.push(date.toISOString().split('T')[0])
    
    const dailyReturn = (Math.random() - 0.48) * 0.02
    const benchmarkReturn = (Math.random() - 0.49) * 0.015
    
    value *= (1 + dailyReturn)
    benchmarkValue *= (1 + benchmarkReturn)
    maxEquity = Math.max(maxEquity, value)
    
    equity.push(value.toFixed(2))
    benchmark.push(benchmarkValue.toFixed(2))
    drawdown.push(((maxEquity - value) / maxEquity * 100).toFixed(2))
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['策略净值', '基准净值', '回撤']
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
    yAxis: [
      {
        type: 'value',
        name: '净值'
      },
      {
        type: 'value',
        name: '回撤(%)',
        inverse: true
      }
    ],
    series: [
      {
        name: '策略净值',
        type: 'line',
        smooth: true,
        data: equity,
        yAxisIndex: 0,
        areaStyle: {
          opacity: 0.3
        }
      },
      {
        name: '基准净值',
        type: 'line',
        smooth: true,
        data: benchmark,
        yAxisIndex: 0,
        lineStyle: {
          type: 'dashed'
        }
      },
      {
        name: '回撤',
        type: 'line',
        smooth: true,
        data: drawdown,
        yAxisIndex: 1,
        areaStyle: {
          opacity: 0.1,
          color: '#F56C6C'
        },
        lineStyle: {
          color: '#F56C6C'
        },
        itemStyle: {
          color: '#F56C6C'
        }
      }
    ]
  }

  equityChart.setOption(option)
}

const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  distributionChart = echarts.init(distributionChartRef.value)
  
  const bins = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
  const data = [5, 12, 28, 45, 68, 72, 65, 42, 25, 10]

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
      data: bins.map(b => `${b}%`)
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      type: 'bar',
      data: data.map((val, idx) => ({
        value: val,
        itemStyle: {
          color: bins[idx] >= 0 ? '#67C23A' : '#F56C6C'
        }
      }))
    }]
  }

  distributionChart.setOption(option)
}

const initMonthlyChart = () => {
  if (!monthlyChartRef.value) return
  monthlyChart = echarts.init(monthlyChartRef.value)
  
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  const returns = [2.5, -1.2, 5.8, 3.2, -2.1, 4.5, 1.8, -0.5, 6.2, 3.8, -1.5, 4.2]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => `${params[0].name}<br/>收益率: ${params[0].value}%`
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      type: 'bar',
      data: returns.map((val, idx) => ({
        value: val,
        itemStyle: {
          color: val >= 0 ? '#67C23A' : '#F56C6C'
        }
      }))
    }]
  }

  monthlyChart.setOption(option)
}

const initPositionChart = () => {
  if (!positionChartRef.value) return
  positionChart = echarts.init(positionChartRef.value)
  
  const data = [
    { value: 40, name: '多头持仓' },
    { value: 30, name: '空头持仓' },
    { value: 30, name: '现金' }
  ]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%'
    },
    legend: {
      bottom: '0%',
      left: 'center'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: data
    }]
  }

  positionChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initEquityChart()
    initDistributionChart()
    initMonthlyChart()
    initPositionChart()
  })
}

const handleExport = () => {
  ElMessage.success('报告导出成功')
}

const handlePrint = () => {
  window.print()
}

const handleCompare = () => {
  ElMessage.info('打开对比功能')
}

const handleExportTrades = () => {
  ElMessage.success('交易记录导出成功')
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    equityChart?.resize()
    distributionChart?.resize()
    monthlyChart?.resize()
    positionChart?.resize()
  })
})
</script>

<style scoped>
.backtest-report-container {
  padding: 20px;
}

.header-card,
.chart-card,
.detail-card,
.trades-card {
  margin-bottom: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-title h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.report-subtitle {
  margin: 0;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-card {
  display: flex;
  padding: 20px;
  margin-bottom: 20px;
}

.metric-icon {
  margin-right: 20px;
  display: flex;
  align-items: center;
  color: #409EFF;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.metric-change {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.metric-change.up {
  color: #67C23A;
}

.metric-change.down {
  color: #F56C6C;
}

.chart-container {
  height: 350px;
  width: 100%;
}

@media (max-width: 768px) {
  .backtest-report-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>

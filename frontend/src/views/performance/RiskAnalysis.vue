<template>
  <div class="risk-analysis-container">
    <el-card class="summary-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="risk-metric">
            <div class="metric-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-label">波动率</div>
              <div class="metric-value">{{ (riskData.volatility * 100).toFixed(2) }}%</div>
              <div class="metric-trend" :class="riskData.volatilityTrend >= 0 ? 'up' : 'down'">
                <el-icon><component :is="riskData.volatilityTrend >= 0 ? Top : Bottom" /></el-icon>
                {{ Math.abs(riskData.volatilityTrend * 100).toFixed(2) }}%
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="risk-metric">
            <div class="metric-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon :size="30"><Warning /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-label">最大回撤</div>
              <div class="metric-value">{{ (riskData.maxDrawdown * 100).toFixed(2) }}%</div>
              <div class="metric-trend" :class="riskData.drawdownTrend <= 0 ? 'up' : 'down'">
                <el-icon><component :is="riskData.drawdownTrend <= 0 ? Bottom : Top" /></el-icon>
                {{ Math.abs(riskData.drawdownTrend * 100).toFixed(2) }}%
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="risk-metric">
            <div class="metric-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon :size="30"><Odometer /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-label">VaR (95%)</div>
              <div class="metric-value">{{ (riskData.var95 * 100).toFixed(2) }}%</div>
              <div class="metric-trend" :class="riskData.varTrend <= 0 ? 'up' : 'down'">
                <el-icon><component :is="riskData.varTrend <= 0 ? Bottom : Top" /></el-icon>
                {{ Math.abs(riskData.varTrend * 100).toFixed(2) }}%
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="risk-metric">
            <div class="metric-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
              <el-icon :size="30"><ScaleToOriginal /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-label">下行波动率</div>
              <div class="metric-value">{{ (riskData.downsideVolatility * 100).toFixed(2) }}%</div>
              <div class="metric-trend" :class="riskData.downsideTrend >= 0 ? 'up' : 'down'">
                <el-icon><component :is="riskData.downsideTrend >= 0 ? Top : Bottom" /></el-icon>
                {{ Math.abs(riskData.downsideTrend * 100).toFixed(2) }}%
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>回撤走势</span>
              <el-radio-group v-model="drawbackChartType" size="small">
                <el-radio-button value="drawdown">回撤</el-radio-button>
                <el-radio-button value="underwater">水下图</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="drawdownChartRef" class="chart-container"></div>
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
            <span>VaR分析</span>
          </template>
          <div ref="varChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>滚动波动率</span>
          </template>
          <div ref="rollingVolChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="detail-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>风险指标详情</span>
          <el-button type="primary" size="small" @click="exportRiskReport">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="回撤统计" name="drawdown">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="最大回撤">{{ (riskData.maxDrawdown * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="回撤开始日期">{{ riskData.drawdownStartDate }}</el-descriptions-item>
            <el-descriptions-item label="回撤结束日期">{{ riskData.drawdownEndDate }}</el-descriptions-item>
            <el-descriptions-item label="回撤持续天数">{{ riskData.drawdownDuration }}天</el-descriptions-item>
            <el-descriptions-item label="恢复天数">{{ riskData.recoveryDays }}天</el-descriptions-item>
            <el-descriptions-item label="平均回撤">{{ (riskData.avgDrawdown * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="回撤次数">{{ riskData.drawdownCount }}</el-descriptions-item>
            <el-descriptions-item label="最大回撤(月)">{{ (riskData.maxMonthlyDrawdown * 100).toFixed(2) }}%</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="VaR分析" name="var">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="VaR (95%)">{{ (riskData.var95 * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="VaR (99%)">{{ (riskData.var99 * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="CVaR (95%)">{{ (riskData.cvar95 * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="CVaR (99%)">{{ (riskData.cvar99 * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="历史VaR突破次数">{{ riskData.varBreaches }}</el-descriptions-item>
            <el-descriptions-item label="VaR突破率">{{ (riskData.varBreachRate * 100).toFixed(2) }}%</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="波动率分析" name="volatility">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="年化波动率">{{ (riskData.volatility * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="下行波动率">{{ (riskData.downsideVolatility * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="上行波动率">{{ (riskData.upsideVolatility * 100).toFixed(2) }}%</el-descriptions-item>
            <el-descriptions-item label="波动率偏度">{{ riskData.volatilitySkew.toFixed(3) }}</el-descriptions-item>
            <el-descriptions-item label="波动率峰度">{{ riskData.volatilityKurtosis.toFixed(3) }}</el-descriptions-item>
            <el-descriptions-item label="GARCH波动率">{{ (riskData.garchVolatility * 100).toFixed(2) }}%</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="压力测试" name="stress">
          <el-table :data="stressTestResults" stripe style="width: 100%">
            <el-table-column prop="scenario" label="压力场景" width="200" />
            <el-table-column prop="shock" label="冲击幅度" width="120" />
            <el-table-column prop="pnl" label="盈亏" width="150">
              <template #default="{ row }">
                <span :style="{ color: row.pnl >= 0 ? '#67C23A' : '#F56C6C' }">
                  {{ (row.pnl * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="varImpact" label="VaR变化" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '安全' ? 'success' : row.status === '警告' ? 'warning' : 'danger'" size="small">
                  {{ row.status }}
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
import { TrendCharts, Warning, Odometer, ScaleToOriginal, Top, Bottom, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('drawdown')
const drawbackChartType = ref('drawdown')

const drawdownChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()
const varChartRef = ref<HTMLElement>()
const rollingVolChartRef = ref<HTMLElement>()

let drawdownChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let varChart: echarts.ECharts | null = null
let rollingVolChart: echarts.ECharts | null = null

const riskData = ref({
  volatility: 0.235,
  volatilityTrend: -0.015,
  maxDrawdown: -0.185,
  drawdownTrend: 0.023,
  var95: -0.028,
  varTrend: -0.003,
  downsideVolatility: 0.142,
  downsideTrend: -0.008,
  drawdownStartDate: '2023-06-15',
  drawdownEndDate: '2023-10-20',
  drawdownDuration: 127,
  recoveryDays: 45,
  avgDrawdown: -0.068,
  drawdownCount: 8,
  maxMonthlyDrawdown: -0.085,
  var99: -0.042,
  cvar95: -0.035,
  cvar99: -0.052,
  varBreaches: 12,
  varBreachRate: 0.042,
  upsideVolatility: 0.189,
  volatilitySkew: 0.235,
  volatilityKurtosis: 3.452,
  garchVolatility: 0.221
})

const stressTestResults = ref([
  { scenario: '市场大跌', shock: '-10%', pnl: -0.152, varImpact: '+2.5%', status: '警告' },
  { scenario: '波动率飙升', shock: '+50%', pnl: -0.085, varImpact: '+1.8%', status: '安全' },
  { scenario: '流动性危机', shock: 'NA', pnl: -0.215, varImpact: '+3.2%', status: '危险' },
  { scenario: '黑天鹅事件', shock: '-20%', pnl: -0.325, varImpact: '+5.8%', status: '危险' },
  { scenario: '利率上升', shock: '+2%', pnl: -0.045, varImpact: '+0.5%', status: '安全' }
])

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

const dates = generateDates(250)

const exportRiskReport = () => {
  ElMessage.success('风险报告导出成功')
}

const initDrawdownChart = () => {
  if (!drawdownChartRef.value) return
  drawdownChart = echarts.init(drawdownChartRef.value)
  
  const equity = []
  const drawdown = []
  let value = 1000000
  let maxValue = value
  
  for (let i = 0; i < 250; i++) {
    const dailyReturn = (Math.random() - 0.48) * 0.025
    value *= (1 + dailyReturn)
    maxValue = Math.max(maxValue, value)
    equity.push(value.toFixed(0))
    drawdown.push((((maxValue - value) / maxValue) * 100).toFixed(2))
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['净值', '回撤']
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
        name: '净值',
        type: 'line',
        smooth: true,
        data: equity,
        yAxisIndex: 0,
        areaStyle: { opacity: 0.3 }
      },
      {
        name: '回撤',
        type: 'line',
        smooth: true,
        data: drawdown,
        yAxisIndex: 1,
        areaStyle: {
          opacity: 0.3,
          color: '#F56C6C'
        },
        lineStyle: { color: '#F56C6C' },
        itemStyle: { color: '#F56C6C' }
      }
    ]
  }

  drawdownChart.setOption(option)
}

const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  distributionChart = echarts.init(distributionChartRef.value)
  
  const bins = [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
  const data = [3, 5, 8, 15, 25, 40, 60, 85, 90, 80, 55, 35, 20, 12, 7, 4, 2]

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

const initVarChart = () => {
  if (!varChartRef.value) return
  varChart = echarts.init(varChartRef.value)
  
  const returns = []
  const var95 = []
  const var99 = []
  
  for (let i = 0; i < 100; i++) {
    const ret = (Math.random() - 0.5) * 0.05
    returns.push(parseFloat((ret * 100).toFixed(2)))
    var95.push(-2.8)
    var99.push(-4.2)
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['日收益率', 'VaR 95%', 'VaR 99%']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 100 }, (_, i) => i + 1)
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '日收益率',
        type: 'bar',
        data: returns
      },
      {
        name: 'VaR 95%',
        type: 'line',
        data: var95,
        lineStyle: { color: '#E6A23C' }
      },
      {
        name: 'VaR 99%',
        type: 'line',
        data: var99,
        lineStyle: { color: '#F56C6C' }
      }
    ]
  }

  varChart.setOption(option)
}

const initRollingVolChart = () => {
  if (!rollingVolChartRef.value) return
  rollingVolChart = echarts.init(rollingVolChartRef.value)
  
  const vol20 = []
  const vol60 = []
  let vol = 0.2
  
  for (let i = 0; i < 200; i++) {
    vol += (Math.random() - 0.5) * 0.02
    vol = Math.max(0.1, Math.min(0.4, vol))
    vol20.push(parseFloat((vol * 100).toFixed(1)))
    vol60.push(parseFloat(((vol * 0.9 + 0.02) * 100).toFixed(1)))
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['20日波动率', '60日波动率']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates.slice(-200)
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '20日波动率',
        type: 'line',
        smooth: true,
        data: vol20
      },
      {
        name: '60日波动率',
        type: 'line',
        smooth: true,
        data: vol60,
        lineStyle: { type: 'dashed' }
      }
    ]
  }

  rollingVolChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initDrawdownChart()
    initDistributionChart()
    initVarChart()
    initRollingVolChart()
  })
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    drawdownChart?.resize()
    distributionChart?.resize()
    varChart?.resize()
    rollingVolChart?.resize()
  })
})
</script>

<style scoped>
.risk-analysis-container {
  padding: 20px;
}

.summary-card,
.chart-card,
.detail-card {
  margin-bottom: 20px;
}

.risk-metric {
  display: flex;
  padding: 15px;
  align-items: center;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 15px;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 22px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.metric-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.metric-trend.up {
  color: #67C23A;
}

.metric-trend.down {
  color: #F56C6C;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 350px;
  width: 100%;
}

@media (max-width: 768px) {
  .risk-analysis-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 280px;
  }
}
</style>

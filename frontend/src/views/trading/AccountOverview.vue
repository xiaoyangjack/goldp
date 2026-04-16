<template>
  <div class="account-overview-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="summary-card">
          <template #header>
            <div class="card-header">
              <span>账户总览</span>
              <el-button type="primary" size="small" @click="refreshData">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <el-skeleton v-if="loading" :rows="4" animated />
          <div v-else class="summary-content">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">总资产</div>
                  <div class="stat-value">¥{{ accountInfo.totalAsset.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">可用资金</div>
                  <div class="stat-value">¥{{ accountInfo.availableCash.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">持仓市值</div>
                  <div class="stat-value">¥{{ accountInfo.positionValue.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-label">总盈亏</div>
                  <div :class="['stat-value', accountInfo.totalPnl >= 0 ? 'positive' : 'negative']">
                    {{ accountInfo.totalPnl >= 0 ? '+' : '' }}¥{{ accountInfo.totalPnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>收益曲线</span>
              <el-radio-group v-model="chartPeriod" size="small">
                <el-radio-button label="week">近一周</el-radio-button>
                <el-radio-button label="month">近一月</el-radio-button>
                <el-radio-button label="year">近一年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <el-skeleton v-if="loading" :rows="10" animated />
          <div v-else ref="equityChartRef" class="chart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stats-card">
          <template #header>
            <span>收益统计</span>
          </template>
          <el-skeleton v-if="loading" :rows="8" animated />
          <div v-else class="stats-content">
            <div class="stat-row">
              <span class="stat-label">今日收益</span>
              <span :class="['stat-value', accountInfo.todayPnl >= 0 ? 'positive' : 'negative']">
                {{ accountInfo.todayPnl >= 0 ? '+' : '' }}¥{{ accountInfo.todayPnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">今日收益率</span>
              <span :class="['stat-value', accountInfo.todayReturn >= 0 ? 'positive' : 'negative']">
                {{ accountInfo.todayReturn >= 0 ? '+' : '' }}{{ accountInfo.todayReturn }}%
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">持仓收益率</span>
              <span :class="['stat-value', accountInfo.positionReturn >= 0 ? 'positive' : 'negative']">
                {{ accountInfo.positionReturn >= 0 ? '+' : '' }}{{ accountInfo.positionReturn }}%
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">年化收益率</span>
              <span :class="['stat-value', accountInfo.annualReturn >= 0 ? 'positive' : 'negative']">
                {{ accountInfo.annualReturn >= 0 ? '+' : '' }}{{ accountInfo.annualReturn }}%
              </span>
            </div>
            <div class="stat-row">
              <span class="stat-label">最大回撤</span>
              <span class="stat-value negative">{{ accountInfo.maxDrawdown }}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">夏普比率</span>
              <span class="stat-value">{{ accountInfo.sharpeRatio }}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">胜率</span>
              <span class="stat-value">{{ accountInfo.winRate }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="positions-card">
          <template #header>
            <div class="card-header">
              <span>当前持仓</span>
              <el-button type="primary" size="small">查看全部</el-button>
            </div>
          </template>
          <el-skeleton v-if="loading" :rows="5" animated />
          <el-table v-else :data="positions" stripe style="width: 100%">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="quantity" label="持仓数量" width="120" />
            <el-table-column prop="avgPrice" label="持仓均价" width="120" />
            <el-table-column prop="currentPrice" label="现价" width="100" />
            <el-table-column prop="marketValue" label="市值" width="120">
              <template #default="scope">
                ¥{{ scope.row.marketValue.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
              </template>
            </el-table-column>
            <el-table-column prop="pnl" label="盈亏" width="120">
              <template #default="scope">
                <span :class="scope.row.pnl >= 0 ? 'positive' : 'negative'">
                  {{ scope.row.pnl >= 0 ? '+' : '' }}¥{{ scope.row.pnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="pnlRatio" label="盈亏比例" width="100">
              <template #default="scope">
                <span :class="scope.row.pnlRatio >= 0 ? 'positive' : 'negative'">
                  {{ scope.row.pnlRatio >= 0 ? '+' : '' }}{{ scope.row.pnlRatio }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const chartPeriod = ref('month')
const equityChartRef = ref<HTMLElement>()
const equityChart = ref<echarts.ECharts>()

const accountInfo = reactive({
  totalAsset: 1234567.89,
  availableCash: 456789.12,
  positionValue: 777778.77,
  totalPnl: 123456.78,
  todayPnl: 5678.90,
  todayReturn: 0.46,
  positionReturn: 18.85,
  annualReturn: 25.67,
  maxDrawdown: 12.34,
  sharpeRatio: 1.85,
  winRate: 62.5
})

const positions = ref([
  { code: '600519', name: '贵州茅台', quantity: 100, avgPrice: 1650.00, currentPrice: 1850.00, marketValue: 185000.00, pnl: 20000.00, pnlRatio: 12.12 },
  { code: '000858', name: '五粮液', quantity: 500, avgPrice: 135.00, currentPrice: 156.78, marketValue: 78390.00, pnl: 10890.00, pnlRatio: 16.13 },
  { code: '601318', name: '中国平安', quantity: 2000, avgPrice: 42.00, currentPrice: 45.67, marketValue: 91340.00, pnl: 7340.00, pnlRatio: 8.74 },
  { code: '000001', name: '平安银行', quantity: 5000, avgPrice: 11.00, currentPrice: 12.34, marketValue: 61700.00, pnl: 6700.00, pnlRatio: 12.18 },
  { code: '600036', name: '招商银行', quantity: 3000, avgPrice: 30.00, currentPrice: 32.45, marketValue: 97350.00, pnl: 7350.00, pnlRatio: 8.17 }
])

const initEquityChart = () => {
  if (process.env.NODE_ENV !== 'test' && equityChartRef.value) {
    equityChart.value = echarts.init(equityChartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['账户收益', '沪深300']
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
        data: ['1日', '2日', '3日', '4日', '5日', '6日', '7日', '8日', '9日', '10日']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '账户收益',
          type: 'line',
          smooth: true,
          data: [0, 2.1, 3.5, 5.2, 6.8, 8.5, 9.3, 10.7, 11.2, 12.3],
          lineStyle: {
            color: '#165DFF'
          },
          areaStyle: {
            color: 'rgba(22, 93, 255, 0.1)'
          }
        },
        {
          name: '沪深300',
          type: 'line',
          smooth: true,
          data: [0, 1.2, 2.5, 3.8, 4.5, 5.8, 6.5, 7.2, 7.8, 8.5],
          lineStyle: {
            color: '#67C23A'
          }
        }
      ]
    }
    equityChart.value.setOption(option)
  }
}

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 1000)
}

watch(chartPeriod, () => {
  refreshData()
})

onMounted(() => {
  initEquityChart()
  refreshData()
})
</script>

<style scoped>
.account-overview-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-content {
  padding: 10px 0;
}

.stat-item {
  text-align: center;
  padding: 20px 0;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.chart {
  width: 100%;
  height: 350px;
}

.stats-content {
  padding: 10px 0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #EBEEF5;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row .stat-label {
  color: #606266;
}

.stat-row .stat-value {
  font-size: 16px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .account-overview-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>

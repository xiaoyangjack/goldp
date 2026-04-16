<template>
  <div class="overview-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用 GoldQuant</span>
        </div>
      </template>
      <div class="welcome-content">
        <p>专业级量化投研与交易平台，为A股个人/机构投资者提供一站式量化投研与模拟交易服务。</p>
        <div class="action-buttons">
          <el-button type="primary" size="large" @click="handleGuide">
            <el-icon><Guide /></el-icon>
            新手引导
          </el-button>
          <el-button type="success" size="large" style="margin-left: 10px;" @click="handleQuickStart">
            <el-icon><VideoPlay /></el-icon>
            快速开始
          </el-button>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>账户信息</span>
              <el-button type="primary" size="small" @click="refreshAccountInfo">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="info-content">
            <el-skeleton v-if="loading.account" :rows="4" animated />
            <div v-else class="info-items">
              <div class="info-item">
                <span class="label">总资产</span>
                <span class="value">¥{{ accountInfo.totalAsset.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
              </div>
              <div class="info-item">
                <span class="label">可用资金</span>
                <span class="value">¥{{ accountInfo.availableCash.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
              </div>
              <div class="info-item">
                <span class="label">持仓市值</span>
                <span class="value">¥{{ accountInfo.positionValue.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
              </div>
              <div class="info-item">
                <span class="label">总盈亏</span>
                <span :class="accountInfo.totalPnl >= 0 ? 'value positive' : 'value negative'">
                  {{ accountInfo.totalPnl >= 0 ? '+' : '' }}¥{{ accountInfo.totalPnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>最近回测</span>
              <el-button type="primary" size="small" @click="refreshBacktests">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="info-content">
            <el-skeleton v-if="loading.backtests" :rows="5" animated />
            <el-table v-else :data="recentBacktests" stripe style="width: 100%">
              <el-table-column prop="name" label="策略名称" />
              <el-table-column prop="status" label="状态">
                <template #default="scope">
                  <el-tag :type="scope.row.status === 'completed' ? 'success' : 'info'">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="return" label="收益率">
                <template #default="scope">
                  <span :class="scope.row.return >= 0 ? 'positive' : 'negative'">
                    {{ scope.row.return }}%
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>市场概览</span>
              <el-button type="primary" size="small" @click="refreshMarket">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="info-content">
            <el-skeleton v-if="loading.market" :rows="4" animated />
            <div v-else class="market-items">
              <div class="market-item" v-for="item in marketData" :key="item.name">
                <span class="label">{{ item.name }}</span>
                <div class="market-value">
                  <span>{{ item.value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
                  <span :class="item.change >= 0 ? 'positive' : 'negative'">
                    {{ item.change >= 0 ? '+' : '' }}{{ item.change }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>模拟账户收益曲线</span>
          <el-button type="primary" size="small" @click="refreshEquityCurve">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="chart-content">
        <el-skeleton v-if="loading.equity" :rows="10" animated />
        <div v-else ref="chartRef" class="chart" style="height: 400px;"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Guide, VideoPlay, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { accountApi, backtestApi, marketApi, equityApi } from '../../api'
import { ElMessage } from 'element-plus'

// 响应式数据
const chartRef = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()

// 账户信息
const accountInfo = ref({
  totalAsset: 0,
  availableCash: 0,
  positionValue: 0,
  totalPnl: 0
})

// 最近回测
const recentBacktests = ref([
  { name: '沪深300多因子', status: 'completed', return: 15.2 },
  { name: '中证500动量', status: 'completed', return: 8.7 },
  { name: '行业轮动', status: 'pending', return: 0 }
])

// 市场数据
const marketData = ref([
  { name: '上证指数', value: 3200.00, change: 1.20 },
  { name: '深证成指', value: 12500.00, change: 0.80 },
  { name: '创业板指', value: 2500.00, change: -0.30 },
  { name: '沪深300', value: 4100.00, change: 1.00 }
])

// 加载状态
const loading = reactive({
  account: false,
  backtests: false,
  market: false,
  equity: false
})

// 初始化图表
const initChart = (data?: any) => {
  // 避免在测试环境中初始化ECharts
  if (process.env.NODE_ENV !== 'test' && chartRef.value) {
    chart.value = echarts.init(chartRef.value)
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
        data: data?.months || ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
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
          stack: 'Total',
          data: data?.account || [2.1, 3.5, 5.2, 7.8, 10.5, 12.3, 14.7, 16.2, 18.9, 20.5, 22.3, 25.1],
          smooth: true,
          lineStyle: {
            color: '#165DFF'
          }
        },
        {
          name: '沪深300',
          type: 'line',
          stack: 'Total',
          data: data?.benchmark || [1.2, 2.5, 3.8, 5.1, 6.5, 7.8, 9.2, 10.5, 11.8, 13.2, 14.5, 15.8],
          smooth: true,
          lineStyle: {
            color: '#67C23A'
          }
        }
      ]
    }
    chart.value.setOption(option)
  }
}

// 刷新账户信息
const refreshAccountInfo = async () => {
  loading.account = true
  try {
    const response = await accountApi.getAccountInfo()
    if (response.code === 200) {
      accountInfo.value = response.data
    }
  } catch (error) {
    console.error('Failed to get account info:', error)
    ElMessage.error('获取账户信息失败')
  } finally {
    loading.account = false
  }
}

// 刷新回测数据
const refreshBacktests = async () => {
  loading.backtests = true
  try {
    const response = await backtestApi.getRecentBacktests()
    if (response.code === 200) {
      recentBacktests.value = response.data
    }
  } catch (error) {
    console.error('Failed to get backtests:', error)
    ElMessage.error('获取回测数据失败')
  } finally {
    loading.backtests = false
  }
}

// 刷新市场数据
const refreshMarket = async () => {
  loading.market = true
  try {
    const response = await marketApi.getMarketOverview()
    if (response.code === 200) {
      marketData.value = response.data
    }
  } catch (error) {
    console.error('Failed to get market data:', error)
    ElMessage.error('获取市场数据失败')
  } finally {
    loading.market = false
  }
}

// 刷新收益曲线
const refreshEquityCurve = async () => {
  loading.equity = true
  try {
    const response = await equityApi.getEquityCurve()
    if (response.code === 200) {
      initChart(response.data)
    }
  } catch (error) {
    console.error('Failed to get equity curve:', error)
    ElMessage.error('获取收益曲线失败')
  } finally {
    loading.equity = false
  }
}

// 处理新手引导
const handleGuide = () => {
  ElMessage.info('新手引导功能开发中')
}

// 处理快速开始
const handleQuickStart = () => {
  ElMessage.info('快速开始功能开发中')
}

// 处理窗口 resize
const handleResize = () => {
  chart.value?.resize()
}

// 初始化数据
onMounted(async () => {
  // 并行获取所有数据
  await Promise.all([
    refreshAccountInfo(),
    refreshBacktests(),
    refreshMarket(),
    refreshEquityCurve()
  ])
  
  window.addEventListener('resize', handleResize)
})
</script>



<style scoped>
.overview-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-content {
  padding: 20px 0;
}

.welcome-content p {
  font-size: 16px;
  line-height: 1.5;
  margin-bottom: 20px;
  color: #606266;
}

.action-buttons {
  margin-top: 20px;
}

.info-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-content {
  padding: 10px 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.label {
  color: #606266;
  font-size: 14px;
}

.value {
  font-weight: bold;
  font-size: 16px;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.market-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.market-value {
  display: flex;
  align-items: center;
}

.market-value span {
  margin-left: 10px;
}

.chart-card {
  margin-top: 20px;
}

.chart-content {
  padding: 10px 0;
}

.chart {
  width: 100%;
  height: 400px;
}

@media (max-width: 768px) {
  .overview-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .chart {
    height: 300px;
  }
}
</style>
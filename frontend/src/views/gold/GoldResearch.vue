<template>
  <div class="gold-research-container">
    <el-card class="gold-card">
      <template #header>
        <div class="card-header">
          <span>贵金属研究</span>
          <el-button type="primary" size="small" @click="fetchGoldData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="data-card" shadow="hover">
            <template #header>
              <span>黄金现货价格</span>
            </template>
            <div class="price-display">
              <div class="current-price">
                ¥{{ goldPrice.current }} 
                <span :class="goldPrice.change >= 0 ? 'positive' : 'negative'">
                  {{ goldPrice.change >= 0 ? '+' : '' }}{{ goldPrice.change }} ({{ goldPrice.changePercent }}%)
                </span>
              </div>
              <div class="price-details">
                <span>开盘: ¥{{ goldPrice.open }}</span>
                <span>最高: ¥{{ goldPrice.high }}</span>
                <span>最低: ¥{{ goldPrice.low }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="data-card" shadow="hover">
            <template #header>
              <span>贵金属品种</span>
            </template>
            <el-select v-model="selectedMetal" placeholder="选择贵金属" style="width: 100%" @change="fetchMetalData">
              <el-option v-for="metal in metalTypes" :key="metal.code" :label="metal.name" :value="metal.code" />
            </el-select>
            <div class="metal-info" v-if="selectedMetalInfo">
              <div class="info-item">
                <span class="label">当前价格:</span>
                <span class="value">¥{{ selectedMetalInfo.price }}</span>
              </div>
              <div class="info-item">
                <span class="label">涨跌幅:</span>
                <span :class="selectedMetalInfo.change >= 0 ? 'positive' : 'negative'">
                  {{ selectedMetalInfo.change >= 0 ? '+' : '' }}{{ selectedMetalInfo.change }}%
                </span>
              </div>
              <div class="info-item">
                <span class="label">更新时间:</span>
                <span class="value">{{ selectedMetalInfo.updateTime }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="chart-card" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>黄金价格走势</span>
            <el-select v-model="timeRange" style="width: 120px" @change="fetchGoldData">
              <el-option label="1周" value="7d" />
              <el-option label="1月" value="30d" />
              <el-option label="3月" value="90d" />
              <el-option label="1年" value="365d" />
            </el-select>
          </div>
        </template>
        <div class="chart-content">
          <el-skeleton v-if="loading" :rows="10" animated />
          <div v-else ref="chartRef" class="chart" style="height: 400px;"></div>
        </div>
      </el-card>
      
      <el-card class="analysis-card" style="margin-top: 20px;">
        <template #header>
          <span>贵金属分析</span>
        </template>
        <el-tabs v-model="activeAnalysisTab">
          <el-tab-pane label="技术指标">
            <el-table :data="technicalIndicators" stripe style="width: 100%">
              <el-table-column prop="name" label="指标名称" />
              <el-table-column prop="value" label="指标值" />
              <el-table-column prop="signal" label="信号">
                <template #default="scope">
                  <el-tag :type="scope.row.signal === '买入' ? 'success' : scope.row.signal === '卖出' ? 'danger' : 'info'>
                    {{ scope.row.signal }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="基本面分析">
            <div class="fundamental-analysis">
              <el-card shadow="hover" style="margin-bottom: 15px;">
                <template #header>
                  <span>宏观经济指标</span>
                </template>
                <el-table :data="macroIndicators" stripe style="width: 100%">
                  <el-table-column prop="name" label="指标" />
                  <el-table-column prop="value" label="当前值" />
                  <el-table-column prop="impact" label="影响">
                    <template #default="scope">
                      <el-tag :type="scope.row.impact === '正面' ? 'success' : 'danger'>
                        {{ scope.row.impact }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
              <el-card shadow="hover">
                <template #header>
                  <span>市场情绪</span>
                </template>
                <div class="sentiment-analysis">
                  <div class="sentiment-item">
                    <span class="label">恐惧贪婪指数:</span>
                    <div class="sentiment-bar">
                      <div class="sentiment-fill" :style="{ width: sentimentIndex.score + '%' }" :class="sentimentIndex.type"></div>
                    </div>
                    <span class="value">{{ sentimentIndex.type }}</span>
                  </div>
                  <div class="sentiment-item">
                    <span class="label">市场趋势:</span>
                    <span class="value">{{ marketTrend }}</span>
                  </div>
                </div>
              </el-card>
            </div>
          </el-tab-pane>
          <el-tab-pane label="关联市场">
            <el-table :data="relatedMarkets" stripe style="width: 100%">
              <el-table-column prop="name" label="市场" />
              <el-table-column prop="value" label="当前值" />
              <el-table-column prop="change" label="涨跌幅">
                <template #default="scope">
                  <span :class="scope.row.change >= 0 ? 'positive' : 'negative'">
                    {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="correlation" label="与黄金相关性">
                <template #default="scope">
                  <span :class="Math.abs(scope.row.correlation) > 0.7 ? 'strong' : 'weak'">
                    {{ scope.row.correlation.toFixed(2) }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
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
const chartRef = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()
const loading = ref(false)
const timeRange = ref('30d')
const selectedMetal = ref('AU9999')
const activeAnalysisTab = ref('0')

// 贵金属类型
const metalTypes = ref([
  { code: 'AU9999', name: '黄金9999' },
  { code: 'AU9995', name: '黄金9995' },
  { code: 'AG9999', name: '白银9999' },
  { code: 'PT9995', name: '铂金9995' },
  { code: 'PD9995', name: '钯金9995' }
])

// 黄金价格数据
const goldPrice = ref({
  current: 0,
  open: 0,
  high: 0,
  low: 0,
  change: 0,
  changePercent: 0
})

// 选中的贵金属信息
const selectedMetalInfo = ref<any>(null)

// 技术指标
const technicalIndicators = ref([
  { name: 'MA5', value: '0', signal: '中性' },
  { name: 'MA20', value: '0', signal: '中性' },
  { name: 'MA60', value: '0', signal: '中性' },
  { name: 'MACD', value: '0', signal: '中性' },
  { name: 'KDJ', value: '0,0,0', signal: '中性' },
  { name: 'RSI', value: '0', signal: '中性' },
  { name: 'ATR', value: '0', signal: '中性' }
])

// 宏观经济指标
const macroIndicators = ref([
  { name: '美元指数', value: '102.5', impact: '负面' },
  { name: '10年期美债收益率', value: '4.2%', impact: '负面' },
  { name: '通胀率', value: '2.8%', impact: '正面' },
  { name: 'GDP增长率', value: '2.1%', impact: '正面' }
])

// 市场情绪
const sentimentIndex = ref({
  score: 65,
  type: '贪婪'
})

const marketTrend = ref('震荡上行')

// 关联市场
const relatedMarkets = ref([
  { name: '美元指数', value: '102.5', change: -0.2, correlation: -0.75 },
  { name: '原油', value: '78.5', change: 0.5, correlation: 0.65 },
  { name: '白银', value: '22.5', change: 1.2, correlation: 0.92 },
  { name: '铂金', value: '920', change: 0.8, correlation: 0.85 },
  { name: '钯金', value: '1450', change: -0.3, correlation: 0.78 }
])

// 初始化图表
const initChart = (data?: any) => {
  if (chartRef.value) {
    chart.value = echarts.init(chartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis',
        formatter: function(params: any) {
          return `${params[0].name}<br/>价格: ¥${params[0].value}`
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
        boundaryGap: false,
        data: data?.dates || []
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '¥{value}'
        }
      },
      series: [{
        name: '黄金价格',
        type: 'line',
        data: data?.prices || [],
        smooth: true,
        lineStyle: {
          color: '#FFD700'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 215, 0, 0.3)' },
            { offset: 1, color: 'rgba(255, 215, 0, 0.1)' }
          ])
        }
      }]
    }
    chart.value.setOption(option)
  }
}

// 获取黄金数据
const fetchGoldData = async () => {
  loading.value = true
  try {
    // 获取当前价格
    const priceResponse = await goldApi.getGoldPrices()
    if (priceResponse.code === 200) {
      goldPrice.value = {
        current: priceResponse.data.currentPrice,
        open: priceResponse.data.openPrice,
        high: priceResponse.data.highPrice,
        low: priceResponse.data.lowPrice,
        change: priceResponse.data.change,
        changePercent: priceResponse.data.changePercent
      }
    }
    
    // 获取价格历史
    const historyResponse = await goldApi.getGoldPriceHistory(timeRange.value)
    if (historyResponse.code === 200) {
      initChart(historyResponse.data)
    }
  } catch (error) {
    console.error('Failed to get gold data:', error)
    ElMessage.error('获取黄金数据失败')
  } finally {
    loading.value = false
  }
}

// 获取贵金属数据
const fetchMetalData = async () => {
  // 模拟数据，实际项目中应该调用真实API
  selectedMetalInfo.value = {
    price: 2023.50 + Math.random() * 100,
    change: (Math.random() - 0.5) * 2,
    updateTime: new Date().toLocaleString()
  }
}

// 处理窗口resize
const handleResize = () => {
  chart.value?.resize()
}

// 初始化
onMounted(async () => {
  await fetchGoldData()
  await fetchMetalData()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.gold-research-container {
  padding: 20px;
}

.gold-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-card {
  height: 100%;
}

.price-display {
  padding: 20px 0;
}

.current-price {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.price-details {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}

.metal-info {
  margin-top: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.label {
  color: #606266;
}

.value {
  font-weight: bold;
}

.chart-content {
  padding: 10px 0;
}

.chart {
  width: 100%;
  height: 400px;
}

.analysis-card {
  margin-top: 20px;
}

.fundamental-analysis {
  margin-top: 20px;
}

.sentiment-analysis {
  padding: 20px 0;
}

.sentiment-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 15px;
}

.sentiment-bar {
  flex: 1;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.sentiment-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.sentiment-fill.恐惧 {
  background-color: #F56C6C;
}

.sentiment-fill.中性 {
  background-color: #E6A23C;
}

.sentiment-fill.贪婪 {
  background-color: #67C23A;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.strong {
  color: #165DFF;
  font-weight: bold;
}

.weak {
  color: #909399;
}

@media (max-width: 768px) {
  .gold-research-container {
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

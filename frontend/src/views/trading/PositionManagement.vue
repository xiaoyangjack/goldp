<template>
  <div class="position-management-container">
    <el-card class="summary-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">总市值</div>
            <div class="summary-value">¥{{ totalMarketValue.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">总盈亏</div>
            <div class="summary-value" :class="totalPnL >= 0 ? 'profit' : 'loss'">
              {{ totalPnL >= 0 ? '+' : '' }}¥{{ totalPnL.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">持仓盈亏</div>
            <div class="summary-value" :class="unrealizedPnL >= 0 ? 'profit' : 'loss'">
              {{ unrealizedPnL >= 0 ? '+' : '' }}¥{{ unrealizedPnL.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">持仓数量</div>
            <div class="summary-value">{{ positions.length }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="positions-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>持仓列表</span>
          <el-button-group>
            <el-button type="primary" size="small" @click="refreshPositions">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="success" size="small" @click="exportPositions">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </el-button-group>
        </div>
      </template>
      
      <el-table :data="positions" stripe style="width: 100%" @row-click="showPositionDetail">
        <el-table-column type="expand">
          <template #default="{ row }">
            <el-form label-position="top" class="position-detail">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="开仓时间">
                    <span>{{ row.openTime }}</span>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="开仓价格">
                    <span>¥{{ row.openPrice.toFixed(2) }}</span>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="持仓天数">
                    <span>{{ row.holdDays }}天</span>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </template>
        </el-table-column>
        <el-table-column prop="symbol" label="标的" width="120">
          <template #default="{ row }">
            <div class="symbol-info">
              <div class="symbol-name">{{ row.symbol }}</div>
              <div class="symbol-label">{{ row.name }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="direction" label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.direction === '多' ? 'success' : 'danger'" size="small">
              {{ row.direction }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="持仓数量" width="120" sortable />
        <el-table-column prop="available" label="可用数量" width="120" sortable />
        <el-table-column prop="openPrice" label="开仓价" width="120" sortable />
        <el-table-column prop="currentPrice" label="当前价" width="120" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.priceChange >= 0 ? '#67C23A' : '#F56C6C' }">
              {{ row.currentPrice.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="marketValue" label="市值" width="140" sortable>
          <template #default="{ row }">
            ¥{{ row.marketValue.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
          </template>
        </el-table-column>
        <el-table-column prop="unrealizedPnL" label="持仓盈亏" width="140" sortable>
          <template #default="{ row }">
            <span :class="row.unrealizedPnL >= 0 ? 'profit' : 'loss'">
              {{ row.unrealizedPnL >= 0 ? '+' : '' }}¥{{ row.unrealizedPnL.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="unrealizedPnLPercent" label="盈亏%" width="100" sortable>
          <template #default="{ row }">
            <el-progress
              :percentage="Math.abs(row.unrealizedPnLPercent)"
              :color="row.unrealizedPnLPercent >= 0 ? '#67C23A' : '#F56C6C'"
              :stroke-width="10"
              :format="() => `${row.unrealizedPnLPercent >= 0 ? '+' : ''}${row.unrealizedPnLPercent.toFixed(2)}%`"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click.stop="openOrderDialog(scope.row, 'close')">平仓</el-button>
            <el-button type="success" size="small" @click.stop="openOrderDialog(scope.row, 'add')">加仓</el-button>
            <el-button type="warning" size="small" @click.stop="setStopLoss(scope.row)">止损</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>持仓分布</span>
          </template>
          <div ref="distributionChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>盈亏概览</span>
          </template>
          <div ref="pnlChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="orderDialogVisible" :title="orderDialogType === 'close' ? '平仓' : '加仓'" width="500px">
      <el-form :model="orderForm" label-width="100px">
        <el-form-item label="标的">
          <span>{{ selectedPosition?.symbol }}</span>
        </el-form-item>
        <el-form-item label="当前持仓">
          <span>{{ selectedPosition?.quantity }}</span>
        </el-form-item>
        <el-form-item label="数量" v-if="orderDialogType === 'add'">
          <el-input-number v-model="orderForm.quantity" :min="1" :max="selectedPosition?.quantity || 10000" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="数量" v-else>
          <el-radio-group v-model="orderForm.closeType">
            <el-radio-button value="all">全部平仓</el-radio-button>
            <el-radio-button value="part">部分平仓</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="平仓数量" v-if="orderDialogType === 'close' && orderForm.closeType === 'part'">
          <el-input-number v-model="orderForm.quantity" :min="1" :max="selectedPosition?.quantity || 0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="价格类型">
          <el-radio-group v-model="orderForm.priceType">
            <el-radio-button value="market">市价</el-radio-button>
            <el-radio-button value="limit">限价</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="限价" v-if="orderForm.priceType === 'limit'">
          <el-input-number v-model="orderForm.price" :precision="2" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="stopLossDialogVisible" title="设置止损止盈" width="500px">
      <el-form :model="stopLossForm" label-width="120px">
        <el-form-item label="止损价格">
          <el-input-number v-model="stopLossForm.stopLossPrice" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="止损比例(%)">
          <el-input-number v-model="stopLossForm.stopLossPercent" :min="0" :max="50" :precision="1" style="width: 100%;" />
        </el-form-item>
        <el-divider />
        <el-form-item label="止盈价格">
          <el-input-number v-model="stopLossForm.takeProfitPrice" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="止盈比例(%)">
          <el-input-number v-model="stopLossForm.takeProfitPercent" :min="0" :max="100" :precision="1" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stopLossDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStopLoss">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { Refresh, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const orderDialogVisible = ref(false)
const stopLossDialogVisible = ref(false)
const orderDialogType = ref<'close' | 'add'>('close')
const selectedPosition = ref<any>(null)

const distributionChartRef = ref<HTMLElement>()
const pnlChartRef = ref<HTMLElement>()
let distributionChart: echarts.ECharts | null = null
let pnlChart: echarts.ECharts | null = null

const positions = ref([
  {
    symbol: 'AU.SHF',
    name: '黄金主力',
    direction: '多',
    quantity: 100,
    available: 100,
    openPrice: 200.50,
    currentPrice: 205.80,
    priceChange: 5.30,
    marketValue: 20580,
    unrealizedPnL: 530,
    unrealizedPnLPercent: 2.64,
    openTime: '2024-04-10 09:30:00',
    holdDays: 5
  },
  {
    symbol: 'AG.SHF',
    name: '白银主力',
    direction: '空',
    quantity: 50,
    available: 50,
    openPrice: 5800,
    currentPrice: 5680,
    priceChange: -120,
    marketValue: 284000,
    unrealizedPnL: 6000,
    unrealizedPnLPercent: 2.07,
    openTime: '2024-04-08 14:00:00',
    holdDays: 7
  },
  {
    symbol: 'CU.SHF',
    name: '铜主力',
    direction: '多',
    quantity: 30,
    available: 30,
    openPrice: 72000,
    currentPrice: 71500,
    priceChange: -500,
    marketValue: 2145000,
    unrealizedPnL: -15000,
    unrealizedPnLPercent: -0.69,
    openTime: '2024-04-05 10:15:00',
    holdDays: 10
  }
])

const orderForm = ref({
  quantity: 100,
  closeType: 'all',
  priceType: 'market',
  price: 0
})

const stopLossForm = ref({
  stopLossPrice: 0,
  stopLossPercent: 5,
  takeProfitPrice: 0,
  takeProfitPercent: 10
})

const totalMarketValue = computed(() => {
  return positions.value.reduce((sum, pos) => sum + pos.marketValue, 0)
})

const totalPnL = computed(() => {
  return positions.value.reduce((sum, pos) => sum + pos.unrealizedPnL, 0)
})

const unrealizedPnL = computed(() => {
  return totalPnL.value
})

const refreshPositions = () => {
  ElMessage.success('持仓已刷新')
}

const exportPositions = () => {
  ElMessage.success('持仓导出成功')
}

const showPositionDetail = (row: any) => {
  console.log('查看持仓详情:', row)
}

const openOrderDialog = (position: any, type: 'close' | 'add') => {
  selectedPosition.value = position
  orderDialogType.value = type
  orderForm.value = {
    quantity: type === 'close' ? position.quantity : 100,
    closeType: 'all',
    priceType: 'market',
    price: position.currentPrice
  }
  orderDialogVisible.value = true
}

const submitOrder = () => {
  ElMessage.success(orderDialogType.value === 'close' ? '平仓委托已提交' : '加仓委托已提交')
  orderDialogVisible.value = false
}

const setStopLoss = (position: any) => {
  selectedPosition.value = position
  stopLossForm.value = {
    stopLossPrice: position.currentPrice * 0.95,
    stopLossPercent: 5,
    takeProfitPrice: position.currentPrice * 1.1,
    takeProfitPercent: 10
  }
  stopLossDialogVisible.value = true
}

const saveStopLoss = () => {
  ElMessage.success('止损止盈设置成功')
  stopLossDialogVisible.value = false
}

const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  distributionChart = echarts.init(distributionChartRef.value)
  
  const data = positions.value.map(pos => ({
    value: pos.marketValue,
    name: pos.symbol
  }))

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
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

  distributionChart.setOption(option)
}

const initPnLChart = () => {
  if (!pnlChartRef.value) return
  pnlChart = echarts.init(pnlChartRef.value)
  
  const symbols = positions.value.map(pos => pos.symbol)
  const pnlValues = positions.value.map(pos => pos.unrealizedPnL)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => `${params[0].name}<br/>盈亏: ¥${params[0].value.toLocaleString('zh-CN')}`
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: symbols
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [{
      type: 'bar',
      data: pnlValues.map((val, idx) => ({
        value: val,
        itemStyle: {
          color: val >= 0 ? '#67C23A' : '#F56C6C'
        }
      }))
    }]
  }

  pnlChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initDistributionChart()
    initPnLChart()
  })
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    distributionChart?.resize()
    pnlChart?.resize()
  })
})
</script>

<style scoped>
.position-management-container {
  padding: 20px;
}

.summary-card,
.positions-card,
.chart-card {
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 10px;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.summary-value.profit {
  color: #67C23A;
}

.summary-value.loss {
  color: #F56C6C;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.symbol-info {
  display: flex;
  flex-direction: column;
}

.symbol-name {
  font-weight: bold;
  color: #303133;
}

.symbol-label {
  font-size: 12px;
  color: #909399;
}

.position-detail {
  padding: 20px;
  background: #f5f7fa;
}

.profit {
  color: #67C23A;
}

.loss {
  color: #F56C6C;
}

.chart-container {
  height: 300px;
  width: 100%;
}

@media (max-width: 768px) {
  .position-management-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>

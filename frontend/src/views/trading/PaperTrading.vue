<template>
  <div class="paper-trading-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="account-card">
          <template #header>
            <div class="card-header">
              <span>账户信息</span>
              <el-button type="primary" size="small" @click="fetchTradingAccount">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          <div class="account-content">
            <el-skeleton v-if="loading.account" :rows="4" animated />
            <div v-else class="account-items">
              <div class="account-item">
                <span class="label">总资产</span>
                <span class="value">¥{{ tradingAccount.totalAsset.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
              </div>
              <div class="account-item">
                <span class="label">可用资金</span>
                <span class="value">¥{{ tradingAccount.availableCash.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
              </div>
              <div class="account-item">
                <span class="label">持仓市值</span>
                <span class="value">¥{{ tradingAccount.positionValue.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
              </div>
              <div class="account-item">
                <span class="label">总盈亏</span>
                <span :class="tradingAccount.totalPnl >= 0 ? 'value positive' : 'value negative'">
                  {{ tradingAccount.totalPnl >= 0 ? '+' : '' }}¥{{ tradingAccount.totalPnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </span>
              </div>
              <div class="account-item">
                <span class="label">今日盈亏</span>
                <span :class="tradingAccount.todayPnl >= 0 ? 'value positive' : 'value negative'">
                  {{ tradingAccount.todayPnl >= 0 ? '+' : '' }}¥{{ tradingAccount.todayPnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card class="order-card">
          <template #header>
            <span>下单</span>
          </template>
          <div class="order-content">
            <el-form :model="orderForm" class="order-form">
              <el-form-item label="股票代码">
                <el-input v-model="orderForm.symbol" placeholder="请输入股票代码" />
              </el-form-item>
              <el-form-item label="交易方向">
                <el-radio-group v-model="orderForm.direction">
                  <el-radio label="buy">买入</el-radio>
                  <el-radio label="sell">卖出</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="订单类型">
                <el-radio-group v-model="orderForm.type">
                  <el-radio label="limit">限价单</el-radio>
                  <el-radio label="market">市价单</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="价格">
                <el-input v-model="orderForm.price" type="number" placeholder="请输入价格" />
              </el-form-item>
              <el-form-item label="数量">
                <el-input v-model="orderForm.quantity" type="number" placeholder="请输入数量" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="placeOrder" :loading="loading.order">提交订单</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="positions-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>持仓</span>
          <el-button type="primary" size="small" @click="fetchPositions">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="positions-content">
        <el-skeleton v-if="loading.positions" :rows="10" animated />
        <el-table v-else :data="positions" stripe style="width: 100%">
          <el-table-column prop="symbol" label="股票代码" />
          <el-table-column prop="name" label="股票名称" />
          <el-table-column prop="quantity" label="持仓数量" />
          <el-table-column prop="costPrice" label="成本价" />
          <el-table-column prop="currentPrice" label="当前价" />
          <el-table-column prop="marketValue" label="市值" />
          <el-table-column prop="unrealizedPnl" label="浮动盈亏">
            <template #default="scope">
              <span :class="scope.row.unrealizedPnl >= 0 ? 'positive' : 'negative'">
                {{ scope.row.unrealizedPnl >= 0 ? '+' : '' }}¥{{ scope.row.unrealizedPnl.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="primary" size="small" @click="sellStock(scope.row)">
                卖出
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { tradingApi } from '../../api'
import { ElMessage } from 'element-plus'

// 交易账户信息
const tradingAccount = ref({
  totalAsset: 0,
  availableCash: 0,
  positionValue: 0,
  totalPnl: 0,
  todayPnl: 0
})

// 持仓信息
const positions = ref([])

// 下单表单
const orderForm = reactive({
  symbol: '600000',
  direction: 'buy',
  type: 'limit',
  price: 9.2,
  quantity: 1000
})

// 加载状态
const loading = reactive({
  account: false,
  positions: false,
  order: false
})

// 获取交易账户信息
const fetchTradingAccount = async () => {
  loading.account = true
  try {
    const response = await tradingApi.getTradingAccount()
    if (response.code === 200) {
      tradingAccount.value = response.data
    }
  } catch (error) {
    console.error('Failed to get trading account:', error)
    ElMessage.error('获取交易账户信息失败')
  } finally {
    loading.account = false
  }
}

// 获取持仓信息
const fetchPositions = async () => {
  loading.positions = true
  try {
    const response = await tradingApi.getPositions()
    if (response.code === 200) {
      positions.value = response.data
    }
  } catch (error) {
    console.error('Failed to get positions:', error)
    ElMessage.error('获取持仓信息失败')
  } finally {
    loading.positions = false
  }
}

// 下单
const placeOrder = async () => {
  loading.order = true
  try {
    const response = await tradingApi.placeOrder(orderForm)
    if (response.code === 200) {
      ElMessage.success('下单成功')
      // 刷新账户和持仓信息
      await Promise.all([
        fetchTradingAccount(),
        fetchPositions()
      ])
    }
  } catch (error) {
    console.error('Failed to place order:', error)
    ElMessage.error('下单失败')
  } finally {
    loading.order = false
  }
}

// 卖出股票
const sellStock = (stock: any) => {
  orderForm.symbol = stock.symbol
  orderForm.direction = 'sell'
  orderForm.price = stock.currentPrice
  orderForm.quantity = stock.availableQuantity
}

// 初始化数据
fetchTradingAccount()
fetchPositions()
</script>

<style scoped>
.paper-trading-container {
  padding: 20px;
}

.account-card,
.order-card,
.positions-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.account-content,
.order-content,
.positions-content {
  margin-top: 20px;
}

.account-item {
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

.order-form .el-form-item {
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .paper-trading-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
}
</style>
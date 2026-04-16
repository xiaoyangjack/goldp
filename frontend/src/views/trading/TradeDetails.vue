<template>
  <div class="trade-details-container">
    <el-card class="filter-card">
      <el-form :model="filterForm" inline label-width="100px">
        <el-form-item label="标的代码">
          <el-input v-model="filterForm.symbol" placeholder="请输入标的代码" clearable style="width: 150px;" />
        </el-form-item>
        <el-form-item label="成交方向">
          <el-select v-model="filterForm.direction" placeholder="全部" clearable style="width: 120px;">
            <el-option label="全部" value="" />
            <el-option label="买入" value="buy" />
            <el-option label="卖出" value="sell" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="filterForm.startDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 150px;"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="filterForm.endDate"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 150px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchTrades">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="stats-card" style="margin-top: 20px;">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总成交笔数</div>
            <div class="stat-value">{{ stats.totalTrades }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总成交金额</div>
            <div class="stat-value">¥{{ stats.totalAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">买入笔数</div>
            <div class="stat-value buy">{{ stats.buyTrades }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">卖出笔数</div>
            <div class="stat-value sell">{{ stats.sellTrades }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="trades-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>成交明细</span>
          <el-button-group>
            <el-button type="primary" size="small" @click="refreshTrades">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="success" size="small" @click="exportTrades">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </el-button-group>
        </div>
      </template>

      <el-table :data="tradeDetails" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="tradeId" label="成交编号" width="180" fixed />
        <el-table-column prop="orderId" label="委托单号" width="180" />
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
            <el-tag :type="row.direction === 'buy' ? 'success' : 'danger'" size="small">
              {{ row.direction === 'buy' ? '买入' : '卖出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="成交价" width="120" sortable>
          <template #default="{ row }">
            ¥{{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="成交数量" width="120" sortable />
        <el-table-column prop="amount" label="成交金额" width="150" sortable>
          <template #default="{ row }">
            ¥{{ row.amount.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
          </template>
        </el-table-column>
        <el-table-column prop="commission" label="手续费" width="120">
          <template #default="{ row }">
            ¥{{ row.commission.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stampDuty" label="印花税" width="120">
          <template #default="{ row }">
            ¥{{ row.stampDuty.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="transferFee" label="过户费" width="120">
          <template #default="{ row }">
            ¥{{ row.transferFee.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="netAmount" label="净金额" width="150">
          <template #default="{ row }">
            ¥{{ row.netAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
          </template>
        </el-table-column>
        <el-table-column prop="tradeTime" label="成交时间" width="180" sortable />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewTradeDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="detailDialogVisible"
      title="成交详情"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="currentTrade">
        <el-descriptions-item label="成交编号" :span="2">{{ currentTrade.tradeId }}</el-descriptions-item>
        <el-descriptions-item label="委托单号" :span="2">{{ currentTrade.orderId }}</el-descriptions-item>
        <el-descriptions-item label="标的代码">{{ currentTrade.symbol }}</el-descriptions-item>
        <el-descriptions-item label="标的名称">{{ currentTrade.name }}</el-descriptions-item>
        <el-descriptions-item label="成交方向">
          <el-tag :type="currentTrade.direction === 'buy' ? 'success' : 'danger'">
            {{ currentTrade.direction === 'buy' ? '买入' : '卖出' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="成交价格">¥{{ currentTrade.price.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="成交数量">{{ currentTrade.quantity }}</el-descriptions-item>
        <el-descriptions-item label="成交金额">¥{{ currentTrade.amount.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</el-descriptions-item>
        <el-descriptions-item label="手续费">¥{{ currentTrade.commission.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="印花税">¥{{ currentTrade.stampDuty.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="过户费">¥{{ currentTrade.transferFee.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="净金额">¥{{ currentTrade.netAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</el-descriptions-item>
        <el-descriptions-item label="成交时间" :span="2">{{ currentTrade.tradeTime }}</el-descriptions-item>
        <el-descriptions-item label="结算时间" :span="2">{{ currentTrade.settlementTime }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const detailDialogVisible = ref(false)
const currentTrade = ref<any>(null)

const filterForm = reactive({
  symbol: '',
  direction: '',
  startDate: '',
  endDate: ''
})

const stats = reactive({
  totalTrades: 328,
  totalAmount: 2568450.75,
  buyTrades: 175,
  sellTrades: 153
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 328
})

const tradeDetails = ref([
  {
    tradeId: 'TRD2024011500001',
    orderId: 'ORD2024011500001',
    symbol: '600519',
    name: '贵州茅台',
    direction: 'buy',
    price: 1850.00,
    quantity: 100,
    amount: 185000.00,
    commission: 92.50,
    stampDuty: 0.00,
    transferFee: 1.00,
    netAmount: 185093.50,
    tradeTime: '2024-01-15 09:30:22',
    settlementTime: '2024-01-15 16:00:00'
  },
  {
    tradeId: 'TRD2024011500002',
    orderId: 'ORD2024011500002',
    symbol: '000001',
    name: '平安银行',
    direction: 'sell',
    price: 11.75,
    quantity: 500,
    amount: 5875.00,
    commission: 2.94,
    stampDuty: 5.88,
    transferFee: 0.50,
    netAmount: 5865.68,
    tradeTime: '2024-01-15 09:35:43',
    settlementTime: '2024-01-15 16:00:00'
  },
  {
    tradeId: 'TRD2024011500003',
    orderId: 'ORD2024011500003',
    symbol: '601318',
    name: '中国平安',
    direction: 'buy',
    price: 45.50,
    quantity: 80,
    amount: 3640.00,
    commission: 1.82,
    stampDuty: 0.00,
    transferFee: 0.80,
    netAmount: 3642.62,
    tradeTime: '2024-01-15 10:15:35',
    settlementTime: '2024-01-15 16:00:00'
  },
  {
    tradeId: 'TRD2024011400001',
    orderId: 'ORD2024011400001',
    symbol: '000858',
    name: '五粮液',
    direction: 'sell',
    price: 162.50,
    quantity: 200,
    amount: 32500.00,
    commission: 16.25,
    stampDuty: 32.50,
    transferFee: 2.00,
    netAmount: 32449.25,
    tradeTime: '2024-01-14 14:22:18',
    settlementTime: '2024-01-14 16:00:00'
  },
  {
    tradeId: 'TRD2024011400002',
    orderId: 'ORD2024011400002',
    symbol: '600036',
    name: '招商银行',
    direction: 'buy',
    price: 34.80,
    quantity: 500,
    amount: 17400.00,
    commission: 8.70,
    stampDuty: 0.00,
    transferFee: 5.00,
    netAmount: 17413.70,
    tradeTime: '2024-01-14 10:08:45',
    settlementTime: '2024-01-14 16:00:00'
  }
])

const searchTrades = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('查询完成')
  }, 500)
}

const resetFilter = () => {
  Object.assign(filterForm, {
    symbol: '',
    direction: '',
    startDate: '',
    endDate: ''
  })
  ElMessage.info('筛选条件已重置')
}

const refreshTrades = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 500)
}

const exportTrades = () => {
  ElMessage.success('导出成功')
}

const viewTradeDetail = (row: any) => {
  currentTrade.value = row
  detailDialogVisible.value = true
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

onMounted(() => {
})
</script>

<style scoped>
.trade-details-container {
  padding: 20px;
}

.filter-card,
.stats-card,
.trades-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  text-align: center;
  padding: 15px;
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

.stat-value.buy {
  color: #67C23A;
}

.stat-value.sell {
  color: #F56C6C;
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

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .trade-details-container {
    padding: 10px;
  }
}
</style>

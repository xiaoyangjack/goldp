<template>
  <div class="settlement-sheet-container">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>筛选条件</span>
          <el-button type="primary" size="small" @click="handleReset">
            重置
          </el-button>
        </div>
      </template>
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="日期范围">
          <el-date-picker v-model="filterForm.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" />
        </el-form-item>
        <el-form-item label="合约代码">
          <el-input v-model="filterForm.symbol" placeholder="请输入合约代码" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item label="交易方向">
          <el-select v-model="filterForm.direction" placeholder="请选择" clearable>
            <el-option label="全部" value="" />
            <el-option label="做多" value="long" />
            <el-option label="做空" value="short" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="stat-card" style="margin-top: 20px;">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总成交笔数</div>
            <div class="stat-value">{{ totalTrades }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总成交金额</div>
            <div class="stat-value">¥{{ totalAmount.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总手续费</div>
            <div class="stat-value">¥{{ totalCommission.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">净盈亏</div>
            <div class="stat-value" :class="{ 'profit': totalPnL >= 0, 'loss': totalPnL < 0 }">
              ¥{{ totalPnL >= 0 ? '+' : '' }}{{ totalPnL.toLocaleString() }}
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="list-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>交割单明细</span>
          <el-button type="success" size="small" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出交割单
          </el-button>
        </div>
      </template>
      <el-skeleton v-if="loading" :rows="10" animated />
      <el-table v-else :data="settlementList" stripe style="width: 100%">
        <el-table-column prop="settlementId" label="交割单号" width="150" />
        <el-table-column prop="tradeDate" label="交易日期" width="120" />
        <el-table-column prop="symbol" label="合约代码" width="120" />
        <el-table-column prop="direction" label="交易方向" width="100">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'long' ? 'success' : 'danger'">
              {{ row.direction === 'long' ? '做多' : '做空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="成交数量" width="100" sortable />
        <el-table-column prop="price" label="成交价格" width="120" sortable />
        <el-table-column prop="amount" label="成交金额" width="140" sortable>
          <template #default="{ row }">
            ¥{{ row.amount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="commission" label="手续费" width="100">
          <template #default="{ row }">
            ¥{{ row.commission.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="pnl" label="盈亏" width="120" sortable>
          <template #default="{ row }">
            <span :class="{ 'profit': row.pnl >= 0, 'loss': row.pnl < 0 }">
              ¥{{ row.pnl >= 0 ? '+' : '' }}{{ row.pnl.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" style="margin-top: 20px; justify-content: center;" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface Settlement {
  settlementId: string
  tradeDate: string
  symbol: string
  direction: string
  quantity: number
  price: number
  amount: number
  commission: number
  pnl: number
}

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filterForm = ref({
  dateRange: null as [Date, Date] | null,
  symbol: '',
  direction: ''
})

const mockSettlements: Settlement[] = [
  { settlementId: 'ST20240401001', tradeDate: '2024-04-01', symbol: 'AU.SHF', direction: 'long', quantity: 10, price: 725.5, amount: 72550, commission: 21.77, pnl: 1250 },
  { settlementId: 'ST20240401002', tradeDate: '2024-04-01', symbol: 'AG.SHF', direction: 'short', quantity: 50, price: 5680, amount: 284000, commission: 85.2, pnl: -3500 },
  { settlementId: 'ST20240402001', tradeDate: '2024-04-02', symbol: 'CU.SHF', direction: 'long', quantity: 5, price: 68900, amount: 344500, commission: 103.35, pnl: 8900 },
  { settlementId: 'ST20240402002', tradeDate: '2024-04-02', symbol: 'AU.SHF', direction: 'short', quantity: 8, price: 732.2, amount: 58576, commission: 17.57, pnl: -680 },
  { settlementId: 'ST20240403001', tradeDate: '2024-04-03', symbol: 'RU.SHF', direction: 'long', quantity: 10, price: 12850, amount: 128500, commission: 38.55, pnl: 2400 },
  { settlementId: 'ST20240403002', tradeDate: '2024-04-03', symbol: 'AG.SHF', direction: 'long', quantity: 30, price: 5720, amount: 171600, commission: 51.48, pnl: 1800 },
  { settlementId: 'ST20240404001', tradeDate: '2024-04-04', symbol: 'AU.SHF', direction: 'long', quantity: 15, price: 728.8, amount: 109320, commission: 32.8, pnl: 3200 },
  { settlementId: 'ST20240404002', tradeDate: '2024-04-04', symbol: 'CU.SHF', direction: 'short', quantity: 3, price: 69500, amount: 208500, commission: 62.55, pnl: -1200 }
]

const settlementList = ref<Settlement[]>(mockSettlements)

const totalTrades = computed(() => settlementList.value.length)
const totalAmount = computed(() => settlementList.value.reduce((sum, item) => sum + item.amount, 0))
const totalCommission = computed(() => settlementList.value.reduce((sum, item) => sum + item.commission, 0))
const totalPnL = computed(() => settlementList.value.reduce((sum, item) => sum + item.pnl, 0))

onMounted(() => {
  total.value = mockSettlements.length
})

const handleSearch = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('查询完成')
  }, 500)
}

const handleReset = () => {
  filterForm.value = {
    dateRange: null,
    symbol: '',
    direction: ''
  }
  ElMessage.info('已重置筛选条件')
}

const handleExport = () => {
  ElMessage.success('交割单导出成功')
}

const handleDetail = (row: Settlement) => {
  ElMessage.info(`查看交割单详情: ${row.settlementId}`)
}
</script>

<style scoped>
.settlement-sheet-container {
  padding: 20px;
}

.filter-card,
.stat-card,
.list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  .settlement-sheet-container {
    padding: 10px;
  }
}
</style>

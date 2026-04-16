<template>
  <div class="entrust-records-container">
    <el-card class="filter-card">
      <el-form :model="filterForm" inline label-width="100px">
        <el-form-item label="标的代码">
          <el-input v-model="filterForm.symbol" placeholder="请输入标的代码" clearable style="width: 150px;" />
        </el-form-item>
        <el-form-item label="委托方向">
          <el-select v-model="filterForm.direction" placeholder="全部" clearable style="width: 120px;">
            <el-option label="全部" value="" />
            <el-option label="买入" value="buy" />
            <el-option label="卖出" value="sell" />
          </el-select>
        </el-form-item>
        <el-form-item label="委托状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 120px;">
            <el-option label="全部" value="" />
            <el-option label="未成交" value="pending" />
            <el-option label="部分成交" value="partial" />
            <el-option label="全部成交" value="filled" />
            <el-option label="已撤销" value="cancelled" />
            <el-option label="已拒绝" value="rejected" />
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
          <el-button type="primary" @click="searchRecords">
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
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">总委托数</div>
            <div class="stat-value">{{ stats.total }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">未成交</div>
            <div class="stat-value pending">{{ stats.pending }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">部分成交</div>
            <div class="stat-value partial">{{ stats.partial }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">全部成交</div>
            <div class="stat-value filled">{{ stats.filled }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">已撤销</div>
            <div class="stat-value cancelled">{{ stats.cancelled }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">成交率</div>
            <div class="stat-value">{{ stats.fillRate }}%</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="records-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>委托记录</span>
          <el-button-group>
            <el-button type="primary" size="small" @click="refreshRecords">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="success" size="small" @click="exportRecords">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button type="danger" size="small" @click="cancelAllPending" :disabled="stats.pending === 0">
              <el-icon><Close /></el-icon>
              批量撤单
            </el-button>
          </el-button-group>
        </div>
      </template>

      <el-table :data="entrustRecords" stripe style="width: 100%" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="orderId" label="委托单号" width="180" fixed />
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
        <el-table-column prop="orderType" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">
              {{ row.orderType === 'limit' ? '限价' : row.orderType === 'market' ? '市价' : '条件单' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="委托价" width="120" sortable>
          <template #default="{ row }">
            {{ row.price ? '¥' + row.price.toFixed(2) : '市价' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="委托数量" width="120" sortable />
        <el-table-column prop="filledQuantity" label="成交数量" width="120" sortable />
        <el-table-column prop="filledAmount" label="成交金额" width="130" sortable>
          <template #default="{ row }">
            ¥{{ row.filledAmount?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="orderTime" label="委托时间" width="180" sortable />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending' || row.status === 'partial'"
              type="danger"
              size="small"
              link
              @click="cancelOrder(row)"
            >
              撤销
            </el-button>
            <el-button type="primary" size="small" link @click="viewOrderDetail(row)">
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
      title="委托单详情"
      width="700px"
    >
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="委托单号" :span="2">{{ currentOrder.orderId }}</el-descriptions-item>
        <el-descriptions-item label="标的代码">{{ currentOrder.symbol }}</el-descriptions-item>
        <el-descriptions-item label="标的名称">{{ currentOrder.name }}</el-descriptions-item>
        <el-descriptions-item label="委托方向">
          <el-tag :type="currentOrder.direction === 'buy' ? 'success' : 'danger'">
            {{ currentOrder.direction === 'buy' ? '买入' : '卖出' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="委托类型">
          <el-tag>{{ currentOrder.orderType === 'limit' ? '限价' : '市价' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="委托价格">{{ currentOrder.price ? '¥' + currentOrder.price.toFixed(2) : '市价' }}</el-descriptions-item>
        <el-descriptions-item label="委托数量">{{ currentOrder.quantity }}</el-descriptions-item>
        <el-descriptions-item label="成交数量">{{ currentOrder.filledQuantity }}</el-descriptions-item>
        <el-descriptions-item label="成交金额">¥{{ currentOrder.filledAmount?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) || '0.00' }}</el-descriptions-item>
        <el-descriptions-item label="委托状态">
          <el-tag :type="getStatusType(currentOrder.status)">{{ getStatusText(currentOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="委托时间" :span="2">{{ currentOrder.orderTime }}</el-descriptions-item>
        <el-descriptions-item label="成交时间" :span="2">{{ currentOrder.fillTime || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">成交明细</el-divider>
      <el-table :data="currentOrder?.trades || []" stripe style="width: 100%;">
        <el-table-column prop="tradeId" label="成交编号" width="150" />
        <el-table-column prop="price" label="成交价" width="120">
          <template #default="{ row }">
            ¥{{ row.price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="成交数量" width="120" />
        <el-table-column prop="amount" label="成交金额" width="150">
          <template #default="{ row }">
            ¥{{ row.amount.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
          </template>
        </el-table-column>
        <el-table-column prop="time" label="成交时间" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Download, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const detailDialogVisible = ref(false)
const currentOrder = ref<any>(null)

const filterForm = reactive({
  symbol: '',
  direction: '',
  status: '',
  startDate: '',
  endDate: ''
})

const stats = reactive({
  total: 156,
  pending: 5,
  partial: 3,
  filled: 132,
  cancelled: 16,
  fillRate: 84.6
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 156
})

const entrustRecords = ref([
  {
    orderId: 'ORD2024011500001',
    symbol: '600519',
    name: '贵州茅台',
    direction: 'buy',
    orderType: 'limit',
    price: 1850.00,
    quantity: 100,
    filledQuantity: 100,
    filledAmount: 185000.00,
    status: 'filled',
    orderTime: '2024-01-15 09:30:15',
    fillTime: '2024-01-15 09:30:22',
    trades: [
      { tradeId: 'TRD2024011500001', price: 1850.00, quantity: 100, amount: 185000.00, time: '2024-01-15 09:30:22' }
    ]
  },
  {
    orderId: 'ORD2024011500002',
    symbol: '000001',
    name: '平安银行',
    direction: 'sell',
    orderType: 'market',
    price: null,
    quantity: 500,
    filledQuantity: 500,
    filledAmount: 5875.00,
    status: 'filled',
    orderTime: '2024-01-15 09:35:42',
    fillTime: '2024-01-15 09:35:43',
    trades: [
      { tradeId: 'TRD2024011500002', price: 11.75, quantity: 500, amount: 5875.00, time: '2024-01-15 09:35:43' }
    ]
  },
  {
    orderId: 'ORD2024011500003',
    symbol: '601318',
    name: '中国平安',
    direction: 'buy',
    orderType: 'limit',
    price: 45.50,
    quantity: 200,
    filledQuantity: 80,
    filledAmount: 3640.00,
    status: 'partial',
    orderTime: '2024-01-15 10:15:30',
    fillTime: '2024-01-15 10:15:35',
    trades: [
      { tradeId: 'TRD2024011500003', price: 45.50, quantity: 80, amount: 3640.00, time: '2024-01-15 10:15:35' }
    ]
  },
  {
    orderId: 'ORD2024011500004',
    symbol: '000858',
    name: '五粮液',
    direction: 'buy',
    orderType: 'limit',
    price: 158.00,
    quantity: 50,
    filledQuantity: 0,
    filledAmount: 0,
    status: 'pending',
    orderTime: '2024-01-15 13:45:20',
    fillTime: null,
    trades: []
  },
  {
    orderId: 'ORD2024011500005',
    symbol: '600036',
    name: '招商银行',
    direction: 'sell',
    orderType: 'limit',
    price: 35.00,
    quantity: 300,
    filledQuantity: 0,
    filledAmount: 0,
    status: 'cancelled',
    orderTime: '2024-01-15 14:20:15',
    fillTime: null,
    trades: []
  }
])

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    partial: 'warning',
    filled: 'success',
    cancelled: 'info',
    rejected: 'danger'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '未成交',
    partial: '部分成交',
    filled: '全部成交',
    cancelled: '已撤销',
    rejected: '已拒绝'
  }
  return map[status] || status
}

const searchRecords = () => {
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
    status: '',
    startDate: '',
    endDate: ''
  })
  ElMessage.info('筛选条件已重置')
}

const refreshRecords = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 500)
}

const exportRecords = () => {
  ElMessage.success('导出成功')
}

const cancelOrder = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要撤销该委托单吗？', '撤单确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('撤单成功')
    row.status = 'cancelled'
  } catch {
  }
}

const cancelAllPending = async () => {
  try {
    await ElMessageBox.confirm('确定要撤销所有未成交的委托单吗？', '批量撤单确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('批量撤单成功')
  } catch {
  }
}

const viewOrderDetail = (row: any) => {
  currentOrder.value = row
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
.entrust-records-container {
  padding: 20px;
}

.filter-card,
.stats-card,
.records-card {
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

.stat-value.pending {
  color: #409EFF;
}

.stat-value.partial {
  color: #E6A23C;
}

.stat-value.filled {
  color: #67C23A;
}

.stat-value.cancelled {
  color: #909399;
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
  .entrust-records-container {
    padding: 10px;
  }
}
</style>

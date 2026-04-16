<template>
  <div class="condition-order-container">
    <el-card class="create-card">
      <template #header>
        <span>创建条件单</span>
      </template>
      <el-form :model="orderForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="合约代码" required>
              <el-select v-model="orderForm.symbol" placeholder="请选择合约">
                <el-option label="AU.SHF 黄金" value="AU.SHF" />
                <el-option label="AG.SHF 白银" value="AG.SHF" />
                <el-option label="CU.SHF 铜" value="CU.SHF" />
                <el-option label="RU.SHF 橡胶" value="RU.SHF" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="交易方向" required>
              <el-radio-group v-model="orderForm.direction">
                <el-radio label="long">做多</el-radio>
                <el-radio label="short">做空</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="条件类型" required>
              <el-select v-model="orderForm.conditionType" placeholder="请选择">
                <el-option label="价格突破" value="price_break" />
                <el-option label="价格回落" value="price_retrace" />
                <el-option label="时间条件" value="time" />
                <el-option label="指标触发" value="indicator" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="触发价格">
              <el-input-number v-model="orderForm.triggerPrice" :min="0" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="委托价格">
              <el-input-number v-model="orderForm.orderPrice" :min="0" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="委托数量" required>
              <el-input-number v-model="orderForm.quantity" :min="1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="有效期">
              <el-select v-model="orderForm.validity" placeholder="请选择">
                <el-option label="当日有效" value="day" />
                <el-option label="一周有效" value="week" />
                <el-option label="一月有效" value="month" />
                <el-option label="永久有效" value="forever" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="止损价格">
              <el-input-number v-model="orderForm.stopLossPrice" :min="0" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="止盈价格">
              <el-input-number v-model="orderForm.takeProfitPrice" :min="0" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="orderForm.remark" type="textarea" :rows="2" placeholder="请输入备注信息" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCreateOrder">创建条件单</el-button>
          <el-button @click="handleResetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="待触发" name="pending" />
            <el-tab-pane label="已触发" name="triggered" />
            <el-tab-pane label="已失效" name="expired" />
          </el-tabs>
          <div>
            <el-button type="danger" size="small" @click="handleBatchCancel" :disabled="selectedOrders.length === 0">
              <el-icon><Delete /></el-icon>
              批量撤销
            </el-button>
          </div>
        </div>
      </template>
      <el-skeleton v-if="loading" :rows="8" animated />
      <el-table v-else :data="orderList" @selection-change="handleSelectionChange" stripe style="width: 100%">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="orderId" label="条件单号" width="150" />
        <el-table-column prop="symbol" label="合约代码" width="120" />
        <el-table-column prop="direction" label="方向" width="80">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'long' ? 'success' : 'danger'">
              {{ row.direction === 'long' ? '做多' : '做空' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="conditionType" label="条件类型" width="120">
          <template #default="{ row }">
            {{ getConditionTypeName(row.conditionType) }}
          </template>
        </el-table-column>
        <el-table-column prop="triggerPrice" label="触发价格" width="100" sortable />
        <el-table-column prop="orderPrice" label="委托价格" width="100" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column prop="expireTime" label="到期时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleCancel(scope.row)">撤销</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: center;" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface ConditionOrder {
  orderId: string
  symbol: string
  direction: string
  conditionType: string
  triggerPrice: number
  orderPrice: number
  quantity: number
  createTime: string
  expireTime: string
  status: string
}

const loading = ref(false)
const activeTab = ref('pending')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const selectedOrders = ref<ConditionOrder[]>([])

const orderForm = ref({
  symbol: '',
  direction: 'long',
  conditionType: '',
  triggerPrice: 0,
  orderPrice: 0,
  quantity: 1,
  validity: 'day',
  stopLossPrice: 0,
  takeProfitPrice: 0,
  remark: ''
})

const mockOrders: ConditionOrder[] = [
  { orderId: 'CO20240415001', symbol: 'AU.SHF', direction: 'long', conditionType: 'price_break', triggerPrice: 735.0, orderPrice: 735.5, quantity: 10, createTime: '2024-04-15 09:30:00', expireTime: '2024-04-15 15:00:00', status: 'pending' },
  { orderId: 'CO20240415002', symbol: 'AG.SHF', direction: 'short', conditionType: 'price_retrace', triggerPrice: 5700, orderPrice: 5695, quantity: 50, createTime: '2024-04-15 10:15:00', expireTime: '2024-04-15 15:00:00', status: 'pending' },
  { orderId: 'CO20240414001', symbol: 'CU.SHF', direction: 'long', conditionType: 'price_break', triggerPrice: 69000, orderPrice: 69050, quantity: 5, createTime: '2024-04-14 14:20:00', expireTime: '2024-04-14 15:00:00', status: 'triggered' },
  { orderId: 'CO20240414002', symbol: 'RU.SHF', direction: 'short', conditionType: 'time', triggerPrice: 0, orderPrice: 12800, quantity: 10, createTime: '2024-04-14 09:00:00', expireTime: '2024-04-14 14:00:00', status: 'triggered' },
  { orderId: 'CO20240413001', symbol: 'AU.SHF', direction: 'long', conditionType: 'indicator', triggerPrice: 720, orderPrice: 720.5, quantity: 8, createTime: '2024-04-13 09:45:00', expireTime: '2024-04-13 15:00:00', status: 'expired' }
]

const orderList = ref<ConditionOrder[]>([])

onMounted(() => {
  loadOrders()
})

const loadOrders = () => {
  loading.value = true
  setTimeout(() => {
    orderList.value = mockOrders.filter(order => {
      if (activeTab.value === 'pending') return order.status === 'pending'
      if (activeTab.value === 'triggered') return order.status === 'triggered'
      return order.status === 'expired'
    })
    total.value = orderList.value.length
    loading.value = false
  }, 300)
}

const getConditionTypeName = (type: string) => {
  const nameMap: Record<string, string> = {
    'price_break': '价格突破',
    'price_retrace': '价格回落',
    'time': '时间条件',
    'indicator': '指标触发'
  }
  return nameMap[type] || type
}

const getStatusName = (status: string) => {
  const nameMap: Record<string, string> = {
    'pending': '待触发',
    'triggered': '已触发',
    'expired': '已失效'
  }
  return nameMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    'pending': 'warning',
    'triggered': 'success',
    'expired': 'info'
  }
  return typeMap[status] || 'info'
}

const handleCreateOrder = () => {
  if (!orderForm.value.symbol || !orderForm.value.conditionType || !orderForm.value.quantity) {
    ElMessage.warning('请填写必要信息')
    return
  }
  ElMessage.success('条件单创建成功')
  handleResetForm()
}

const handleResetForm = () => {
  orderForm.value = {
    symbol: '',
    direction: 'long',
    conditionType: '',
    triggerPrice: 0,
    orderPrice: 0,
    quantity: 1,
    validity: 'day',
    stopLossPrice: 0,
    takeProfitPrice: 0,
    remark: ''
  }
}

const handleSelectionChange = (selection: ConditionOrder[]) => {
  selectedOrders.value = selection
}

const handleEdit = (row: ConditionOrder) => {
  ElMessage.info(`编辑条件单: ${row.orderId}`)
}

const handleCancel = async (row: ConditionOrder) => {
  try {
    await ElMessageBox.confirm('确定要撤销该条件单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('条件单已撤销')
    loadOrders()
  } catch {
  }
}

const handleBatchCancel = async () => {
  try {
    await ElMessageBox.confirm(`确定要撤销选中的 ${selectedOrders.value.length} 个条件单吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('批量撤销成功')
    loadOrders()
  } catch {
  }
}
</script>

<style scoped>
.condition-order-container {
  padding: 20px;
}

.create-card,
.list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .condition-order-container {
    padding: 10px;
  }
}
</style>

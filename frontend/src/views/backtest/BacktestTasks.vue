<template>
  <div class="backtest-tasks-container">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>任务筛选</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="任务状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable>
            <el-option label="全部" value="" />
            <el-option label="等待中" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="策略名称">
          <el-input v-model="filterForm.strategyName" placeholder="请输入" clearable style="width: 200px;" />
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="tasks-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>回测任务列表 ({{ tasks.length }})</span>
          <el-button-group>
            <el-button type="danger" size="small" @click="handleBatchDelete" :disabled="selectedTasks.length === 0">
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
            <el-button type="info" size="small" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-button-group>
        </div>
      </template>
      <el-skeleton v-if="loading" :rows="8" animated />
      <el-table
        v-else
        :data="tasks"
        @selection-change="handleSelectionChange"
        stripe
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="任务ID" width="120" />
        <el-table-column prop="strategyName" label="策略名称" width="180" />
        <el-table-column prop="symbol" label="标的" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150">
          <template #default="{ row }">
            <el-progress
              v-if="row.status === 'running'"
              :percentage="row.progress"
              :stroke-width="8"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="startDate" label="开始日期" width="120" />
        <el-table-column prop="endDate" label="结束日期" width="120" />
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <template v-if="scope.row.status === 'pending'">
              <el-button type="primary" size="small" @click="handleStart(scope.row)">
                启动
              </el-button>
              <el-button type="danger" size="small" @click="handleCancel(scope.row)">
                取消
              </el-button>
            </template>
            <template v-else-if="scope.row.status === 'running'">
              <el-button type="warning" size="small" @click="handlePause(scope.row)">
                暂停
              </el-button>
              <el-button type="danger" size="small" @click="handleStop(scope.row)">
                停止
              </el-button>
            </template>
            <template v-else-if="scope.row.status === 'paused'">
              <el-button type="success" size="small" @click="handleResume(scope.row)">
                继续
              </el-button>
              <el-button type="danger" size="small" @click="handleStop(scope.row)">
                停止
              </el-button>
            </template>
            <template v-else>
              <el-button type="primary" size="small" @click="handleViewReport(scope.row)">
                查看报告
              </el-button>
              <el-button type="success" size="small" @click="handleRerun(scope.row)">
                重新运行
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
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

    <el-dialog v-model="createDialogVisible" title="新建回测任务" width="600px">
      <el-form :model="taskForm" label-width="120px">
        <el-form-item label="策略模板" required>
          <el-select v-model="taskForm.strategyId" placeholder="请选择策略" style="width: 100%;">
            <el-option v-for="strategy in strategyOptions" :key="strategy.id" :label="strategy.name" :value="strategy.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标的代码" required>
          <el-input v-model="taskForm.symbol" placeholder="例如: AU.SHF" />
        </el-form-item>
        <el-form-item label="回测周期" required>
          <el-date-picker
            v-model="taskForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="初始资金">
          <el-input-number v-model="taskForm.initialCapital" :min="10000" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="taskForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTask">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Refresh, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const createDialogVisible = ref(false)
const selectedTasks = ref<any[]>([])

const filterForm = ref({
  status: '',
  strategyName: '',
  dateRange: []
})

const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 100
})

const strategyOptions = ref([
  { id: 1, name: '均线交叉策略' },
  { id: 2, name: 'RSI反转策略' },
  { id: 3, name: '布林带突破策略' },
  { id: 4, name: '网格交易策略' }
])

const taskForm = ref({
  strategyId: '',
  symbol: 'AU.SHF',
  dateRange: [new Date('2023-01-01'), new Date()],
  initialCapital: 100000,
  remark: ''
})

const tasks = ref([
  {
    id: 'BT001',
    strategyName: '均线交叉策略',
    symbol: 'AU.SHF',
    status: 'completed',
    progress: 100,
    startDate: '2023-01-01',
    endDate: '2024-04-15',
    createdAt: '2024-04-10 10:30:00',
    duration: '2m 15s'
  },
  {
    id: 'BT002',
    strategyName: 'RSI反转策略',
    symbol: 'AU.SHF',
    status: 'running',
    progress: 65,
    startDate: '2023-01-01',
    endDate: '2024-04-15',
    createdAt: '2024-04-15 09:00:00',
    duration: '1m 30s'
  },
  {
    id: 'BT003',
    strategyName: '布林带突破策略',
    symbol: 'AU.SHF',
    status: 'pending',
    progress: 0,
    startDate: '2023-06-01',
    endDate: '2024-04-15',
    createdAt: '2024-04-15 11:00:00',
    duration: '-'
  },
  {
    id: 'BT004',
    strategyName: '网格交易策略',
    symbol: 'AU.SHF',
    status: 'failed',
    progress: 35,
    startDate: '2023-01-01',
    endDate: '2024-04-15',
    createdAt: '2024-04-14 15:00:00',
    duration: '45s'
  },
  {
    id: 'BT005',
    strategyName: 'ATR止损策略',
    symbol: 'AU.SHF',
    status: 'completed',
    progress: 100,
    startDate: '2023-01-01',
    endDate: '2023-12-31',
    createdAt: '2024-04-13 08:30:00',
    duration: '1m 50s'
  }
])

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    pending: 'info',
    running: 'primary',
    paused: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

const handleSearch = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('搜索完成')
  }, 500)
}

const handleReset = () => {
  filterForm.value = {
    status: '',
    strategyName: '',
    dateRange: []
  }
  ElMessage.info('已重置筛选条件')
}

const handleSelectionChange = (selection: any[]) => {
  selectedTasks.value = selection
}

const handleRefresh = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('列表已刷新')
  }, 500)
}

const showCreateDialog = () => {
  createDialogVisible.value = true
}

const handleCreateTask = () => {
  if (!taskForm.value.strategyId || !taskForm.value.symbol) {
    ElMessage.warning('请填写必填字段')
    return
  }
  ElMessage.success('任务创建成功')
  createDialogVisible.value = false
  tasks.value.unshift({
    id: `BT${String(tasks.value.length + 1).padStart(3, '0')}`,
    strategyName: strategyOptions.value.find(s => s.id === taskForm.value.strategyId)?.name || '',
    symbol: taskForm.value.symbol,
    status: 'pending',
    progress: 0,
    startDate: taskForm.value.dateRange[0]?.toISOString().split('T')[0] || '',
    endDate: taskForm.value.dateRange[1]?.toISOString().split('T')[0] || '',
    createdAt: new Date().toLocaleString(),
    duration: '-'
  })
}

const handleStart = (task: any) => {
  task.status = 'running'
  task.progress = 0
  ElMessage.success(`任务 ${task.id} 已启动`)
}

const handlePause = (task: any) => {
  task.status = 'paused'
  ElMessage.warning(`任务 ${task.id} 已暂停`)
}

const handleResume = (task: any) => {
  task.status = 'running'
  ElMessage.success(`任务 ${task.id} 已继续`)
}

const handleStop = (task: any) => {
  task.status = 'cancelled'
  ElMessage.info(`任务 ${task.id} 已停止`)
}

const handleCancel = (task: any) => {
  task.status = 'cancelled'
  ElMessage.info(`任务 ${task.id} 已取消`)
}

const handleViewReport = (task: any) => {
  ElMessage.info(`查看任务 ${task.id} 的报告`)
}

const handleRerun = (task: any) => {
  task.status = 'pending'
  task.progress = 0
  ElMessage.success(`任务 ${task.id} 已重新加入队列`)
}

const handleDelete = async (task: any) => {
  try {
    await ElMessageBox.confirm(`确认删除任务 ${task.id}?`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = tasks.value.findIndex(t => t.id === task.id)
    if (index > -1) {
      tasks.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch {}
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedTasks.value.length} 个任务?`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    selectedTasks.value.forEach(task => {
      const index = tasks.value.findIndex(t => t.id === task.id)
      if (index > -1) {
        tasks.value.splice(index, 1)
      }
    })
    ElMessage.success('批量删除成功')
  } catch {}
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
}

const handleCurrentChange = (page: number) => {
  pagination.value.currentPage = page
}

onMounted(() => {
  handleRefresh()
})
</script>

<style scoped>
.backtest-tasks-container {
  padding: 20px;
}

.filter-card,
.tasks-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .backtest-tasks-container {
    padding: 10px;
  }
}
</style>

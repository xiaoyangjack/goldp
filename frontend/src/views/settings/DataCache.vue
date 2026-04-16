<template>
  <div class="data-cache-container">
    <el-card class="overview-card">
      <template #header>
        <span>缓存概览</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总缓存大小</div>
            <div class="stat-value">{{ formatSize(totalSize) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">缓存项目数</div>
            <div class="stat-value">{{ totalItems }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">缓存命中率</div>
            <div class="stat-value">{{ hitRate.toFixed(1) }}%</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">最后更新时间</div>
            <div class="stat-value">{{ lastUpdateTime }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="settings-card" style="margin-top: 20px;">
      <template #header>
        <span>缓存设置</span>
      </template>
      <el-form :model="cacheSettings" label-width="180px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="缓存有效期(天)">
              <el-input-number v-model="cacheSettings.expireDays" :min="1" :max="365" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大缓存大小(GB)">
              <el-input-number v-model="cacheSettings.maxSizeGB" :min="0.1" :max="100" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="自动清理">
              <el-switch v-model="cacheSettings.autoClean" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预加载热门数据">
              <el-switch v-model="cacheSettings.preloadHotData" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="缓存策略">
          <el-radio-group v-model="cacheSettings.strategy">
            <el-radio label="lru">LRU (最近最少使用)</el-radio>
            <el-radio label="lfu">LFU (最不经常使用)</el-radio>
            <el-radio label="fifo">FIFO (先进先出)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSaveSettings">
            <el-icon><Document /></el-icon>
            保存设置
          </el-button>
          <el-button @click="handleResetSettings">
            <el-icon><Refresh /></el-icon>
            重置默认
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="types-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>缓存分类</span>
          <el-button-group>
            <el-button type="warning" size="small" @click="handleCleanExpired">
              <el-icon><Delete /></el-icon>
              清理过期
            </el-button>
            <el-button type="danger" size="small" @click="handleCleanAll">
              <el-icon><Delete /></el-icon>
              清理全部
            </el-button>
          </el-button-group>
        </div>
      </template>
      <el-table :data="cacheTypes" style="width: 100%;">
        <el-table-column prop="name" label="缓存类型" width="200" />
        <el-table-column prop="description" label="说明" />
        <el-table-column prop="size" label="大小" width="150" sortable>
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="count" label="项目数" width="120" sortable />
        <el-table-column prop="hitRate" label="命中率" width="120" sortable>
          <template #default="{ row }">
            {{ row.hitRate.toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleRefresh(scope.row)">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="danger" size="small" @click="handleCleanType(scope.row)">
              <el-icon><Delete /></el-icon>
              清理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="list-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>缓存详情</span>
          <el-input v-model="searchKeyword" placeholder="搜索缓存项" clearable style="width: 300px;" @clear="handleSearch" />
        </div>
      </template>
      <el-table :data="filteredCacheList" stripe style="width: 100%;">
        <el-table-column prop="key" label="缓存键" width="250" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120" sortable>
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" sortable />
        <el-table-column prop="expireTime" label="过期时间" width="180" sortable />
        <el-table-column prop="accessCount" label="访问次数" width="100" sortable />
        <el-table-column prop="lastAccessTime" label="最后访问" width="180" sortable />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button type="info" size="small" @click="handleViewDetail(scope.row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="danger" size="small" @click="handleDeleteItem(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: center;" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Document, Refresh, Delete, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface CacheType {
  id: string
  name: string
  description: string
  size: number
  count: number
  hitRate: number
}

interface CacheItem {
  key: string
  type: string
  size: number
  createTime: string
  expireTime: string
  accessCount: number
  lastAccessTime: string
}

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')

const totalSize = ref(2560 * 1024 * 1024)
const totalItems = ref(1523)
const hitRate = ref(87.5)
const lastUpdateTime = ref('2024-04-16 15:30:00')

const cacheSettings = ref({
  expireDays: 30,
  maxSizeGB: 10,
  autoClean: true,
  preloadHotData: true,
  strategy: 'lru'
})

const cacheTypes: CacheType[] = [
  { id: 'market', name: '行情数据', description: 'K线、Tick、实时行情等数据', size: 1024 * 1024 * 1024, count: 580, hitRate: 92.3 },
  { id: 'factor', name: '因子数据', description: '因子计算结果、因子值等', size: 512 * 1024 * 1024, count: 320, hitRate: 88.5 },
  { id: 'backtest', name: '回测数据', description: '回测结果、报告等', size: 384 * 1024 * 1024, count: 185, hitRate: 82.1 },
  { id: 'strategy', name: '策略数据', description: '策略配置、参数等', size: 256 * 1024 * 1024, count: 268, hitRate: 85.7 },
  { id: 'other', name: '其他数据', description: '日志、临时文件等', size: 384 * 1024 * 1024, count: 170, hitRate: 75.2 }
]

const mockCacheList: CacheItem[] = [
  { key: 'market:kline:AU.SHF:1d:20240101-20240416', type: '行情数据', size: 10 * 1024 * 1024, createTime: '2024-04-16 10:00:00', expireTime: '2024-05-16 10:00:00', accessCount: 125, lastAccessTime: '2024-04-16 15:20:00' },
  { key: 'market:tick:AU.SHF:20240416', type: '行情数据', size: 50 * 1024 * 1024, createTime: '2024-04-16 09:00:00', expireTime: '2024-04-17 09:00:00', accessCount: 89, lastAccessTime: '2024-04-16 15:15:00' },
  { key: 'factor:momentum:AU.SHF:20240101-20240416', type: '因子数据', size: 5 * 1024 * 1024, createTime: '2024-04-15 14:30:00', expireTime: '2024-05-15 14:30:00', accessCount: 45, lastAccessTime: '2024-04-16 14:00:00' },
  { key: 'backtest:result:bt_20240415_001', type: '回测数据', size: 20 * 1024 * 1024, createTime: '2024-04-15 18:00:00', expireTime: '2024-07-15 18:00:00', accessCount: 28, lastAccessTime: '2024-04-16 12:30:00' },
  { key: 'strategy:config:ma_cross_v1', type: '策略数据', size: 100 * 1024, createTime: '2024-04-10 09:00:00', expireTime: '2024-07-10 09:00:00', accessCount: 67, lastAccessTime: '2024-04-16 10:45:00' }
]

const cacheList = ref<CacheItem[]>(mockCacheList)

const filteredCacheList = computed(() => {
  if (!searchKeyword.value) return cacheList.value
  return cacheList.value.filter(item => item.key.includes(searchKeyword.value) || item.type.includes(searchKeyword.value))
})

const formatSize = (bytes: number): string => {
  if (bytes >= 1024 * 1024 * 1024) return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
  if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  if (bytes >= 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return bytes + ' B'
}

const handleSaveSettings = () => {
  ElMessage.success('缓存设置已保存')
}

const handleResetSettings = () => {
  cacheSettings.value = {
    expireDays: 30,
    maxSizeGB: 10,
    autoClean: true,
    preloadHotData: true,
    strategy: 'lru'
  }
  ElMessage.info('已重置为默认设置')
}

const handleCleanExpired = async () => {
  try {
    await ElMessageBox.confirm('确定要清理所有过期的缓存吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('过期缓存清理成功')
  } catch {
  }
}

const handleCleanAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清理所有缓存吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('所有缓存已清理')
  } catch {
  }
}

const handleRefresh = (row: CacheType) => {
  ElMessage.info(`正在刷新 ${row.name}...`)
}

const handleCleanType = async (row: CacheType) => {
  try {
    await ElMessageBox.confirm(`确定要清理 ${row.name} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success(`${row.name} 已清理`)
  } catch {
  }
}

const handleSearch = () => {
  ElMessage.success('搜索完成')
}

const handleViewDetail = (row: CacheItem) => {
  ElMessage.info(`查看缓存详情: ${row.key}`)
}

const handleDeleteItem = async (row: CacheItem) => {
  try {
    await ElMessageBox.confirm('确定要删除该缓存项吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = cacheList.value.findIndex(item => item.key === row.key)
    if (index > -1) {
      cacheList.value.splice(index, 1)
    }
    ElMessage.success('缓存项已删除')
  } catch {
  }
}

onMounted(() => {
  total.value = mockCacheList.length
})
</script>

<style scoped>
.data-cache-container {
  padding: 20px;
}

.overview-card,
.settings-card,
.types-card,
.list-card {
  margin-bottom: 20px;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .data-cache-container {
    padding: 10px;
  }
}
</style>
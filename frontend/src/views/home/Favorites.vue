<template>
  <div class="favorites-container">
    <el-card class="favorites-card">
      <template #header>
        <div class="card-header">
          <span>我的收藏</span>
          <div class="header-actions">
            <el-radio-group v-model="activeTab" size="small">
              <el-radio-button label="strategies">策略</el-radio-button>
              <el-radio-button label="factors">因子</el-radio-button>
            </el-radio-group>
            <el-button type="primary" size="small" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      <div class="favorites-content">
        <el-skeleton v-if="loading" :rows="8" animated />
        <div v-else>
          <el-empty v-if="currentData.length === 0" description="暂无收藏" />
          <el-table v-else :data="currentData" stripe style="width: 100%">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="type" label="类型">
              <template #default="scope">
                <el-tag size="small">{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="favoriteDate" label="收藏时间" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button type="primary" size="small" link @click="viewDetail(scope.row)">
                  查看
                </el-button>
                <el-button type="danger" size="small" link @click="removeFavorite(scope.row)">
                  取消收藏
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('strategies')
const loading = ref(false)

const strategies = ref([
  { name: '沪深300多因子策略', type: '多因子', description: '基于市值、估值、动量等多因子的选股策略', favoriteDate: '2024-01-15 10:30:00' },
  { name: '中证500动量策略', type: '动量', description: '基于价格动量的选股策略', favoriteDate: '2024-01-10 14:20:00' },
  { name: '行业轮动策略', type: '行业轮动', description: '基于行业景气度的轮动策略', favoriteDate: '2024-01-05 09:15:00' }
])

const factors = ref([
  { name: 'PE估值因子', type: '估值', description: '市盈率因子，用于衡量股票估值水平', favoriteDate: '2024-01-12 11:00:00' },
  { name: 'ROE盈利因子', type: '盈利', description: '净资产收益率因子，衡量公司盈利能力', favoriteDate: '2024-01-08 16:30:00' },
  { name: '动量因子', type: '动量', description: '价格动量因子，捕捉趋势', favoriteDate: '2024-01-03 08:45:00' }
])

const currentData = computed(() => {
  return activeTab.value === 'strategies' ? strategies.value : factors.value
})

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 1000)
}

const viewDetail = (row: any) => {
  ElMessage.info(`查看${row.name}详情`)
}

const removeFavorite = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    if (activeTab.value === 'strategies') {
      strategies.value = strategies.value.filter(item => item.name !== row.name)
    } else {
      factors.value = factors.value.filter(item => item.name !== row.name)
    }
    ElMessage.success('已取消收藏')
  } catch {
    ElMessage.info('已取消操作')
  }
}
</script>

<style scoped>
.favorites-container {
  padding: 20px;
}

.favorites-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.favorites-content {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .favorites-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>

<template>
  <div class="strategy-development-container">
    <el-card class="strategy-card">
      <template #header>
        <div class="card-header">
          <span>策略开发</span>
          <el-button type="primary" size="small" @click="fetchStrategyTemplates">
            <el-icon><Refresh /></el-icon>
            刷新模板
          </el-button>
        </div>
      </template>
      <div class="strategy-content">
        <el-skeleton v-if="loading" :rows="10" animated />
        <el-table v-else :data="strategyTemplates" stripe style="width: 100%">
          <el-table-column prop="id" label="策略ID" />
          <el-table-column prop="name" label="策略名称" />
          <el-table-column prop="description" label="策略描述" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="primary" size="small" @click="editStrategy(scope.row)">
                编辑
              </el-button>
              <el-button type="success" size="small" style="margin-left: 10px" @click="runBacktest(scope.row)">
                回测
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { strategyApi } from '../../api'
import { ElMessage } from 'element-plus'

// 策略模板数据
const strategyTemplates = ref([])
const loading = ref(false)

// 获取策略模板
const fetchStrategyTemplates = async () => {
  loading.value = true
  try {
    const response = await strategyApi.getStrategyTemplates()
    if (response.code === 200) {
      strategyTemplates.value = response.data
    }
  } catch (error) {
    console.error('Failed to get strategy templates:', error)
    ElMessage.error('获取策略模板失败')
  } finally {
    loading.value = false
  }
}

// 编辑策略
const editStrategy = (strategy: any) => {
  ElMessage.info(`编辑策略: ${strategy.name}`)
  // 这里可以添加策略编辑的逻辑
}

// 运行回测
const runBacktest = (strategy: any) => {
  ElMessage.info(`运行回测: ${strategy.name}`)
  // 这里可以添加回测运行的逻辑
}

// 初始化数据
fetchStrategyTemplates()
</script>

<style scoped>
.strategy-development-container {
  padding: 20px;
}

.strategy-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-content {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .strategy-development-container {
    padding: 10px;
  }
}
</style>
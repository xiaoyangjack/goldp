<template>
  <div class="factor-research-container">
    <el-card class="factor-card">
      <template #header>
        <div class="card-header">
          <span>因子研究</span>
          <el-button type="primary" size="small" @click="fetchFactorLibrary">
            <el-icon><Refresh /></el-icon>
            刷新因子库
          </el-button>
        </div>
      </template>
      <div class="factor-content">
        <el-skeleton v-if="loading" :rows="10" animated />
        <el-table v-else :data="factorLibrary" stripe style="width: 100%">
          <el-table-column prop="id" label="因子ID" />
          <el-table-column prop="name" label="因子名称" />
          <el-table-column prop="category" label="因子类别" />
          <el-table-column prop="description" label="因子描述" />
          <el-table-column prop="formula" label="计算公式" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button type="primary" size="small" @click="analyzeFactor(scope.row)">
                分析
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
import { factorApi } from '../../api'
import { ElMessage } from 'element-plus'

// 因子库数据
const factorLibrary = ref([])
const loading = ref(false)

// 获取因子库
const fetchFactorLibrary = async () => {
  loading.value = true
  try {
    const response = await factorApi.getFactorLibrary()
    if (response.code === 200) {
      factorLibrary.value = response.data
    }
  } catch (error) {
    console.error('Failed to get factor library:', error)
    ElMessage.error('获取因子库失败')
  } finally {
    loading.value = false
  }
}

// 分析因子
const analyzeFactor = (factor: any) => {
  ElMessage.info(`分析因子: ${factor.name}`)
  // 这里可以添加因子分析的逻辑
}

// 初始化数据
fetchFactorLibrary()
</script>

<style scoped>
.factor-research-container {
  padding: 20px;
}

.factor-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.factor-content {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .factor-research-container {
    padding: 10px;
  }
}
</style>
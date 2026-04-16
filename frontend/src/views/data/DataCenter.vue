<template>
  <div class="data-center-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>数据中心</span>
          <el-button type="primary" size="small" @click="fetchMarketData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>
      <div class="data-content">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="股票代码">
            <el-input v-model="searchForm.symbol" placeholder="请输入股票代码" />
          </el-form-item>
          <el-form-item label="开始日期">
            <el-date-picker v-model="searchForm.startDate" type="date" placeholder="选择开始日期" />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker v-model="searchForm.endDate" type="date" placeholder="选择结束日期" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchMarketData">查询</el-button>
          </el-form-item>
        </el-form>
        
        <div class="data-table">
          <el-skeleton v-if="loading" :rows="10" animated />
          <el-table v-else :data="marketData" stripe style="width: 100%">
            <el-table-column prop="date" label="日期" />
            <el-table-column prop="open" label="开盘价" />
            <el-table-column prop="high" label="最高价" />
            <el-table-column prop="low" label="最低价" />
            <el-table-column prop="close" label="收盘价" />
            <el-table-column prop="volume" label="成交量" />
            <el-table-column prop="amount" label="成交额" />
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { dataApi } from '../../api'
import { ElMessage } from 'element-plus'

// 搜索表单
const searchForm = reactive({
  symbol: '600000',
  startDate: '2024-01-01',
  endDate: '2024-01-31'
})

// 市场数据
const marketData = ref([])
const loading = ref(false)

// 获取市场数据
const fetchMarketData = async () => {
  loading.value = true
  try {
    const response = await dataApi.getMarketData(
      searchForm.symbol,
      searchForm.startDate,
      searchForm.endDate
    )
    if (response.code === 200) {
      marketData.value = response.data
    }
  } catch (error) {
    console.error('Failed to get market data:', error)
    ElMessage.error('获取市场数据失败')
  } finally {
    loading.value = false
  }
}

// 初始化数据
fetchMarketData()
</script>

<style scoped>
.data-center-container {
  padding: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.data-table {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .data-center-container {
    padding: 10px;
  }
  
  .search-form {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-form .el-form-item {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>
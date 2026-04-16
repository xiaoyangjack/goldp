<template>
  <div class="fundamental-data-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>基本面数据</span>
          <el-button type="primary" size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="data-content">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="股票代码">
            <el-input v-model="searchForm.symbol" placeholder="请输入股票代码" />
          </el-form-item>
          <el-form-item label="报告期">
            <el-select v-model="searchForm.period" placeholder="选择报告期">
              <el-option label="2023年报" value="2023-12-31" />
              <el-option label="2023三季报" value="2023-09-30" />
              <el-option label="2023中报" value="2023-06-30" />
              <el-option label="2023一季报" value="2023-03-31" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchData">查询</el-button>
          </el-form-item>
        </el-form>
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="财务数据" name="finance">
            <el-skeleton v-if="loading" :rows="10" animated />
            <el-table v-else :data="financeData" stripe style="width: 100%">
              <el-table-column prop="item" label="项目" />
              <el-table-column prop="value" label="数值" />
              <el-table-column prop="unit" label="单位" />
              <el-table-column prop="growth" label="同比增长">
                <template #default="scope">
                  <span :class="scope.row.growth >= 0 ? 'positive' : 'negative'">
                    {{ scope.row.growth >= 0 ? '+' : '' }}{{ scope.row.growth }}%
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="估值指标" name="valuation">
            <el-skeleton v-if="loading" :rows="10" animated />
            <div v-else class="valuation-grid">
              <el-card v-for="item in valuationData" :key="item.name" class="valuation-item">
                <div class="valuation-name">{{ item.name }}</div>
                <div class="valuation-value">{{ item.value }}</div>
                <div :class="['valuation-change', item.change >= 0 ? 'positive' : 'negative']">
                  {{ item.change >= 0 ? '+' : '' }}{{ item.change }}%
                </div>
              </el-card>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('finance')
const loading = ref(false)

const searchForm = reactive({
  symbol: '600000',
  period: '2023-12-31'
})

const financeData = ref([
  { item: '营业收入', value: '1,234.56', unit: '亿元', growth: 12.5 },
  { item: '净利润', value: '456.78', unit: '亿元', growth: 8.3 },
  { item: '总资产', value: '8,901.23', unit: '亿元', growth: 5.6 },
  { item: '净资产', value: '3,456.78', unit: '亿元', growth: 7.2 },
  { item: '经营现金流', value: '678.90', unit: '亿元', growth: 15.3 },
  { item: '每股收益', value: '2.34', unit: '元', growth: 10.5 }
])

const valuationData = ref([
  { name: 'PE(市盈率)', value: '12.5', change: 2.3 },
  { name: 'PB(市净率)', value: '1.2', change: -1.5 },
  { name: 'PS(市销率)', value: '3.5', change: 0.8 },
  { name: 'PCF(市现率)', value: '8.9', change: -2.1 },
  { name: 'EV/EBITDA', value: '7.5', change: 1.2 },
  { name: '股息率', value: '3.2%', change: 0.5 }
])

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 1000)
}

const searchData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('查询成功')
  }, 1000)
}
</script>

<style scoped>
.fundamental-data-container {
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

.data-content {
  padding: 10px 0;
}

.valuation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.valuation-item {
  text-align: center;
}

.valuation-name {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.valuation-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.valuation-change {
  font-size: 14px;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

@media (max-width: 768px) {
  .fundamental-data-container {
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
  
  .valuation-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>

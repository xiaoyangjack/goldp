<template>
  <div class="factor-calculation-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>因子计算</span>
        </div>
      </template>
      <div class="data-content">
        <el-form :model="calcForm" label-width="150px">
          <el-form-item label="因子名称">
            <el-select v-model="calcForm.factor" placeholder="请选择因子">
              <el-option label="PE估值因子" value="pe" />
              <el-option label="PB估值因子" value="pb" />
              <el-option label="ROE盈利因子" value="roe" />
              <el-option label="动量因子" value="momentum" />
            </el-select>
          </el-form-item>
          <el-form-item label="股票池">
            <el-select v-model="calcForm.universe" placeholder="请选择股票池">
              <el-option label="沪深300" value="hs300" />
              <el-option label="中证500" value="zz500" />
              <el-option label="中证800" value="zz800" />
              <el-option label="全市场" value="all" />
            </el-select>
          </el-form-item>
          <el-form-item label="计算周期">
            <el-select v-model="calcForm.period" placeholder="请选择计算周期">
              <el-option label="日频" value="daily" />
              <el-option label="周频" value="weekly" />
              <el-option label="月频" value="monthly" />
            </el-select>
          </el-form-item>
          <el-form-item label="开始日期">
            <el-date-picker v-model="calcForm.startDate" type="date" placeholder="选择开始日期" />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker v-model="calcForm.endDate" type="date" placeholder="选择结束日期" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="calculateFactor" :loading="calculating">
              <el-icon v-if="!calculating"><Operation /></el-icon>
              开始计算
            </el-button>
          </el-form-item>
        </el-form>
        
        <el-card v-if="resultVisible" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>计算结果</span>
              <el-button type="primary" size="small" @click="exportResult">导出</el-button>
            </div>
          </template>
          <el-table :data="factorResult" stripe style="width: 100%">
            <el-table-column prop="code" label="股票代码" width="120" />
            <el-table-column prop="name" label="股票名称" width="120" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="value" label="因子值" width="120" />
            <el-table-column prop="rank" label="排名" width="100" />
          </el-table>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Operation } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const calculating = ref(false)
const resultVisible = ref(false)

const calcForm = reactive({
  factor: '',
  universe: '',
  period: '',
  startDate: '',
  endDate: ''
})

const factorResult = ref([
  { code: '600519', name: '贵州茅台', date: '2024-01-15', value: 35.2, rank: 15 },
  { code: '000858', name: '五粮液', date: '2024-01-15', value: 28.5, rank: 25 },
  { code: '601318', name: '中国平安', date: '2024-01-15', value: 12.3, rank: 180 },
  { code: '000001', name: '平安银行', date: '2024-01-15', value: 8.7, rank: 250 },
  { code: '600036', name: '招商银行', date: '2024-01-15', value: 10.5, rank: 220 }
])

const calculateFactor = () => {
  if (!calcForm.factor || !calcForm.universe || !calcForm.period) {
    ElMessage.warning('请填写完整的计算参数')
    return
  }
  calculating.value = true
  setTimeout(() => {
    calculating.value = false
    resultVisible.value = true
    ElMessage.success('因子计算完成')
  }, 2000)
}

const exportResult = () => {
  ElMessage.success('导出成功')
}
</script>

<style scoped>
.factor-calculation-container {
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

.data-content {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .factor-calculation-container {
    padding: 10px;
  }
}
</style>

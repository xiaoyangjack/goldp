<template>
  <div class="performance-analysis-container">
    <el-card class="performance-card">
      <template #header>
        <div class="card-header">
          <span>绩效分析</span>
          <el-button type="primary" size="small" @click="analyzePerformance">
            <el-icon><Refresh /></el-icon>
            分析绩效
          </el-button>
        </div>
      </template>
      <div class="performance-content">
        <el-form :model="analysisForm" class="analysis-form">
          <el-form-item label="开始日期">
            <el-date-picker v-model="analysisForm.startDate" type="date" placeholder="选择开始日期" />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker v-model="analysisForm.endDate" type="date" placeholder="选择结束日期" />
          </el-form-item>
          <el-form-item label="账户ID">
            <el-input v-model="analysisForm.accountId" placeholder="请输入账户ID" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="analyzePerformance" :loading="loading">分析</el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="performanceResult" class="performance-result">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="result-card">
                <template #header>
                  <span>收益分析</span>
                </template>
                <el-table :data="returnMetrics" stripe style="width: 100%">
                  <el-table-column prop="name" label="指标名称" />
                  <el-table-column prop="value" label="指标值" />
                </el-table>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="result-card">
                <template #header>
                  <span>风险分析</span>
                </template>
                <el-table :data="riskMetrics" stripe style="width: 100%">
                  <el-table-column prop="name" label="指标名称" />
                  <el-table-column prop="value" label="指标值" />
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { performanceApi } from '../../api'
import { ElMessage } from 'element-plus'

// 分析表单
const analysisForm = reactive({
  startDate: '2023-01-01',
  endDate: '2023-12-31',
  accountId: '1'
})

// 绩效分析结果
const performanceResult = ref(null)
const loading = ref(false)

// 收益指标
const returnMetrics = computed(() => {
  if (!performanceResult.value) return []
  return [
    { name: '总收益率', value: performanceResult.value.returnAnalysis.totalReturn + '%' },
    { name: '年化收益率', value: performanceResult.value.returnAnalysis.annualReturn + '%' },
    { name: '基准收益率', value: performanceResult.value.returnAnalysis.benchmarkReturn + '%' }
  ]
})

// 风险指标
const riskMetrics = computed(() => {
  if (!performanceResult.value) return []
  return [
    { name: '最大回撤', value: performanceResult.value.riskAnalysis.maxDrawdown + '%' },
    { name: '波动率', value: performanceResult.value.riskAnalysis.volatility + '%' },
    { name: '夏普比率', value: performanceResult.value.riskAnalysis.sharpeRatio },
    { name: '索提诺比率', value: performanceResult.value.riskAnalysis.sortinoRatio },
    { name: '卡马比率', value: performanceResult.value.riskAnalysis.calmarRatio }
  ]
})

// 分析绩效
const analyzePerformance = async () => {
  loading.value = true
  try {
    const response = await performanceApi.analyzePerformance(analysisForm)
    if (response.code === 200) {
      performanceResult.value = response.data
      ElMessage.success('绩效分析成功')
    }
  } catch (error) {
    console.error('Failed to analyze performance:', error)
    ElMessage.error('绩效分析失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.performance-analysis-container {
  padding: 20px;
}

.performance-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analysis-form {
  margin-bottom: 20px;
}

.analysis-form .el-form-item {
  margin-bottom: 15px;
}

.performance-result {
  margin-top: 20px;
}

.result-card {
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .performance-analysis-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
}
</style>
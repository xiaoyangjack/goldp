<template>
  <div class="backtest-engine-container">
    <el-card class="backtest-card">
      <template #header>
        <div class="card-header">
          <span>回测引擎</span>
        </div>
      </template>
      <div class="backtest-content">
        <el-form :model="backtestForm" class="backtest-form">
          <el-form-item label="策略ID">
            <el-input v-model="backtestForm.strategyId" placeholder="请输入策略ID" />
          </el-form-item>
          <el-form-item label="开始日期">
            <el-date-picker v-model="backtestForm.startDate" type="date" placeholder="选择开始日期" />
          </el-form-item>
          <el-form-item label="结束日期">
            <el-date-picker v-model="backtestForm.endDate" type="date" placeholder="选择结束日期" />
          </el-form-item>
          <el-form-item label="初始资金">
            <el-input v-model="backtestForm.initialCapital" type="number" placeholder="请输入初始资金" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="runBacktest" :loading="loading">运行回测</el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="backtestResult" class="backtest-result">
          <el-card class="result-card">
            <template #header>
              <span>回测结果</span>
            </template>
            <el-table :data="backtestMetrics" stripe style="width: 100%">
              <el-table-column prop="name" label="指标名称" />
              <el-table-column prop="value" label="指标值" />
            </el-table>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { backtestEngineApi } from '../../api'
import { ElMessage } from 'element-plus'

// 回测表单
const backtestForm = reactive({
  strategyId: '1',
  startDate: '2023-01-01',
  endDate: '2023-12-31',
  initialCapital: 1000000
})

// 回测结果
const backtestResult = ref(null)
const loading = ref(false)

// 回测指标
const backtestMetrics = computed(() => {
  if (!backtestResult.value) return []
  return [
    { name: '年化收益率', value: backtestResult.value.metrics.annualReturn + '%' },
    { name: '总收益率', value: backtestResult.value.metrics.totalReturn + '%' },
    { name: '夏普比率', value: backtestResult.value.metrics.sharpeRatio },
    { name: '最大回撤', value: backtestResult.value.metrics.maxDrawdown + '%' },
    { name: '胜率', value: backtestResult.value.metrics.winRate + '%' },
    { name: '盈利因子', value: backtestResult.value.metrics.profitFactor },
    { name: '换手率', value: backtestResult.value.metrics.turnover }
  ]
})

// 运行回测
const runBacktest = async () => {
  loading.value = true
  try {
    const response = await backtestEngineApi.runBacktest(backtestForm)
    if (response.code === 200) {
      backtestResult.value = response.data
      ElMessage.success('回测成功')
    }
  } catch (error) {
    console.error('Failed to run backtest:', error)
    ElMessage.error('回测失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.backtest-engine-container {
  padding: 20px;
}

.backtest-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.backtest-form {
  margin-bottom: 20px;
}

.backtest-form .el-form-item {
  margin-bottom: 15px;
}

.backtest-result {
  margin-top: 20px;
}

.result-card {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .backtest-engine-container {
    padding: 10px;
  }
}
</style>
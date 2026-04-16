<template>
  <div class="factor-selection-container">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <span>因子筛选条件</span>
          <el-button type="primary" size="small" @click="handleReset">
            重置
          </el-button>
        </div>
      </template>
      <el-form :model="filterForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="因子类别">
              <el-select v-model="filterForm.category" placeholder="请选择" clearable>
                <el-option label="全部" value="" />
                <el-option label="技术类" value="technical" />
                <el-option label="基本面类" value="fundamental" />
                <el-option label="情绪类" value="sentiment" />
                <el-option label="另类数据" value="alternative" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="IC值范围">
              <el-input-number v-model="filterForm.minIC" :min="-1" :max="1" :step="0.01" placeholder="最小值" style="width: 45%; margin-right: 10px;" />
              <el-input-number v-model="filterForm.maxIC" :min="-1" :max="1" :step="0.01" placeholder="最大值" style="width: 45%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="ICIR范围">
              <el-input-number v-model="filterForm.minICIR" :min="0" :max="10" :step="0.1" placeholder="最小值" style="width: 45%; margin-right: 10px;" />
              <el-input-number v-model="filterForm.maxICIR" :min="0" :max="10" :step="0.1" placeholder="最大值" style="width: 45%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="换手率">
              <el-select v-model="filterForm.turnover" placeholder="请选择" clearable>
                <el-option label="全部" value="" />
                <el-option label="低(<20%)" value="low" />
                <el-option label="中(20%-50%)" value="medium" />
                <el-option label="高(>50%)" value="high" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="收益率">
              <el-input-number v-model="filterForm.minReturn" :min="-100" :max="100" :step="0.1" placeholder="最小(%)" style="width: 45%; margin-right: 10px;" />
              <el-input-number v-model="filterForm.maxReturn" :min="-100" :max="100" :step="0.1" placeholder="最大(%)" style="width: 45%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <el-button type="primary" @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="result-card">
      <template #header>
        <div class="card-header">
          <span>筛选结果 ({{ selectedFactors.length }}/{{ filteredFactors.length }} 已选中)</span>
          <el-button type="primary" size="small" @click="handleBatchAnalyze" :disabled="selectedFactors.length === 0">
            <el-icon><DataAnalysis /></el-icon>
            批量分析
          </el-button>
        </div>
      </template>
      <el-skeleton v-if="loading" :rows="10" animated />
      <el-table v-else :data="filteredFactors" @selection-change="handleSelectionChange" stripe style="width: 100%">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="因子ID" width="100" />
        <el-table-column prop="name" label="因子名称" width="150" />
        <el-table-column prop="category" label="因子类别" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ic" label="IC值" width="100" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.ic >= 0 ? '#67C23A' : '#F56C6C' }">
              {{ row.ic?.toFixed(4) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="icir" label="ICIR" width="100" sortable />
        <el-table-column prop="tvalue" label="T值" width="100" sortable />
        <el-table-column prop="turnover" label="换手率(%)" width="120" sortable />
        <el-table-column prop="return" label="收益率(%)" width="120" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.return >= 0 ? '#67C23A' : '#F56C6C' }">
              {{ row.return?.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleAnalyze(scope.row)">分析</el-button>
            <el-button type="success" size="small" @click="handleAddToPortfolio(scope.row)">添加</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface Factor {
  id: string
  name: string
  category: string
  ic: number
  icir: number
  tvalue: number
  turnover: number
  return: number
  description: string
}

const loading = ref(false)
const selectedFactors = ref<Factor[]>([])

const filterForm = ref({
  category: '',
  minIC: -1,
  maxIC: 1,
  minICIR: 0,
  maxICIR: 10,
  turnover: '',
  minReturn: -100,
  maxReturn: 100
})

const mockFactors: Factor[] = [
  { id: 'F001', name: '动量因子', category: '技术类', ic: 0.08, icir: 1.8, tvalue: 2.5, turnover: 35, return: 12.5, description: '基于过去20日收益率的动量因子' },
  { id: 'F002', name: '反转因子', category: '技术类', ic: -0.05, icir: 1.2, tvalue: -1.8, turnover: 45, return: -8.3, description: '基于过去5日收益率的反转因子' },
  { id: 'F003', name: '波动率因子', category: '技术类', ic: 0.03, icir: 0.8, tvalue: 1.2, turnover: 20, return: 5.2, description: '基于历史波动率的因子' },
  { id: 'F004', name: '市盈率因子', category: '基本面类', ic: 0.12, icir: 2.1, tvalue: 3.2, turnover: 15, return: 18.6, description: '低市盈率因子' },
  { id: 'F005', name: '市净率因子', category: '基本面类', ic: 0.09, icir: 1.9, tvalue: 2.8, turnover: 18, return: 15.3, description: '低市净率因子' },
  { id: 'F006', name: 'ROE因子', category: '基本面类', ic: 0.15, icir: 2.5, tvalue: 3.8, turnover: 12, return: 22.1, description: '净资产收益率因子' },
  { id: 'F007', name: '新闻情绪', category: '情绪类', ic: 0.06, icir: 1.5, tvalue: 2.0, turnover: 55, return: 8.7, description: '基于新闻文本的情绪因子' },
  { id: 'F008', name: '分析师预期', category: '情绪类', ic: 0.10, icir: 2.0, tvalue: 2.9, turnover: 25, return: 14.2, description: '基于分析师评级的因子' }
]

const allFactors = ref<Factor[]>(mockFactors)

const filteredFactors = computed(() => {
  return allFactors.value.filter(factor => {
    if (filterForm.value.category && factor.category !== filterForm.value.category) return false
    if (factor.ic < filterForm.value.minIC || factor.ic > filterForm.value.maxIC) return false
    if (factor.icir < filterForm.value.minICIR || factor.icir > filterForm.value.maxICIR) return false
    if (factor.return < filterForm.value.minReturn || factor.return > filterForm.value.maxReturn) return false
    return true
  })
})

const getCategoryType = (category: string) => {
  const typeMap: Record<string, any> = {
    '技术类': 'primary',
    '基本面类': 'success',
    '情绪类': 'warning',
    '另类数据': 'danger'
  }
  return typeMap[category] || ''
}

const handleSearch = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('筛选完成')
  }, 500)
}

const handleReset = () => {
  filterForm.value = {
    category: '',
    minIC: -1,
    maxIC: 1,
    minICIR: 0,
    maxICIR: 10,
    turnover: '',
    minReturn: -100,
    maxReturn: 100
  }
  ElMessage.info('已重置筛选条件')
}

const handleSelectionChange = (selection: Factor[]) => {
  selectedFactors.value = selection
}

const handleAnalyze = (factor: Factor) => {
  ElMessage.info(`正在分析因子: ${factor.name}`)
}

const handleAddToPortfolio = (factor: Factor) => {
  ElMessage.success(`已添加因子: ${factor.name}`)
}

const handleBatchAnalyze = () => {
  ElMessage.info(`正在批量分析 ${selectedFactors.value.length} 个因子`)
}
</script>

<style scoped>
.factor-selection-container {
  padding: 20px;
}

.filter-card,
.result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .factor-selection-container {
    padding: 10px;
  }
}
</style>

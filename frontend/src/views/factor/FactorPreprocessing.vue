<template>
  <div class="factor-preprocessing-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>因子预处理</span>
        </div>
      </template>
      <div class="data-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="数据清洗" name="clean">
            <el-form :model="cleanForm" label-width="150px">
              <el-form-item label="选择因子">
                <el-select v-model="cleanForm.factor" placeholder="请选择因子">
                  <el-option label="PE估值因子" value="pe" />
                  <el-option label="PB估值因子" value="pb" />
                  <el-option label="ROE盈利因子" value="roe" />
                </el-select>
              </el-form-item>
              <el-form-item label="处理方法">
                <el-checkbox-group v-model="cleanForm.methods">
                  <el-checkbox label="missing">缺失值填充</el-checkbox>
                  <el-checkbox label="duplicate">删除重复值</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="缺失值填充方式">
                <el-radio-group v-model="cleanForm.fillMethod">
                  <el-radio label="mean">均值填充</el-radio>
                  <el-radio label="median">中位数填充</el-radio>
                  <el-radio label="zero">零值填充</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="cleanData">开始清洗</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="去极值" name="winsorize">
            <el-form :model="winsorizeForm" label-width="150px">
              <el-form-item label="选择因子">
                <el-select v-model="winsorizeForm.factor" placeholder="请选择因子">
                  <el-option label="PE估值因子" value="pe" />
                  <el-option label="PB估值因子" value="pb" />
                  <el-option label="ROE盈利因子" value="roe" />
                </el-select>
              </el-form-item>
              <el-form-item label="去极值方法">
                <el-radio-group v-model="winsorizeForm.method">
                  <el-radio label="mad">MAD方法</el-radio>
                  <el-radio label="percentile">百分位法</el-radio>
                  <el-radio label="sigma">3σ方法</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="阈值参数">
                <el-input-number v-model="winsorizeForm.threshold" :min="0.01" :max="0.5" :step="0.01" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="winsorizeData">开始去极值</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="标准化" name="standardize">
            <el-form :model="standardizeForm" label-width="150px">
              <el-form-item label="选择因子">
                <el-select v-model="standardizeForm.factor" placeholder="请选择因子">
                  <el-option label="PE估值因子" value="pe" />
                  <el-option label="PB估值因子" value="pb" />
                  <el-option label="ROE盈利因子" value="roe" />
                </el-select>
              </el-form-item>
              <el-form-item label="标准化方法">
                <el-radio-group v-model="standardizeForm.method">
                  <el-radio label="zscore">Z-Score标准化</el-radio>
                  <el-radio label="rank">排序标准化</el-radio>
                  <el-radio label="minmax">Min-Max标准化</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="行业中性化">
                <el-switch v-model="standardizeForm.neutralize" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="standardizeData">开始标准化</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
        
        <el-card v-if="resultVisible" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>处理结果预览</span>
              <div class="header-actions">
                <el-statistic title="处理前数据量" :value="beforeCount" style="margin-right: 30px;" />
                <el-statistic title="处理后数据量" :value="afterCount" />
              </div>
            </div>
          </template>
          <div ref="chartRef" class="chart" style="height: 350px;"></div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('clean')
const resultVisible = ref(false)
const chartRef = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()
const beforeCount = ref(5000)
const afterCount = ref(4850)

const cleanForm = reactive({
  factor: '',
  methods: [],
  fillMethod: 'mean'
})

const winsorizeForm = reactive({
  factor: '',
  method: 'mad',
  threshold: 0.05
})

const standardizeForm = reactive({
  factor: '',
  method: 'zscore',
  neutralize: false
})

const initChart = () => {
  if (process.env.NODE_ENV !== 'test' && chartRef.value) {
    chart.value = echarts.init(chartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['处理前', '处理后']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '处理前',
          type: 'scatter',
          symbolSize: 8,
          data: Array.from({ length: 50 }, () => [Math.random() * 10 - 5, Math.random() * 10 - 5])
        },
        {
          name: '处理后',
          type: 'scatter',
          symbolSize: 8,
          data: Array.from({ length: 48 }, () => [Math.random() * 6 - 3, Math.random() * 6 - 3])
        }
      ]
    }
    chart.value.setOption(option)
  }
}

const cleanData = () => {
  if (!cleanForm.factor) {
    ElMessage.warning('请选择因子')
    return
  }
  resultVisible.value = true
  ElMessage.success('数据清洗完成')
  initChart()
}

const winsorizeData = () => {
  if (!winsorizeForm.factor) {
    ElMessage.warning('请选择因子')
    return
  }
  resultVisible.value = true
  ElMessage.success('去极值完成')
  initChart()
}

const standardizeData = () => {
  if (!standardizeForm.factor) {
    ElMessage.warning('请选择因子')
    return
  }
  resultVisible.value = true
  ElMessage.success('标准化完成')
  initChart()
}

onMounted(() => {
})
</script>

<style scoped>
.factor-preprocessing-container {
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

.header-actions {
  display: flex;
  align-items: center;
}

.data-content {
  padding: 10px 0;
}

.chart {
  width: 100%;
  height: 350px;
}

@media (max-width: 768px) {
  .factor-preprocessing-container {
    padding: 10px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>

<template>
  <div class="factor-analysis-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>因子有效性分析</span>
          <el-button type="primary" size="small" @click="runAnalysis">
            <el-icon><TrendCharts /></el-icon>
            开始分析
          </el-button>
        </div>
      </template>
      <div class="data-content">
        <el-form :inline="true" :model="analysisForm" class="search-form">
          <el-form-item label="选择因子">
            <el-select v-model="analysisForm.factor" placeholder="请选择因子">
              <el-option label="PE估值因子" value="pe" />
              <el-option label="PB估值因子" value="pb" />
              <el-option label="ROE盈利因子" value="roe" />
              <el-option label="动量因子" value="momentum" />
            </el-select>
          </el-form-item>
          <el-form-item label="股票池">
            <el-select v-model="analysisForm.universe" placeholder="请选择股票池">
              <el-option label="沪深300" value="hs300" />
              <el-option label="中证500" value="zz500" />
              <el-option label="中证800" value="zz800" />
            </el-select>
          </el-form-item>
          <el-form-item label="回测区间">
            <el-date-picker
              v-model="analysisForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
            />
          </el-form-item>
        </el-form>
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="IC分析" name="ic">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>IC统计</template>
                  <el-skeleton v-if="loading" :rows="5" animated />
                  <div v-else class="ic-stats">
                    <div class="stat-item">
                      <span class="label">IC均值</span>
                      <span class="value">0.085</span>
                    </div>
                    <div class="stat-item">
                      <span class="label">IC标准差</span>
                      <span class="value">0.152</span>
                    </div>
                    <div class="stat-item">
                      <span class="label">IR比率</span>
                      <span class="value positive">0.559</span>
                    </div>
                    <div class="stat-item">
                      <span class="label">IC胜率</span>
                      <span class="value positive">62.5%</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>IC时间序列</template>
                  <el-skeleton v-if="loading" :rows="8" animated />
                  <div v-else ref="icChartRef" class="chart" style="height: 280px;"></div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>
          
          <el-tab-pane label="分组回测" name="group">
            <el-card>
              <template #header>分组年化收益率</template>
              <el-skeleton v-if="loading" :rows="8" animated />
              <div v-else ref="groupChartRef" class="chart" style="height: 400px;"></div>
            </el-card>
            <el-card style="margin-top: 20px;">
              <template #header>分组回测详情</template>
              <el-table :data="groupBacktestData" stripe style="width: 100%">
                <el-table-column prop="group" label="分组" width="100" />
                <el-table-column prop="annualReturn" label="年化收益">
                  <template #default="scope">
                    <span :class="scope.row.annualReturn >= 0 ? 'positive' : 'negative'">
                      {{ scope.row.annualReturn >= 0 ? '+' : '' }}{{ scope.row.annualReturn }}%
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="sharpe" label="夏普比率" />
                <el-table-column prop="maxDrawdown" label="最大回撤">
                  <template #default="scope">
                    <span class="negative">{{ scope.row.maxDrawdown }}%</span>
                  </template>
                </el-table-column>
                <el-table-column prop="winRate" label="胜率" />
              </el-table>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('ic')
const loading = ref(false)
const icChartRef = ref<HTMLElement>()
const groupChartRef = ref<HTMLElement>()
const icChart = ref<echarts.ECharts>()
const groupChart = ref<echarts.ECharts>()

const analysisForm = reactive({
  factor: '',
  universe: '',
  dateRange: []
})

const groupBacktestData = ref([
  { group: '第1组(多头)', annualReturn: 25.8, sharpe: 1.85, maxDrawdown: 15.2, winRate: '68.5%' },
  { group: '第2组', annualReturn: 18.5, sharpe: 1.52, maxDrawdown: 18.6, winRate: '62.3%' },
  { group: '第3组', annualReturn: 12.3, sharpe: 1.21, maxDrawdown: 20.1, winRate: '58.7%' },
  { group: '第4组', annualReturn: 6.8, sharpe: 0.85, maxDrawdown: 22.5, winRate: '54.2%' },
  { group: '第5组(空头)', annualReturn: -5.2, sharpe: -0.32, maxDrawdown: 35.8, winRate: '42.5%' }
])

const initICChart = () => {
  if (process.env.NODE_ENV !== 'test' && icChartRef.value) {
    icChart.value = echarts.init(icChartRef.value)
    const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    const data = [0.12, 0.08, 0.15, -0.02, 0.05, 0.18, 0.10, 0.03, 0.12, 0.08, 0.05, 0.15]
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: months
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: 'IC值',
          type: 'bar',
          data: data.map((val, idx) => ({
            value: val,
            itemStyle: {
              color: val >= 0 ? '#67C23A' : '#F56C6C'
            }
          }))
        }
      ]
    }
    icChart.value.setOption(option)
  }
}

const initGroupChart = () => {
  if (process.env.NODE_ENV !== 'test' && groupChartRef.value) {
    groupChart.value = echarts.init(groupChartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['第1组', '第2组', '第3组', '第4组', '第5组']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: '第1组',
          type: 'line',
          smooth: true,
          data: [0, 5, 8, 12, 15, 18, 20, 22, 24, 23, 25, 26],
          lineStyle: {
            color: '#67C23A'
          }
        },
        {
          name: '第2组',
          type: 'line',
          smooth: true,
          data: [0, 3, 6, 9, 11, 14, 16, 17, 18, 17, 19, 18],
          lineStyle: {
            color: '#165DFF'
          }
        },
        {
          name: '第3组',
          type: 'line',
          smooth: true,
          data: [0, 2, 4, 6, 8, 10, 12, 11, 13, 12, 12, 12],
          lineStyle: {
            color: '#E6A23C'
          }
        },
        {
          name: '第4组',
          type: 'line',
          smooth: true,
          data: [0, 1, 3, 4, 5, 6, 7, 6, 7, 6, 7, 7],
          lineStyle: {
            color: '#909399'
          }
        },
        {
          name: '第5组',
          type: 'line',
          smooth: true,
          data: [0, -1, -2, -3, -4, -3, -5, -4, -6, -5, -5, -5],
          lineStyle: {
            color: '#F56C6C'
          }
        }
      ]
    }
    groupChart.value.setOption(option)
  }
}

const runAnalysis = () => {
  if (!analysisForm.factor || !analysisForm.universe) {
    ElMessage.warning('请选择因子和股票池')
    return
  }
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('分析完成')
    initICChart()
    initGroupChart()
  }, 2000)
}

onMounted(() => {
})
</script>

<style scoped>
.factor-analysis-container {
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

.ic-stats {
  padding: 20px 0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.stat-item .label {
  color: #606266;
}

.stat-item .value {
  font-weight: bold;
  font-size: 18px;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.chart {
  width: 100%;
  height: 280px;
}

@media (max-width: 768px) {
  .factor-analysis-container {
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
  
  .el-col {
    margin-bottom: 20px;
  }
}
</style>

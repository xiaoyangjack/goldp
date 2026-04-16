<template>
  <div class="attribution-analysis-container">
    <el-card class="config-card">
      <el-form :model="configForm" inline label-width="100px">
        <el-form-item label="归因模型">
          <el-select v-model="configForm.model" style="width: 150px;">
            <el-option label="Brinson模型" value="brinson" />
            <el-option label="Campisi模型" value="campisi" />
            <el-option label="多因子模型" value="factor" />
          </el-select>
        </el-form-item>
        <el-form-item label="基准组合">
          <el-select v-model="configForm.benchmark" style="width: 150px;">
            <el-option label="沪深300" value="000300" />
            <el-option label="中证500" value="000905" />
            <el-option label="上证50" value="000016" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="configForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 300px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="runAnalysis">
            <el-icon><DataAnalysis /></el-icon>
            运行分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="summary-card" style="margin-top: 20px;">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">组合收益率</div>
            <div class="summary-value" :class="portfolioReturn >= 0 ? 'profit' : 'loss'">
              {{ portfolioReturn >= 0 ? '+' : '' }}{{ (portfolioReturn * 100).toFixed(2) }}%
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">基准收益率</div>
            <div class="summary-value" :class="benchmarkReturn >= 0 ? 'profit' : 'loss'">
              {{ benchmarkReturn >= 0 ? '+' : '' }}{{ (benchmarkReturn * 100).toFixed(2) }}%
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">超额收益</div>
            <div class="summary-value" :class="excessReturn >= 0 ? 'profit' : 'loss'">
              {{ excessReturn >= 0 ? '+' : '' }}{{ (excessReturn * 100).toFixed(2) }}%
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-label">信息比率</div>
            <div class="summary-value" :class="informationRatio >= 0 ? 'profit' : 'loss'">
              {{ informationRatio.toFixed(3) }}
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="attribution-card" style="margin-top: 20px;">
      <template #header>
        <span>收益归因</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="Brinson归因" name="brinson">
          <el-table :data="brinsonAttribution" stripe style="width: 100%;" show-summary :summary-method="getBrinsonSummary">
            <el-table-column prop="sector" label="行业" width="150" />
            <el-table-column label="配置效应" width="140">
              <template #default="{ row }">
                <span :style="{ color: row.allocation >= 0 ? '#67C23A' : '#F56C6C' }">
                  {{ row.allocation >= 0 ? '+' : '' }}{{ (row.allocation * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="选股效应" width="140">
              <template #default="{ row }">
                <span :style="{ color: row.selection >= 0 ? '#67C23A' : '#F56C6C' }">
                  {{ row.selection >= 0 ? '+' : '' }}{{ (row.selection * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="交互效应" width="140">
              <template #default="{ row }">
                <span :style="{ color: row.interaction >= 0 ? '#67C23A' : '#F56C6C' }">
                  {{ row.interaction >= 0 ? '+' : '' }}{{ (row.interaction * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="总超额" width="140">
              <template #default="{ row }">
                <span :style="{ color: row.total >= 0 ? '#67C23A' : '#F56C6C' }">
                  {{ row.total >= 0 ? '+' : '' }}{{ (row.total * 100).toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column label="组合权重" width="120">
              <template #default="{ row }">
                {{ (row.portfolioWeight * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column label="基准权重" width="120">
              <template #default="{ row }">
                {{ (row.benchmarkWeight * 100).toFixed(2) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="归因图表" name="charts">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="chart-card">
                <template #header>
                  <span>归因分解</span>
                </template>
                <div ref="attributionChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="chart-card">
                <template #header>
                  <span>行业配置贡献</span>
                </template>
                <div ref="sectorChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card class="risk-card" style="margin-top: 20px;">
      <template #header>
        <span>风险归因</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-table :data="riskAttribution" stripe style="width: 100%;">
            <el-table-column prop="factor" label="风险因子" />
            <el-table-column prop="contribution" label="风险贡献" width="150">
              <template #default="{ row }">
                {{ (row.contribution * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="marginal" label="边际风险" width="150">
              <template #default="{ row }">
                {{ (row.marginal * 100).toFixed(4) }}
              </template>
            </el-table-column>
            <el-table-column prop="proportion" label="贡献占比" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.proportion" :show-text="false" />
                <span style="margin-left: 10px;">{{ row.proportion }}%</span>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="12">
          <div ref="riskChartRef" class="chart-container"></div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('brinson')
const attributionChartRef = ref<HTMLElement>()
const sectorChartRef = ref<HTMLElement>()
const riskChartRef = ref<HTMLElement>()
let attributionChart: echarts.ECharts | null = null
let sectorChart: echarts.ECharts | null = null
let riskChart: echarts.ECharts | null = null

const configForm = reactive({
  model: 'brinson',
  benchmark: '000300',
  dateRange: ['2024-01-01', '2024-03-31']
})

const portfolioReturn = ref(0.1523)
const benchmarkReturn = ref(0.0845)
const excessReturn = ref(0.0678)
const informationRatio = ref(1.235)

const brinsonAttribution = ref([
  { sector: '消费', allocation: 0.0125, selection: 0.0210, interaction: 0.0045, total: 0.0380, portfolioWeight: 0.25, benchmarkWeight: 0.18 },
  { sector: '科技', allocation: -0.0035, selection: 0.0185, interaction: -0.0020, total: 0.0130, portfolioWeight: 0.22, benchmarkWeight: 0.25 },
  { sector: '金融', allocation: 0.0080, selection: 0.0055, interaction: 0.0015, total: 0.0150, portfolioWeight: 0.18, benchmarkWeight: 0.15 },
  { sector: '医药', allocation: 0.0045, selection: -0.0025, interaction: 0.0010, total: 0.0030, portfolioWeight: 0.15, benchmarkWeight: 0.12 },
  { sector: '能源', allocation: -0.0020, selection: 0.0035, interaction: -0.0007, total: 0.0008, portfolioWeight: 0.10, benchmarkWeight: 0.12 },
  { sector: '其他', allocation: 0.0010, selection: -0.0040, interaction: -0.0005, total: -0.0035, portfolioWeight: 0.10, benchmarkWeight: 0.18 }
])

const riskAttribution = ref([
  { factor: '市场风险', contribution: 0.085, marginal: 0.0234, proportion: 45 },
  { factor: '行业风险', contribution: 0.045, marginal: 0.0125, proportion: 24 },
  { factor: '风格风险', contribution: 0.035, marginal: 0.0095, proportion: 18 },
  { factor: '特质风险', contribution: 0.025, marginal: 0.0068, proportion: 13 }
])

const getBrinsonSummary = ({ columns, data }: any) => {
  const sums = ['合计', 0, 0, 0, 0, 0, 0, 0]
  data.forEach((row: any) => {
    sums[1] += row.allocation
    sums[2] += row.selection
    sums[3] += row.interaction
    sums[4] += row.total
    sums[5] += row.portfolioWeight
    sums[6] += row.benchmarkWeight
  })
  return columns.map((column: any, index: number) => {
    if (index === 0) return sums[index]
    if (index <= 4) {
      return `${sums[index] >= 0 ? '+' : ''}${(sums[index] * 100).toFixed(2)}%`
    }
    if (index <= 6) {
      return `${(sums[index] * 100).toFixed(2)}%`
    }
    return ''
  })
}

const runAnalysis = () => {
  ElMessage.success('归因分析完成')
}

const initAttributionChart = () => {
  if (!attributionChartRef.value) return
  attributionChart = echarts.init(attributionChartRef.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['配置效应', '选股效应', '交互效应']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: brinsonAttribution.value.map(r => r.sector)
    },
    yAxis: {
      type: 'value',
      name: '收益率%',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '配置效应',
        type: 'bar',
        stack: 'total',
        data: brinsonAttribution.value.map(r => (r.allocation * 100).toFixed(2))
      },
      {
        name: '选股效应',
        type: 'bar',
        stack: 'total',
        data: brinsonAttribution.value.map(r => (r.selection * 100).toFixed(2))
      },
      {
        name: '交互效应',
        type: 'bar',
        stack: 'total',
        data: brinsonAttribution.value.map(r => (r.interaction * 100).toFixed(2))
      }
    ]
  }

  attributionChart.setOption(option)
}

const initSectorChart = () => {
  if (!sectorChartRef.value) return
  sectorChart = echarts.init(sectorChartRef.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '行业配置贡献',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: brinsonAttribution.value.map(r => ({
          value: Math.abs(r.total * 100),
          name: r.sector
        }))
      }
    ]
  }

  sectorChart.setOption(option)
}

const initRiskChart = () => {
  if (!riskChartRef.value) return
  riskChart = echarts.init(riskChartRef.value)
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: '风险归因',
        type: 'pie',
        radius: '60%',
        data: riskAttribution.value.map(r => ({
          value: r.proportion,
          name: r.factor
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  riskChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initAttributionChart()
    initSectorChart()
    initRiskChart()
  })
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    attributionChart?.resize()
    sectorChart?.resize()
    riskChart?.resize()
  })
})
</script>

<style scoped>
.attribution-analysis-container {
  padding: 20px;
}

.config-card,
.summary-card,
.attribution-card,
.risk-card {
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 15px;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
}

.summary-value.profit {
  color: #67C23A;
}

.summary-value.loss {
  color: #F56C6C;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 350px;
  width: 100%;
}

@media (max-width: 768px) {
  .attribution-analysis-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 250px;
  }
}
</style>

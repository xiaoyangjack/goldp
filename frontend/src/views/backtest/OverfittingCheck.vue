<template>
  <div class="overfitting-check-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>过拟合检验配置</span>
          <el-button type="primary" @click="startCheck" :disabled="checking">
            <el-icon><VideoPlay /></el-icon>
            {{ checking ? '检验中...' : '开始检验' }}
          </el-button>
        </div>
      </template>
      <el-form :model="checkForm" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="检验方法">
              <el-select v-model="checkForm.method" style="width: 100%;">
                <el-option label="样本外测试" value="out-of-sample" />
                <el-option label="交叉验证" value="cross-validation" />
                <el-option label="白噪声检验" value="white-noise" />
                <el-option label="组合检验" value="combination" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="回测策略">
              <el-select v-model="checkForm.strategy" style="width: 100%;">
                <el-option label="双均线策略" value="dual-ma" />
                <el-option label="MACD策略" value="macd" />
                <el-option label="RSI策略" value="rsi" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="显著水平">
              <el-select v-model="checkForm.significance" style="width: 100%;">
                <el-option label="99% (0.01)" value="0.01" />
                <el-option label="95% (0.05)" value="0.05" />
                <el-option label="90% (0.10)" value="0.10" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="训练集占比">
              <el-slider v-model="checkForm.trainRatio" :min="50" :max="90" :step="5" show-input />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="蒙特卡洛次数">
              <el-input-number v-model="checkForm.monteCarlo" :min="100" :max="10000" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="折数">
              <el-input-number v-model="checkForm.folds" :min="3" :max="20" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="progress-card" style="margin-top: 20px;" v-if="checking">
      <template #header>
        <span>检验进度</span>
      </template>
      <el-progress :percentage="checkProgress" :status="checkStatus" />
      <div class="progress-info">
        <span>当前步骤: {{ currentStep }}</span>
        <span>已完成: {{ completedIterations }} / {{ checkForm.monteCarlo }}</span>
      </div>
    </el-card>

    <el-card class="risk-card" style="margin-top: 20px;">
      <template #header>
        <span>过拟合风险评估</span>
      </template>
      <div class="risk-assessment">
        <div class="risk-indicator" :class="riskLevel">
          <div class="risk-icon">
            <el-icon :size="80">
              <component :is="riskIcon" />
            </el-icon>
          </div>
          <div class="risk-text">
            <div class="risk-level">{{ riskText }}</div>
            <div class="risk-score">风险评分: {{ riskScore }} / 100</div>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="results-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>检验结果</span>
          <el-button type="primary" size="small" @click="exportReport" :disabled="!checkResults">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="样本内外对比" name="comparison">
          <div ref="comparisonChartRef" class="chart-container"></div>
        </el-tab-pane>
        
        <el-tab-pane label="蒙特卡洛分布" name="montecarlo">
          <div ref="montecarloChartRef" class="chart-container"></div>
        </el-tab-pane>
        
        <el-tab-pane label="滚动窗口分析" name="rolling">
          <div ref="rollingChartRef" class="chart-container"></div>
        </el-tab-pane>
        
        <el-tab-pane label="检验指标" name="metrics">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="metric-card">
                <template #header>
                  <span>样本内表现</span>
                </template>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="年化收益率">
                    <span :style="{ color: checkResults?.inSample?.return >= 0 ? '#67C23A' : '#F56C6C' }">
                      {{ checkResults?.inSample?.return?.toFixed(2) }}%
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="夏普比率">
                    <el-tag :type="checkResults?.inSample?.sharpe >= 1 ? 'success' : 'warning'">
                      {{ checkResults?.inSample?.sharpe?.toFixed(3) }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="最大回撤">
                    <span>{{ checkResults?.inSample?.maxDrawdown?.toFixed(2) }}%</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="胜率">
                    <span>{{ checkResults?.inSample?.winRate?.toFixed(2) }}%</span>
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="metric-card">
                <template #header>
                  <span>样本外表现</span>
                </template>
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="年化收益率">
                    <span :style="{ color: checkResults?.outSample?.return >= 0 ? '#67C23A' : '#F56C6C' }">
                      {{ checkResults?.outSample?.return?.toFixed(2) }}%
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="夏普比率">
                    <el-tag :type="checkResults?.outSample?.sharpe >= 1 ? 'success' : 'warning'">
                      {{ checkResults?.outSample?.sharpe?.toFixed(3) }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="最大回撤">
                    <span>{{ checkResults?.outSample?.maxDrawdown?.toFixed(2) }}%</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="胜率">
                    <span>{{ checkResults?.outSample?.winRate?.toFixed(2) }}%</span>
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>
            </el-col>
          </el-row>
          
          <el-divider content-position="left">表现衰减</el-divider>
          <el-table :data="decayMetrics" stripe style="width: 100%; margin-top: 20px;">
            <el-table-column prop="metric" label="指标" />
            <el-table-column prop="inSample" label="样本内" />
            <el-table-column prop="outSample" label="样本外" />
            <el-table-column prop="decay" label="衰减">
              <template #default="{ row }">
                <el-tag :type="row.decay >= 0 ? 'success' : 'danger'">
                  {{ row.decay >= 0 ? '+' : '' }}{{ row.decay.toFixed(2) }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === '正常' ? 'success' : row.status === '警告' ? 'warning' : 'danger'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="检验结论" name="conclusion">
          <el-alert
            :title="conclusionTitle"
            :type="conclusionType"
            :description="conclusionDescription"
            show-icon
            :closable="false"
          />
          <div class="conclusion-details">
            <h4>主要发现：</h4>
            <ul>
              <li v-for="(finding, index) in findings" :key="index">{{ finding }}</li>
            </ul>
            <h4>建议措施：</h4>
            <ul>
              <li v-for="(suggestion, index) in suggestions" :key="index">{{ suggestion }}</li>
            </ul>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { VideoPlay, Download, SuccessFilled, WarningFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('comparison')
const checking = ref(false)
const checkProgress = ref(0)
const checkStatus = ref('')
const currentStep = ref('初始化')
const completedIterations = ref(0)

const comparisonChartRef = ref<HTMLElement>()
const montecarloChartRef = ref<HTMLElement>()
const rollingChartRef = ref<HTMLElement>()
let comparisonChart: echarts.ECharts | null = null
let montecarloChart: echarts.ECharts | null = null
let rollingChart: echarts.ECharts | null = null

const checkForm = ref({
  method: 'out-of-sample',
  strategy: 'dual-ma',
  significance: '0.05',
  trainRatio: 70,
  monteCarlo: 1000,
  folds: 5
})

const checkResults = ref({
  inSample: {
    return: 25.3,
    sharpe: 1.65,
    maxDrawdown: -12.5,
    winRate: 58.2
  },
  outSample: {
    return: 12.8,
    sharpe: 0.95,
    maxDrawdown: -18.3,
    winRate: 51.5
  }
})

const decayMetrics = ref([
  { metric: '年化收益率', inSample: '25.30%', outSample: '12.80%', decay: -49.4, status: '警告' },
  { metric: '夏普比率', inSample: '1.65', outSample: '0.95', decay: -42.4, status: '警告' },
  { metric: '最大回撤', inSample: '-12.50%', outSample: '-18.30%', decay: -46.4, status: '危险' },
  { metric: '胜率', inSample: '58.20%', outSample: '51.50%', decay: -11.5, status: '正常' }
])

const riskScore = ref(62)
const riskLevel = computed(() => {
  if (riskScore.value < 40) return 'low'
  if (riskScore.value < 70) return 'medium'
  return 'high'
})
const riskIcon = computed(() => {
  if (riskScore.value < 40) return SuccessFilled
  if (riskScore.value < 70) return WarningFilled
  return CircleCloseFilled
})
const riskText = computed(() => {
  if (riskScore.value < 40) return '低风险'
  if (riskScore.value < 70) return '中等风险'
  return '高风险'
})

const conclusionTitle = computed(() => {
  if (riskScore.value < 40) return '策略稳健，过拟合风险较低'
  if (riskScore.value < 70) return '存在一定过拟合风险，建议优化'
  return '过拟合风险较高，需重新审视策略'
})
const conclusionType = computed(() => {
  if (riskScore.value < 40) return 'success'
  if (riskScore.value < 70) return 'warning'
  return 'error'
})
const conclusionDescription = computed(() => {
  if (riskScore.value < 40) return '样本内外表现一致，策略具有较好的泛化能力。'
  if (riskScore.value < 70) return '样本外表现有所衰减，但仍具有一定盈利能力。'
  return '样本外表现显著恶化，策略可能过度拟合历史数据。'
})

const findings = ref([
  '样本内夏普比率1.65，样本外降至0.95，衰减幅度42.4%',
  '最大回撤从12.5%扩大至18.3%，风险控制能力下降',
  '年化收益率衰减接近50%，策略在新市场环境下表现不佳',
  '蒙特卡洛检验p值为0.08，接近显著水平'
])

const suggestions = ref([
  '简化策略逻辑，减少参数数量',
  '增加样本外测试时间长度',
  '考虑使用更长的历史数据进行回测',
  '实施更严格的止损机制',
  '考虑组合多个低相关性策略'
])

const startCheck = () => {
  checking.value = true
  checkProgress.value = 0
  checkStatus.value = ''
  currentStep.value = '数据准备'
  completedIterations.value = 0
  
  const steps = ['数据准备', '样本划分', '策略回测', '蒙特卡洛模拟', '统计检验', '生成报告']
  let stepIndex = 0
  
  const interval = setInterval(() => {
    if (checkProgress.value >= 100) {
      clearInterval(interval)
      checking.value = false
      checkStatus.value = 'success'
      ElMessage.success('过拟合检验完成')
      return
    }
    
    checkProgress.value += Math.floor(Math.random() * 3)
    completedIterations.value = Math.floor((checkProgress.value / 100) * checkForm.value.monteCarlo)
    
    stepIndex = Math.floor((checkProgress.value / 100) * steps.length)
    currentStep.value = steps[Math.min(stepIndex, steps.length - 1)]
  }, 150)
}

const exportReport = () => {
  ElMessage.success('报告导出成功')
}

const initComparisonChart = () => {
  if (!comparisonChartRef.value) return
  comparisonChart = echarts.init(comparisonChartRef.value)
  
  const dates = []
  const inSampleData = []
  const outSampleData = []
  let inValue = 1
  let outValue = 1
  
  for (let i = 0; i < 252; i++) {
    dates.push(`2023-${String(Math.floor(i/21) + 1).padStart(2, '0')}-${String(i%21 + 1).padStart(2, '0')}`)
    const inReturn = 0.001 + Math.random() * 0.02
    const outReturn = i < 176 ? null : (0.0005 + Math.random() * 0.025)
    inValue *= (1 + inReturn)
    inSampleData.push(parseFloat((inValue - 1).toFixed(3)))
    if (outReturn !== null) {
      outValue *= (1 + outReturn)
      outSampleData.push(parseFloat((outValue - 1).toFixed(3)))
    } else {
      outSampleData.push(null)
    }
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['样本内', '样本外'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        formatter: (value: string) => value.substring(5)
      }
    },
    yAxis: {
      type: 'value',
      name: '累积收益率',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '样本内',
        type: 'line',
        data: inSampleData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '样本外',
        type: 'line',
        data: outSampleData,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#E6A23C'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
            { offset: 1, color: 'rgba(230, 162, 60, 0.05)' }
          ])
        }
      }
    ],
    visualMap: {
      show: false,
      pieces: [{
        lte: 0,
        color: '#F56C6C'
      }, {
        gt: 0,
        color: '#67C23A'
      }]
    }
  }

  comparisonChart.setOption(option)
}

const initMontecarloChart = () => {
  if (!montecarloChartRef.value) return
  montecarloChart = echarts.init(montecarloChartRef.value)
  
  const data = []
  for (let i = 0; i < 1000; i++) {
    const value = -0.5 + Math.random() * 1.5
    data.push(parseFloat(value.toFixed(3)))
  }
  
  const bins = 50
  const histogram = new Array(bins).fill(0)
  const min = Math.min(...data)
  const max = Math.max(...data)
  const binWidth = (max - min) / bins
  
  data.forEach(value => {
    const binIndex = Math.min(Math.floor((value - min) / binWidth), bins - 1)
    histogram[binIndex]++
  })
  
  const binCenters = []
  for (let i = 0; i < bins; i++) {
    binCenters.push(parseFloat((min + (i + 0.5) * binWidth).toFixed(3)))
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: binCenters,
      name: '夏普比率',
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '频数'
    },
    series: [{
      name: '频数',
      type: 'bar',
      data: histogram,
      itemStyle: {
        color: (params: any) => {
          const x = parseFloat(binCenters[params.dataIndex])
          if (x < 0.95) return '#909399'
          if (x < 1.65) return '#E6A23C'
          return '#67C23A'
        }
      }
    }],
    markLine: {
      data: [
        { xAxis: 0.95, name: '样本外值' },
        { xAxis: 1.65, name: '样本内值' }
      ],
      lineStyle: {
        color: '#F56C6C',
        type: 'dashed'
      },
      label: {
        formatter: '{b}'
      }
    }
  }

  montecarloChart.setOption(option)
}

const initRollingChart = () => {
  if (!rollingChartRef.value) return
  rollingChart = echarts.init(rollingChartRef.value)
  
  const windows = []
  const sharpeData = []
  const returnData = []
  
  for (let i = 0; i < 52; i++) {
    windows.push(`W${i + 1}`)
    sharpeData.push(parseFloat((0.5 + Math.random() * 1.5).toFixed(3)))
    returnData.push(parseFloat((-5 + Math.random() * 20).toFixed(2)))
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['滚动夏普', '滚动收益率'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: windows
    },
    yAxis: [
      {
        type: 'value',
        name: '夏普比率',
        position: 'left'
      },
      {
        type: 'value',
        name: '收益率%',
        position: 'right'
      }
    ],
    series: [
      {
        name: '滚动夏普',
        type: 'line',
        data: sharpeData,
        smooth: true,
        yAxisIndex: 0,
        lineStyle: {
          width: 2,
          color: '#409EFF'
        },
        markLine: {
          data: [{ yAxis: 1, name: '基准线' }],
          lineStyle: {
            color: '#909399',
            type: 'dashed'
          }
        }
      },
      {
        name: '滚动收益率',
        type: 'bar',
        data: returnData,
        yAxisIndex: 1,
        itemStyle: {
          color: (params: any) => params.value >= 0 ? '#67C23A' : '#F56C6C'
        }
      }
    ]
  }

  rollingChart.setOption(option)
}

const initAllCharts = () => {
  nextTick(() => {
    initComparisonChart()
    initMontecarloChart()
    initRollingChart()
  })
}

onMounted(() => {
  initAllCharts()
  
  window.addEventListener('resize', () => {
    comparisonChart?.resize()
    montecarloChart?.resize()
    rollingChart?.resize()
  })
})
</script>

<style scoped>
.overfitting-check-container {
  padding: 20px;
}

.config-card,
.progress-card,
.risk-card,
.results-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: #606266;
}

.risk-assessment {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.risk-indicator {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 30px;
  border-radius: 12px;
}

.risk-indicator.low {
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border: 2px solid #67C23A;
}

.risk-indicator.medium {
  background: linear-gradient(135deg, #fffbe6 0%, #fff3cd 100%);
  border: 2px solid #E6A23C;
}

.risk-indicator.high {
  background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
  border: 2px solid #F56C6C;
}

.risk-indicator.low .risk-icon {
  color: #67C23A;
}

.risk-indicator.medium .risk-icon {
  color: #E6A23C;
}

.risk-indicator.high .risk-icon {
  color: #F56C6C;
}

.risk-text {
  text-align: left;
}

.risk-level {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 10px;
}

.risk-indicator.low .risk-level {
  color: #67C23A;
}

.risk-indicator.medium .risk-level {
  color: #E6A23C;
}

.risk-indicator.high .risk-level {
  color: #F56C6C;
}

.risk-score {
  font-size: 18px;
  color: #606266;
}

.metric-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.conclusion-details {
  margin-top: 20px;
}

.conclusion-details h4 {
  margin: 15px 0 10px;
  color: #303133;
}

.conclusion-details ul {
  padding-left: 20px;
}

.conclusion-details li {
  margin: 8px 0;
  color: #606266;
}

@media (max-width: 768px) {
  .overfitting-check-container {
    padding: 10px;
  }
  
  .chart-container {
    height: 300px;
  }
  
  .risk-indicator {
    flex-direction: column;
    text-align: center;
  }
  
  .risk-text {
    text-align: center;
  }
}
</style>

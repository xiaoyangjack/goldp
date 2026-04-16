<template>
  <div class="strategy-debug-container">
    <el-card class="control-card">
      <template #header>
        <div class="card-header">
          <span>调试控制</span>
          <el-button-group>
            <el-button type="primary" :icon="VideoPlay" @click="startDebug" :disabled="debugging">开始调试</el-button>
            <el-button type="warning" :icon="VideoPause" @click="pauseDebug" :disabled="!debugging || paused">暂停</el-button>
            <el-button type="success" :icon="VideoPlay" @click="resumeDebug" :disabled="!paused">继续</el-button>
            <el-button type="danger" :icon="VideoStop" @click="stopDebug" :disabled="!debugging">停止</el-button>
          </el-button-group>
        </div>
      </template>
      <el-form :inline="true">
        <el-form-item label="调试模式">
          <el-radio-group v-model="debugMode">
            <el-radio-button label="step">单步执行</el-radio-button>
            <el-radio-button label="continuous">连续执行</el-radio-button>
            <el-radio-button label="breakpoint">断点调试</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="执行速度" v-if="debugMode === 'continuous'">
          <el-slider v-model="executionSpeed" :min="1" :max="10" show-input style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="stepForward" :disabled="!debugging || !paused" v-if="debugMode === 'step'">
            <el-icon><Right /></el-icon>
            下一步
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="code-card">
          <template #header>
            <span>策略代码</span>
          </template>
          <div class="code-editor-wrapper">
            <div class="line-numbers">
              <div v-for="n in codeLines" :key="n" :class="{ 'current-line': n === currentLine, 'breakpoint': breakpoints.includes(n) }" @click="toggleBreakpoint(n)">
                {{ n }}
              </div>
            </div>
            <textarea
              ref="codeEditorRef"
              v-model="strategyCode"
              class="code-editor"
              readonly
              :style="{ height: `${codeLines * 24}px` }"
            />
          </div>
        </el-card>

        <el-card class="log-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>调试日志</span>
              <el-button-group>
                <el-radio-group v-model="logLevel" size="small">
                  <el-radio-button value="all">全部</el-radio-button>
                  <el-radio-button value="info">信息</el-radio-button>
                  <el-radio-button value="warning">警告</el-radio-button>
                  <el-radio-button value="error">错误</el-radio-button>
                </el-radio-group>
                <el-button size="small" @click="clearLogs">清空</el-button>
              </el-button-group>
            </div>
          </template>
          <div class="log-container" ref="logContainerRef">
            <div v-for="(log, index) in filteredLogs" :key="index" :class="['log-item', `log-${log.level}`]">
              <span class="log-time">[{{ log.time }}]</span>
              <span class="log-level">[{{ log.level.toUpperCase() }}]</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <el-empty v-if="filteredLogs.length === 0" description="暂无日志" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="status-card">
          <template #header>
            <span>执行状态</span>
          </template>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="当前状态">
              <el-tag :type="statusType">{{ statusText }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="当前步骤">
              {{ currentStep }} / {{ totalSteps }}
            </el-descriptions-item>
            <el-descriptions-item label="当前日期">
              {{ currentDate }}
            </el-descriptions-item>
            <el-descriptions-item label="当前价格">
              {{ currentPrice }}
            </el-descriptions-item>
          </el-descriptions>
          <el-progress :percentage="progressPercentage" style="margin-top: 20px;" />
        </el-card>

        <el-card class="variables-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>变量监视</span>
              <el-button type="primary" size="small" link @click="addWatchVariable">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
          </template>
          <el-table :data="watchVariables" size="small" style="width: 100%">
            <el-table-column prop="name" label="变量名" />
            <el-table-column prop="value" label="值" />
            <el-table-column prop="type" label="类型" width="80" />
            <el-table-column label="操作" width="60">
              <template #default="scope">
                <el-button type="danger" size="small" link @click="removeWatchVariable(scope.$index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="orders-card" style="margin-top: 20px;">
          <template #header>
            <span>交易信号</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="signal in tradeSignals"
              :key="signal.id"
              :timestamp="signal.date"
              :type="signal.type === 'buy' ? 'success' : 'danger'"
            >
              <div class="signal-item">
                <div class="signal-type">
                  <el-tag :type="signal.type === 'buy' ? 'success' : 'danger'" size="small">
                    {{ signal.type === 'buy' ? '买入' : '卖出' }}
                  </el-tag>
                </div>
                <div class="signal-price">价格: {{ signal.price }}</div>
                <div class="signal-amount">数量: {{ signal.amount }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <el-card class="equity-card" style="margin-top: 20px;">
          <template #header>
            <span>资金曲线</span>
          </template>
          <div ref="equityChartRef" class="equity-chart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { VideoPlay, VideoPause, VideoStop, Right, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElInput } from 'element-plus'
import * as echarts from 'echarts'

const debugMode = ref('step')
const debugging = ref(false)
const paused = ref(false)
const executionSpeed = ref(5)
const currentLine = ref(1)
const logLevel = ref('all')
const progressPercentage = ref(0)
const currentStep = ref(0)
const totalSteps = ref(100)
const currentDate = ref('2024-01-01')
const currentPrice = ref('200.50')

const strategyCode = ref(`def initialize(context):
    context.short_ma_period = 5
    context.long_ma_period = 20
    context.position = 0

def handle_data(context, data):
    close = data['close']
    
    short_ma = talib.SMA(close, context.short_ma_period)
    long_ma = talib.SMA(close, context.long_ma_period)
    
    if short_ma[-1] > long_ma[-1] and short_ma[-2] <= long_ma[-2]:
        if context.position == 0:
            order_target_percent(data, 0.3)
            context.position = 1
            log.info('金叉信号，买入')
    
    elif short_ma[-1] < long_ma[-1] and short_ma[-2] >= long_ma[-2]:
        if context.position == 1:
            order_target_percent(data, 0)
            context.position = 0
            log.info('死叉信号，卖出')`)

const codeLines = computed(() => strategyCode.value.split('\n').length)
const breakpoints = ref<number[]>([5, 10])

const logs = ref<any[]>([])
const watchVariables = ref([
  { name: 'close', value: '200.50', type: 'float' },
  { name: 'short_ma', value: '199.80', type: 'float' },
  { name: 'long_ma', value: '198.50', type: 'float' },
  { name: 'position', value: '0', type: 'int' }
])

const tradeSignals = ref([
  { id: 1, type: 'buy', date: '2024-01-15', price: '198.50', amount: 100 },
  { id: 2, type: 'sell', date: '2024-02-20', price: '205.30', amount: 100 },
  { id: 3, type: 'buy', date: '2024-03-10', price: '199.80', amount: 100 }
])

const equityChartRef = ref<HTMLElement>()
let equityChart: echarts.ECharts | null = null

const statusText = computed(() => {
  if (!debugging.value) return '等待开始'
  if (paused.value) return '已暂停'
  return '运行中'
})

const statusType = computed(() => {
  if (!debugging.value) return 'info'
  if (paused.value) return 'warning'
  return 'success'
})

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') return logs.value
  return logs.value.filter(log => log.level === logLevel.value)
})

const addLog = (level: string, message: string) => {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({ time, level, message })
  nextTick(() => {
    const container = document.querySelector('.log-container')
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

const toggleBreakpoint = (line: number) => {
  const index = breakpoints.value.indexOf(line)
  if (index > -1) {
    breakpoints.value.splice(index, 1)
  } else {
    breakpoints.value.push(line)
  }
}

const startDebug = () => {
  debugging.value = true
  paused.value = debugMode.value === 'step'
  currentStep.value = 0
  progressPercentage.value = 0
  logs.value = []
  addLog('info', '调试开始')
  addLog('info', '初始化策略参数')
  ElMessage.success('调试已开始')
  
  if (debugMode.value === 'continuous') {
    runContinuous()
  }
}

const pauseDebug = () => {
  paused.value = true
  addLog('info', '调试已暂停')
}

const resumeDebug = () => {
  paused.value = false
  addLog('info', '调试继续')
  if (debugMode.value === 'continuous') {
    runContinuous()
  }
}

const stopDebug = () => {
  debugging.value = false
  paused.value = false
  addLog('info', '调试已停止')
  ElMessage.info('调试已停止')
}

const stepForward = () => {
  if (currentStep.value < totalSteps.value) {
    currentStep.value++
    progressPercentage.value = Math.round((currentStep.value / totalSteps.value) * 100)
    currentLine.value = (currentLine.value % codeLines.value) + 1
    
    if (currentStep.value % 10 === 0) {
      addLog('info', `执行步骤 ${currentStep.value}`)
    }
    if (currentStep.value % 25 === 0) {
      addLog('warning', `检查点 ${currentStep.value}`)
    }
  }
}

const runContinuous = () => {
  const interval = 1000 / executionSpeed.value
  const timer = setInterval(() => {
    if (!debugging.value || paused.value) {
      clearInterval(timer)
      return
    }
    if (currentStep.value >= totalSteps.value) {
      clearInterval(timer)
      debugging.value = false
      addLog('info', '调试完成')
      ElMessage.success('调试完成')
      return
    }
    stepForward()
  }, interval)
}

const clearLogs = () => {
  logs.value = []
}

const addWatchVariable = () => {
  ElMessage.info('添加监视变量')
}

const removeWatchVariable = (index: number) => {
  watchVariables.value.splice(index, 1)
}

const initEquityChart = () => {
  if (!equityChartRef.value) return
  equityChart = echarts.init(equityChartRef.value)
  
  const dates = []
  const equity = []
  let value = 100000
  for (let i = 0; i < 60; i++) {
    const date = new Date('2024-01-01')
    date.setDate(date.getDate() + i)
    dates.push(date.toISOString().split('T')[0])
    value += (Math.random() - 0.45) * 1000
    equity.push(value.toFixed(2))
  }

  const option: echarts.EChartsOption = {
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
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      name: '资金',
      type: 'line',
      data: equity,
      smooth: true,
      areaStyle: {
        opacity: 0.3
      }
    }]
  }

  equityChart.setOption(option)
}

onMounted(() => {
  initEquityChart()
})
</script>

<style scoped>
.strategy-debug-container {
  padding: 20px;
}

.control-card,
.code-card,
.log-card,
.status-card,
.variables-card,
.orders-card,
.equity-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code-editor-wrapper {
  display: flex;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.line-numbers {
  background: #f5f7fa;
  padding: 10px 5px;
  text-align: right;
  user-select: none;
  border-right: 1px solid #dcdfe6;
  min-width: 50px;
}

.line-numbers > div {
  line-height: 24px;
  padding: 0 5px;
  cursor: pointer;
}

.line-numbers .current-line {
  background: #e6f7ff;
  color: #1890ff;
  font-weight: bold;
}

.line-numbers .breakpoint {
  background: #fff1f0;
  color: #f5222d;
}

.line-numbers .breakpoint::before {
  content: '●';
  margin-right: 5px;
}

.code-editor {
  flex: 1;
  padding: 10px;
  border: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 24px;
  resize: none;
  outline: none;
}

.log-container {
  height: 300px;
  overflow-y: auto;
  background: #1e1e1e;
  padding: 10px;
  border-radius: 4px;
}

.log-item {
  margin-bottom: 5px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.log-time {
  color: #888;
  margin-right: 10px;
}

.log-level {
  margin-right: 10px;
}

.log-info .log-level {
  color: #409EFF;
}

.log-warning .log-level {
  color: #E6A23C;
}

.log-error .log-level {
  color: #F56C6C;
}

.log-message {
  color: #fff;
}

.signal-item {
  padding: 5px 0;
}

.signal-type {
  margin-bottom: 5px;
}

.equity-chart {
  height: 200px;
  width: 100%;
}

@media (max-width: 768px) {
  .strategy-debug-container {
    padding: 10px;
  }
}
</style>

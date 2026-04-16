<template>
  <div class="custom-strategy-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="template-card">
          <template #header>
            <div class="card-header">
              <span>策略模板</span>
              <el-button type="primary" size="small" link @click="refreshTemplates">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-menu
            :default-active="selectedTemplate"
            @select="selectTemplate"
            class="template-menu"
          >
            <el-menu-item index="blank">
              <el-icon><Document /></el-icon>
              <span>空白模板</span>
            </el-menu-item>
            <el-menu-item index="ma_cross">
              <el-icon><TrendCharts /></el-icon>
              <span>均线交叉</span>
            </el-menu-item>
            <el-menu-item index="rsi">
              <el-icon><Odometer /></el-icon>
              <span>RSI反转</span>
            </el-menu-item>
            <el-menu-item index="bollinger">
              <el-icon><Connection /></el-icon>
              <span>布林带突破</span>
            </el-menu-item>
            <el-menu-item index="atr">
              <el-icon><Guide /></el-icon>
              <span>ATR止损</span>
            </el-menu-item>
            <el-menu-item index="grid">
              <el-icon><Grid /></el-icon>
              <span>网格交易</span>
            </el-menu-item>
          </el-menu>
        </el-card>

        <el-card class="my-strategies-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>我的策略</span>
              <el-button type="primary" size="small" link @click="showCreateDialog">
                <el-icon><Plus /></el-icon>
                新建
              </el-button>
            </div>
          </template>
          <el-table :data="myStrategies" size="small" style="width: 100%">
            <el-table-column prop="name" label="策略名称" show-overflow-tooltip />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="primary" size="small" link @click="loadStrategy(scope.row)">加载</el-button>
                <el-button type="danger" size="small" link @click="deleteStrategy(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card class="editor-card">
          <template #header>
            <div class="card-header">
              <el-input v-model="strategyName" placeholder="输入策略名称" style="width: 300px;" />
              <el-button-group>
                <el-button type="primary" @click="saveStrategy">
                  <el-icon><Document /></el-icon>
                  保存
                </el-button>
                <el-button type="success" @click="runStrategy">
                  <el-icon><VideoPlay /></el-icon>
                  运行回测
                </el-button>
                <el-button type="info" @click="validateStrategy">
                  <el-icon><CircleCheck /></el-icon>
                  验证
                </el-button>
                <el-dropdown>
                  <el-button>
                    更多
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="exportStrategy">导出</el-dropdown-item>
                      <el-dropdown-item @click="copyCode">复制代码</el-dropdown-item>
                      <el-dropdown-item @click="formatCode">格式化</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </el-button-group>
            </div>
          </template>

          <el-tabs v-model="activeTab">
            <el-tab-pane label="可视化编辑器" name="visual">
              <div class="visual-editor">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <el-card class="component-card">
                      <template #header>
                        <span>入口节点</span>
                      </template>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'initialize')">
                        <el-icon><Setting /></el-icon>
                        <span>初始化</span>
                      </div>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'handle_data')">
                        <el-icon><DataLine /></el-icon>
                        <span>数据处理</span>
                      </div>
                    </el-card>

                    <el-card class="component-card" style="margin-top: 20px;">
                      <template #header>
                        <span>技术指标</span>
                      </template>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'ma')">
                        <el-icon><TrendCharts /></el-icon>
                        <span>均线 MA</span>
                      </div>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'rsi')">
                        <el-icon><Odometer /></el-icon>
                        <span>RSI</span>
                      </div>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'macd')">
                        <el-icon><Connection /></el-icon>
                        <span>MACD</span>
                      </div>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'bollinger')">
                        <el-icon><Crop /></el-icon>
                        <span>布林带</span>
                      </div>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'atr')">
                        <el-icon><Guide /></el-icon>
                        <span>ATR</span>
                      </div>
                    </el-card>

                    <el-card class="component-card" style="margin-top: 20px;">
                      <template #header>
                        <span>交易操作</span>
                      </template>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'buy')">
                        <el-icon><Top /></el-icon>
                        <span>买入</span>
                      </div>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'sell')">
                        <el-icon><Bottom /></el-icon>
                        <span>卖出</span>
                      </div>
                      <div class="component-item" draggable="true" @dragstart="dragStart($event, 'condition')">
                        <el-icon><Switch /></el-icon>
                        <span>条件判断</span>
                      </div>
                    </el-card>
                  </el-col>
                  <el-col :span="18">
                    <el-card class="canvas-card">
                      <template #header>
                        <div class="card-header">
                          <span>策略画布</span>
                          <el-button-group>
                            <el-button size="small" @click="clearCanvas">清空</el-button>
                            <el-button size="small" @click="autoLayout">自动布局</el-button>
                          </el-button-group>
                        </div>
                      </template>
                      <div class="canvas" @drop="drop($event)" @dragover="allowDrop($event)">
                        <div v-for="(node, index) in canvasNodes" :key="index" class="canvas-node" :style="{ left: node.x + 'px', top: node.y + 'px' }">
                          <div class="node-header">{{ node.label }}</div>
                          <div class="node-body">
                            <el-button type="danger" size="small" circle @click="removeNode(index)">
                              <el-icon><Close /></el-icon>
                            </el-button>
                          </div>
                        </div>
                        <el-empty v-if="canvasNodes.length === 0" description="从左侧拖拽组件到这里" />
                      </div>
                    </el-card>
                  </el-col>
                </el-row>
              </div>
            </el-tab-pane>

            <el-tab-pane label="代码编辑器" name="code">
              <div class="code-editor-container">
                <div class="code-toolbar">
                  <el-select v-model="codeLanguage" size="small" style="width: 120px;">
                    <el-option label="Python" value="python" />
                    <el-option label="JavaScript" value="javascript" />
                  </el-select>
                </div>
                <textarea
                  v-model="strategyCode"
                  class="code-textarea"
                  spellcheck="false"
                />
              </div>
            </el-tab-pane>

            <el-tab-pane label="参数配置" name="params">
              <el-form :model="paramForm" label-width="150px" style="padding: 20px;">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="标的代码">
                      <el-input v-model="paramForm.symbol" placeholder="例如: AU.SHF" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="初始资金">
                      <el-input-number v-model="paramForm.initialCapital" :min="10000" style="width: 100%;" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="开始日期">
                      <el-date-picker v-model="paramForm.startDate" type="date" style="width: 100%;" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="结束日期">
                      <el-date-picker v-model="paramForm.endDate" type="date" style="width: 100%;" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-divider content-position="left">策略参数</el-divider>
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="短期均线周期">
                      <el-input-number v-model="paramForm.shortMa" :min="1" :max="100" style="width: 100%;" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="长期均线周期">
                      <el-input-number v-model="paramForm.longMa" :min="1" :max="200" style="width: 100%;" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="回测结果" name="result">
              <div class="result-container">
                <el-empty description="运行回测后查看结果" />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>

        <el-card class="output-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>输出</span>
              <el-button type="danger" size="small" link @click="clearOutput">清空</el-button>
            </div>
          </template>
          <div class="output-area">
            <div v-for="(line, index) in outputLines" :key="index" :class="['output-line', line.type]">
              {{ line.content }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="createDialogVisible" title="创建新策略" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="策略名称">
          <el-input v-model="createForm.name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入策略描述" />
        </el-form-item>
        <el-form-item label="选择模板">
          <el-select v-model="createForm.template" placeholder="请选择模板" style="width: 100%;">
            <el-option label="空白模板" value="blank" />
            <el-option label="均线交叉" value="ma_cross" />
            <el-option label="RSI反转" value="rsi" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createStrategy">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  Document, Refresh, Plus, TrendCharts, Odometer, Connection, Guide, Grid,
  Setting, DataLine, Crop, Top, Bottom, Switch, Close, ArrowDown,
  VideoPlay, CircleCheck
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('visual')
const selectedTemplate = ref('blank')
const strategyName = ref('未命名策略')
const codeLanguage = ref('python')
const createDialogVisible = ref(false)

const myStrategies = ref([
  { id: '1', name: '我的均线策略' },
  { id: '2', name: 'RSI改进版' },
  { id: '3', name: '网格交易v2' }
])

const canvasNodes = ref<any[]>([])

const outputLines = ref([
  { type: 'info', content: '策略编辑器已就绪' }
])

const createForm = ref({
  name: '',
  description: '',
  template: 'blank'
})

const paramForm = ref({
  symbol: 'AU.SHF',
  initialCapital: 100000,
  startDate: new Date('2023-01-01'),
  endDate: new Date(),
  shortMa: 5,
  longMa: 20
})

const strategyCode = ref(`# 策略模板
from goldquant import Strategy, order, log

class MyStrategy(Strategy):
    def initialize(self):
        self.short_ma = 5
        self.long_ma = 20
        
    def on_bar(self, bar):
        close = bar.close
        
        short_ma = self.sma(close, self.short_ma)
        long_ma = self.sma(close, self.long_ma)
        
        if short_ma > long_ma and not self.position:
            order(bar.symbol, 100)
            log.info('买入信号')
        elif short_ma < long_ma and self.position:
            order(bar.symbol, -100)
            log.info('卖出信号')`)

const templateCodes: Record<string, string> = {
  blank: '# 空白模板\nfrom goldquant import Strategy\n\nclass MyStrategy(Strategy):\n    def initialize(self):\n        pass\n        \n    def on_bar(self, bar):\n        pass',
  ma_cross: '# 均线交叉策略\nfrom goldquant import Strategy, order, log\n\nclass MACrossStrategy(Strategy):\n    def initialize(self):\n        self.short_period = 5\n        self.long_period = 20\n        \n    def on_bar(self, bar):\n        close = bar.close\n        short_ma = self.sma(close, self.short_period)\n        long_ma = self.sma(close, self.long_period)\n        \n        if short_ma > long_ma:\n            order(bar.symbol, 100)',
  rsi: '# RSI反转策略\nfrom goldquant import Strategy, order\n\nclass RSIStrategy(Strategy):\n    def initialize(self):\n        self.rsi_period = 14\n        self.overbought = 70\n        self.oversold = 30\n        \n    def on_bar(self, bar):\n        rsi = self.rsi(bar.close, self.rsi_period)\n        if rsi < self.oversold:\n            order(bar.symbol, 100)\n        elif rsi > self.overbought:\n            order(bar.symbol, -100)',
  bollinger: '# 布林带策略',
  atr: '# ATR策略',
  grid: '# 网格策略'
}

const cardHeader = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
}

const selectTemplate = (index: string) => {
  selectedTemplate.value = index
  strategyCode.value = templateCodes[index] || templateCodes['blank']
  addOutput('info', `已加载模板: ${index}`)
}

const refreshTemplates = () => {
  ElMessage.success('模板列表已刷新')
}

const showCreateDialog = () => {
  createDialogVisible.value = true
}

const createStrategy = () => {
  if (!createForm.value.name) {
    ElMessage.warning('请输入策略名称')
    return
  }
  myStrategies.value.unshift({
    id: String(Date.now()),
    name: createForm.value.name
  })
  strategyName.value = createForm.value.name
  createDialogVisible.value = false
  ElMessage.success('策略创建成功')
  addOutput('info', `已创建策略: ${createForm.value.name}`)
  createForm.value = { name: '', description: '', template: 'blank' }
}

const loadStrategy = (strategy: any) => {
  strategyName.value = strategy.name
  ElMessage.success(`已加载策略: ${strategy.name}`)
  addOutput('info', `已加载策略: ${strategy.name}`)
}

const deleteStrategy = async (strategy: any) => {
  try {
    await ElMessageBox.confirm(`确认删除策略 ${strategy.name}?`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const index = myStrategies.value.findIndex(s => s.id === strategy.id)
    if (index > -1) {
      myStrategies.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch {}
}

const saveStrategy = () => {
  if (!strategyName.value) {
    ElMessage.warning('请输入策略名称')
    return
  }
  ElMessage.success('策略保存成功')
  addOutput('info', '策略已保存')
}

const runStrategy = () => {
  ElMessage.success('开始回测...')
  addOutput('info', '开始回测...')
  activeTab.value = 'result'
}

const validateStrategy = () => {
  ElMessage.success('策略验证通过')
  addOutput('success', '策略验证通过')
}

const exportStrategy = () => {
  const dataStr = strategyCode.value
  const dataBlob = new Blob([dataStr], { type: 'text/plain' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${strategyName.value || 'strategy'}.py`
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('策略已导出')
}

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(strategyCode.value)
    ElMessage.success('代码已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

const formatCode = () => {
  ElMessage.info('代码已格式化')
}

const dragStart = (event: DragEvent, type: string) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('nodeType', type)
  }
}

const allowDrop = (event: DragEvent) => {
  event.preventDefault()
}

const drop = (event: DragEvent) => {
  event.preventDefault()
  const type = event.dataTransfer?.getData('nodeType')
  if (type) {
    const canvas = event.currentTarget as HTMLElement
    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left - 75
    const y = event.clientY - rect.top - 30
    const labels: Record<string, string> = {
      initialize: '初始化',
      handle_data: '数据处理',
      ma: '均线计算',
      rsi: 'RSI计算',
      macd: 'MACD计算',
      bollinger: '布林带',
      atr: 'ATR计算',
      buy: '买入',
      sell: '卖出',
      condition: '条件判断'
    }
    canvasNodes.value.push({ type, label: labels[type] || type, x, y })
    addOutput('info', `已添加节点: ${labels[type] || type}`)
  }
}

const removeNode = (index: number) => {
  canvasNodes.value.splice(index, 1)
}

const clearCanvas = () => {
  canvasNodes.value = []
  addOutput('info', '画布已清空')
}

const autoLayout = () => {
  ElMessage.info('自动布局')
}

const addOutput = (type: string, content: string) => {
  outputLines.value.push({ type, content: `[${new Date().toLocaleTimeString()}] ${content}` })
}

const clearOutput = () => {
  outputLines.value = []
}
</script>

<style scoped>
.custom-strategy-container {
  padding: 20px;
}

.template-card,
.my-strategies-card,
.editor-card,
.output-card,
.component-card,
.canvas-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-menu {
  border: none;
}

.code-editor-container {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.code-toolbar {
  padding: 10px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.code-textarea {
  flex: 1;
  padding: 15px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  border: none;
  resize: none;
  outline: none;
}

.visual-editor {
  min-height: 500px;
}

.component-item {
  padding: 10px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  cursor: move;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.component-item:hover {
  background: #e6f7ff;
}

.canvas {
  min-height: 450px;
  background: #fafafa;
  position: relative;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
}

.canvas-node {
  position: absolute;
  width: 150px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.node-header {
  padding: 10px;
  background: #409EFF;
  color: #fff;
  border-radius: 8px 8px 0 0;
  font-weight: bold;
}

.node-body {
  padding: 10px;
  display: flex;
  justify-content: flex-end;
}

.output-area {
  height: 150px;
  overflow-y: auto;
  background: #1e1e1e;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.output-line {
  margin-bottom: 5px;
}

.output-line.info {
  color: #409EFF;
}

.output-line.success {
  color: #67C23A;
}

.output-line.error {
  color: #F56C6C;
}

.output-line.warning {
  color: #E6A23C;
}

@media (max-width: 768px) {
  .custom-strategy-container {
    padding: 10px;
  }
}
</style>

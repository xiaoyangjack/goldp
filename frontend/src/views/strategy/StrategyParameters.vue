<template>
  <div class="strategy-parameters-container">
    <el-card class="strategy-select-card">
      <template #header>
        <span>选择策略</span>
      </template>
      <el-form :inline="true" :model="selectForm">
        <el-form-item label="策略模板">
          <el-select v-model="selectForm.template" placeholder="请选择策略模板" style="width: 300px;">
            <el-option v-for="tpl in strategyTemplates" :key="tpl.id" :label="tpl.name" :value="tpl.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadTemplate">加载模板</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="params-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>策略参数配置</span>
          <el-button-group>
            <el-button type="primary" size="small" @click="handleSave">
              <el-icon><Document /></el-icon>
              保存配置
            </el-button>
            <el-button type="success" size="small" @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置默认
            </el-button>
            <el-button type="info" size="small" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出配置
            </el-button>
          </el-button-group>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基础参数" name="basic">
          <el-form :model="paramForm" label-width="150px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="策略名称">
                  <el-input v-model="paramForm.strategyName" placeholder="请输入策略名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="标的代码">
                  <el-input v-model="paramForm.symbol" placeholder="例如: AU.SHF" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="回测开始日期">
                  <el-date-picker v-model="paramForm.startDate" type="date" placeholder="选择日期" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="回测结束日期">
                  <el-date-picker v-model="paramForm.endDate" type="date" placeholder="选择日期" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="初始资金">
                  <el-input-number v-model="paramForm.initialCapital" :min="10000" :step="10000" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="交易手续费(%)">
                  <el-input-number v-model="paramForm.commission" :min="0" :max="10" :step="0.01" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="滑点(%)">
                  <el-input-number v-model="paramForm.slippage" :min="0" :max="5" :step="0.01" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="单标的仓位上限(%)">
                  <el-input-number v-model="paramForm.maxPosition" :min="0" :max="100" :step="5" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="技术指标参数" name="technical">
          <el-form :model="technicalForm" label-width="150px">
            <el-divider content-position="left">均线参数</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="短期均线周期">
                  <el-input-number v-model="technicalForm.shortMaPeriod" :min="1" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="长期均线周期">
                  <el-input-number v-model="technicalForm.longMaPeriod" :min="1" :max="200" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">RSI参数</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="RSI周期">
                  <el-input-number v-model="technicalForm.rsiPeriod" :min="1" :max="50" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="RSI超买阈值">
                  <el-input-number v-model="technicalForm.rsiOverbought" :min="50" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="RSI超卖阈值">
                  <el-input-number v-model="technicalForm.rsiOversold" :min="0" :max="50" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">布林带参数</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="布林带周期">
                  <el-input-number v-model="technicalForm.bbPeriod" :min="1" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="标准差倍数">
                  <el-input-number v-model="technicalForm.bbStdDev" :min="0.5" :max="5" :step="0.1" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">ATR参数</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="ATR周期">
                  <el-input-number v-model="technicalForm.atrPeriod" :min="1" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="止损倍数">
                  <el-input-number v-model="technicalForm.stopLossMultiplier" :min="0.5" :max="10" :step="0.1" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="风控参数" name="risk">
          <el-form :model="riskForm" label-width="180px">
            <el-divider content-position="left">止损止盈</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="单笔止损比例(%)">
                  <el-input-number v-model="riskForm.stopLossPercent" :min="0" :max="50" :step="0.1" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="单笔止盈比例(%)">
                  <el-input-number v-model="riskForm.takeProfitPercent" :min="0" :max="100" :step="0.1" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">仓位管理</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="最大持仓数">
                  <el-input-number v-model="riskForm.maxPositions" :min="1" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="单笔最大仓位(%)">
                  <el-input-number v-model="riskForm.maxSinglePosition" :min="1" :max="100" :step="1" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">最大回撤控制</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="最大回撤阈值(%)">
                  <el-input-number v-model="riskForm.maxDrawdown" :min="1" :max="100" :step="1" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="回撤降仓比例(%)">
                  <el-input-number v-model="riskForm.drawdownReduceRatio" :min="0" :max="100" :step="5" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">每日风险</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="每日最大亏损(%)">
                  <el-input-number v-model="riskForm.dailyMaxLoss" :min="0.1" :max="20" :step="0.1" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="每日最大交易次数">
                  <el-input-number v-model="riskForm.dailyMaxTrades" :min="1" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="参数预览" name="preview">
          <div class="preview-container">
            <el-button type="primary" size="small" @click="copyConfig" style="margin-bottom: 20px;">
              <el-icon><DocumentCopy /></el-icon>
              复制配置
            </el-button>
            <pre><code>{{ JSON.stringify(fullConfig, null, 2) }}</code></pre>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Document, Refresh, Download, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

const strategyTemplates = [
  { id: 'ma_cross', name: '均线交叉策略' },
  { id: 'rsi_reversal', name: 'RSI反转策略' },
  { id: 'bollinger_breakout', name: '布林带突破策略' },
  { id: 'atr_trailing_stop', name: 'ATR跟踪止损策略' },
  { id: 'grid_trading', name: '网格交易策略' }
]

const selectForm = ref({
  template: ''
})

const paramForm = ref({
  strategyName: '我的策略',
  symbol: 'AU.SHF',
  startDate: new Date('2023-01-01'),
  endDate: new Date(),
  initialCapital: 100000,
  commission: 0.03,
  slippage: 0.01,
  maxPosition: 30
})

const technicalForm = ref({
  shortMaPeriod: 5,
  longMaPeriod: 20,
  rsiPeriod: 14,
  rsiOverbought: 70,
  rsiOversold: 30,
  bbPeriod: 20,
  bbStdDev: 2,
  atrPeriod: 14,
  stopLossMultiplier: 2
})

const riskForm = ref({
  stopLossPercent: 5,
  takeProfitPercent: 10,
  maxPositions: 5,
  maxSinglePosition: 20,
  maxDrawdown: 20,
  drawdownReduceRatio: 50,
  dailyMaxLoss: 5,
  dailyMaxTrades: 10
})

const fullConfig = computed(() => ({
  basic: paramForm.value,
  technical: technicalForm.value,
  risk: riskForm.value
}))

const loadTemplate = () => {
  if (!selectForm.value.template) {
    ElMessage.warning('请先选择策略模板')
    return
  }
  ElMessage.success('模板加载成功')
}

const handleSave = () => {
  ElMessage.success('参数配置已保存')
}

const handleReset = () => {
  paramForm.value = {
    strategyName: '我的策略',
    symbol: 'AU.SHF',
    startDate: new Date('2023-01-01'),
    endDate: new Date(),
    initialCapital: 100000,
    commission: 0.03,
    slippage: 0.01,
    maxPosition: 30
  }
  technicalForm.value = {
    shortMaPeriod: 5,
    longMaPeriod: 20,
    rsiPeriod: 14,
    rsiOverbought: 70,
    rsiOversold: 30,
    bbPeriod: 20,
    bbStdDev: 2,
    atrPeriod: 14,
    stopLossMultiplier: 2
  }
  riskForm.value = {
    stopLossPercent: 5,
    takeProfitPercent: 10,
    maxPositions: 5,
    maxSinglePosition: 20,
    maxDrawdown: 20,
    drawdownReduceRatio: 50,
    dailyMaxLoss: 5,
    dailyMaxTrades: 10
  }
  ElMessage.info('已重置为默认参数')
}

const handleExport = () => {
  const dataStr = JSON.stringify(fullConfig.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'strategy_config.json'
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('配置导出成功')
}

const copyConfig = async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(fullConfig.value, null, 2))
    ElMessage.success('配置已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.strategy-parameters-container {
  padding: 20px;
}

.strategy-select-card,
.params-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-container {
  padding: 10px 0;
}

.preview-container pre {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .strategy-parameters-container {
    padding: 10px;
  }
}
</style>

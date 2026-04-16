<template>
  <div class="strategy-editor-container">
    <el-card class="editor-card">
      <template #header>
        <div class="card-header">
          <span>策略编辑器</span>
          <div class="header-actions">
            <el-button size="small" @click="saveStrategy">
              <el-icon><Document /></el-icon>
              保存
            </el-button>
            <el-button type="primary" size="small" @click="runStrategy">
              <el-icon><VideoPlay /></el-icon>
              运行
            </el-button>
          </div>
        </div>
      </template>
      <div class="editor-content">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="template-card">
              <template #header>策略模板</template>
              <div class="template-list">
                <div
                  v-for="template in templates"
                  :key="template.id"
                  class="template-item"
                  :class="{ active: selectedTemplate === template.id }"
                  @click="selectTemplate(template)"
                >
                  <div class="template-name">{{ template.name }}</div>
                  <div class="template-desc">{{ template.description }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="18">
            <el-card class="code-card">
              <template #header>
                <div class="card-header">
                  <el-input
                    v-model="strategyName"
                    placeholder="策略名称"
                    style="width: 300px;"
                  />
                  <el-select v-model="strategyType" placeholder="策略类型" style="width: 150px; margin-left: 10px;">
                    <el-option label="选股策略" value="stock" />
                    <el-option label="择时策略" value="timing" />
                    <el-option label="套利策略" value="arbitrage" />
                  </el-select>
                </div>
              </template>
              <div class="code-editor">
                <textarea
                  v-model="strategyCode"
                  class="code-textarea"
                  placeholder="# 在此编写策略代码"
                ></textarea>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card v-if="showOutput" class="output-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>运行日志</span>
              <el-button type="danger" size="small" @click="clearOutput">清空</el-button>
            </div>
          </template>
          <div class="output-content">
            <div v-for="(log, index) in logs" :key="index" class="log-item">
              <span class="log-time">{{ log.time }}</span>
              <el-tag :type="log.type" size="small" style="margin-right: 10px;">
                {{ log.type === 'success' ? '成功' : log.type === 'error' ? '错误' : '信息' }}
              </el-tag>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Document, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const strategyName = ref('我的策略')
const strategyType = ref('stock')
const strategyCode = ref(`# 策略示例
import numpy as np
import pandas as pd

def initialize(context):
    # 初始化策略
    context.universe = 'hs300'
    context.lookback = 20

def handle_data(context, data):
    # 每日交易逻辑
    pass
`)
const selectedTemplate = ref<number | null>(null)
const showOutput = ref(false)
const logs = ref<any[]>([])

const templates = ref([
  {
    id: 1,
    name: '双均线策略',
    description: '基于短期和长期均线的交叉信号'
  },
  {
    id: 2,
    name: '多因子选股',
    description: '基于多个因子的综合选股策略'
  },
  {
    id: 3,
    name: '动量策略',
    description: '基于价格动量的趋势跟踪策略'
  },
  {
    id: 4,
    name: '均值回归',
    description: '基于价格均值回归的策略'
  }
])

const selectTemplate = (template: any) => {
  selectedTemplate.value = template.id
  strategyName.value = template.name
  ElMessage.info(`已选择模板：${template.name}`)
}

const saveStrategy = () => {
  if (!strategyName.value) {
    ElMessage.warning('请输入策略名称')
    return
  }
  ElMessage.success('策略保存成功')
}

const runStrategy = () => {
  showOutput.value = true
  logs.value = []
  addLog('info', '策略开始运行...')
  
  setTimeout(() => addLog('info', '加载市场数据...'), 500)
  setTimeout(() => addLog('info', '计算信号...'), 1000)
  setTimeout(() => addLog('info', '生成交易指令...'), 1500)
  setTimeout(() => addLog('success', '策略运行完成！'), 2000)
}

const addLog = (type: string, message: string) => {
  logs.value.push({
    time: new Date().toLocaleTimeString(),
    type,
    message
  })
}

const clearOutput = () => {
  logs.value = []
}
</script>

<style scoped>
.strategy-editor-container {
  padding: 20px;
}

.editor-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.editor-content {
  padding: 10px 0;
}

.template-list {
  max-height: 600px;
  overflow-y: auto;
}

.template-item {
  padding: 12px;
  border-bottom: 1px solid #EBEEF5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.template-item:hover {
  background-color: #F5F7FA;
}

.template-item.active {
  background-color: #ECF5FF;
  border-left: 3px solid #165DFF;
}

.template-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
}

.code-editor {
  min-height: 500px;
}

.code-textarea {
  width: 100%;
  min-height: 500px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  padding: 15px;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  resize: vertical;
}

.code-textarea:focus {
  outline: none;
  border-color: #165DFF;
}

.output-content {
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.log-item {
  padding: 8px 0;
  border-bottom: 1px solid #EBEEF5;
}

.log-time {
  color: #909399;
  margin-right: 10px;
}

.log-message {
  color: #303133;
}

@media (max-width: 768px) {
  .strategy-editor-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>

<template>
  <div class="risk-control-container">
    <el-card class="overview-card">
      <template #header>
        <span>风险控制概览</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="risk-item">
            <div class="risk-label">账户总权益</div>
            <div class="risk-value">¥{{ totalEquity.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="risk-item">
            <div class="risk-label">已用保证金</div>
            <div class="risk-value">¥{{ usedMargin.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="risk-item">
            <div class="risk-label">可用资金</div>
            <div class="risk-value">¥{{ availableFunds.toLocaleString() }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="risk-item">
            <div class="risk-label">保证金使用率</div>
            <div class="risk-value" :class="getRiskClass(marginUsage)">
              {{ marginUsage.toFixed(1) }}%
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="risk-indicators-card">
          <template #header>
            <span>风险指标</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="最大回撤">
              <span class="value-loss">-12.5%</span>
            </el-descriptions-item>
            <el-descriptions-item label="VaR (95%)">
              <span>¥-85,000</span>
            </el-descriptions-item>
            <el-descriptions-item label="VaR (99%)">
              <span>¥-125,000</span>
            </el-descriptions-item>
            <el-descriptions-item label="波动率 (年化)">
              <span>18.3%</span>
            </el-descriptions-item>
            <el-descriptions-item label="Beta系数">
              <span>0.85</span>
            </el-descriptions-item>
            <el-descriptions-item label="夏普比率">
              <span class="value-profit">1.42</span>
            </el-descriptions-item>
            <el-descriptions-item label="最大单笔亏损">
              <span class="value-loss">-¥35,000</span>
            </el-descriptions-item>
            <el-descriptions-item label="连续亏损天数">
              <span>3</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="settings-card">
          <template #header>
            <span>风控设置</span>
          </template>
          <el-form :model="riskSettings" label-width="150px">
            <el-form-item label="最大仓位比例(%)">
              <el-slider v-model="riskSettings.maxPositionPercent" :min="0" :max="100" show-input />
            </el-form-item>
            <el-form-item label="单笔最大亏损(%)">
              <el-slider v-model="riskSettings.maxSingleLossPercent" :min="0" :max="20" show-input />
            </el-form-item>
            <el-form-item label="每日最大亏损(%)">
              <el-slider v-model="riskSettings.maxDailyLossPercent" :min="0" :max="10" show-input />
            </el-form-item>
            <el-form-item label="最大回撤阈值(%)">
              <el-slider v-model="riskSettings.maxDrawdownThreshold" :min="0" :max="50" show-input />
            </el-form-item>
            <el-form-item label="保证金预警线(%)">
              <el-slider v-model="riskSettings.marginWarningLine" :min="0" :max="100" show-input />
            </el-form-item>
            <el-form-item label="强平线(%)">
              <el-slider v-model="riskSettings.forceCloseLine" :min="0" :max="100" show-input />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveSettings">保存设置</el-button>
              <el-button @click="handleResetSettings">重置默认</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="alerts-card" style="margin-top: 20px;">
      <template #header>
        <span>风险预警记录</span>
      </template>
      <el-table :data="alertList" stripe style="width: 100%">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getAlertType(row.level)">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="150" />
        <el-table-column prop="message" label="预警信息" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '处理中' ? 'warning' : 'success'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleAlertDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

interface Alert {
  time: string
  level: string
  type: string
  message: string
  status: string
}

const totalEquity = ref(1250000)
const usedMargin = ref(450000)
const availableFunds = ref(800000)
const marginUsage = ref(36.0)

const riskSettings = ref({
  maxPositionPercent: 80,
  maxSingleLossPercent: 5,
  maxDailyLossPercent: 3,
  maxDrawdownThreshold: 20,
  marginWarningLine: 70,
  forceCloseLine: 90
})

const alertList: Alert[] = [
  { time: '2024-04-15 14:32:15', level: '警告', type: '保证金', message: '保证金使用率已达65%，请注意风险', status: '已处理' },
  { time: '2024-04-15 10:15:30', level: '提示', type: '仓位', message: 'AU.SHF持仓已接近上限', status: '已处理' },
  { time: '2024-04-14 15:45:22', level: '警告', type: '亏损', message: '今日亏损已达2.5%', status: '处理中' },
  { time: '2024-04-14 09:20:10', level: '提示', type: '回撤', message: '最大回撤已达10%', status: '已处理' },
  { time: '2024-04-13 16:10:05', level: '严重', type: '强平预警', message: '保证金使用率接近预警线', status: '已处理' }
]

const getRiskClass = (value: number) => {
  if (value < 50) return 'value-normal'
  if (value < 70) return 'value-warning'
  return 'value-danger'
}

const getAlertType = (level: string) => {
  const typeMap: Record<string, any> = {
    '提示': 'info',
    '警告': 'warning',
    '严重': 'danger'
  }
  return typeMap[level] || 'info'
}

const handleSaveSettings = () => {
  ElMessage.success('风控设置已保存')
}

const handleResetSettings = () => {
  riskSettings.value = {
    maxPositionPercent: 80,
    maxSingleLossPercent: 5,
    maxDailyLossPercent: 3,
    maxDrawdownThreshold: 20,
    marginWarningLine: 70,
    forceCloseLine: 90
  }
  ElMessage.info('已重置为默认设置')
}

const handleAlertDetail = (row: Alert) => {
  ElMessage.info(`查看预警详情: ${row.message}`)
}
</script>

<style scoped>
.risk-control-container {
  padding: 20px;
}

.overview-card,
.risk-indicators-card,
.settings-card,
.alerts-card {
  margin-bottom: 20px;
}

.risk-item {
  text-align: center;
  padding: 10px;
}

.risk-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.risk-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.value-normal {
  color: #67C23A;
}

.value-warning {
  color: #E6A23C;
}

.value-danger {
  color: #F56C6C;
}

.value-profit {
  color: #67C23A;
}

.value-loss {
  color: #F56C6C;
}

@media (max-width: 768px) {
  .risk-control-container {
    padding: 10px;
  }
}
</style>

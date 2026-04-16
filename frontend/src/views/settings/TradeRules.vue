<template>
  <div class="trade-rules-container">
    <el-card class="rules-card">
      <template #header>
        <div class="card-header">
          <span>交易规则设置</span>
          <el-button type="primary" @click="handleSave">
            <el-icon><Document /></el-icon>
            保存设置
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="手续费设置" name="commission">
          <el-form :model="commissionForm" label-width="180px">
            <el-divider content-position="left">期货手续费</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="开仓手续费率(%)">
                  <el-input-number v-model="commissionForm.openCommission" :min="0" :max="10" :step="0.001" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="平仓手续费率(%)">
                  <el-input-number v-model="commissionForm.closeCommission" :min="0" :max="10" :step="0.001" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="平今仓手续费率(%)">
                  <el-input-number v-model="commissionForm.closeTodayCommission" :min="0" :max="10" :step="0.001" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最低手续费(元)">
                  <el-input-number v-model="commissionForm.minCommission" :min="0" :step="0.01" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-divider content-position="left">品种特定手续费</el-divider>
            <el-button type="primary" size="small" @click="handleAddCommissionRule" style="margin-bottom: 20px;">
              <el-icon><Plus /></el-icon>
              添加品种规则
            </el-button>
            <el-table :data="commissionRules" border style="width: 100%;">
              <el-table-column prop="symbol" label="合约代码" width="150">
                <template #default="{ row }">
                  <el-select v-model="row.symbol" placeholder="选择合约">
                    <el-option label="AU.SHF" value="AU.SHF" />
                    <el-option label="AG.SHF" value="AG.SHF" />
                    <el-option label="CU.SHF" value="CU.SHF" />
                    <el-option label="RU.SHF" value="RU.SHF" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="openRate" label="开仓费率(%)" width="150">
                <template #default="{ row }">
                  <el-input-number v-model="row.openRate" :min="0" :step="0.001" style="width: 100%;" />
                </template>
              </el-table-column>
              <el-table-column prop="closeRate" label="平仓费率(%)" width="150">
                <template #default="{ row }">
                  <el-input-number v-model="row.closeRate" :min="0" :step="0.001" style="width: 100%;" />
                </template>
              </el-table-column>
              <el-table-column prop="closeTodayRate" label="平今费率(%)" width="150">
                <template #default="{ row }">
                  <el-input-number v-model="row.closeTodayRate" :min="0" :step="0.001" style="width: 100%;" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button type="danger" size="small" @click="handleDeleteCommissionRule(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="滑点设置" name="slippage">
          <el-form :model="slippageForm" label-width="180px">
            <el-divider content-position="left">全局滑点</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="滑点类型">
                  <el-radio-group v-model="slippageForm.type">
                    <el-radio label="fixed">固定值</el-radio>
                    <el-radio label="percentage">百分比</el-radio>
                    <el-radio label="ticks">跳数</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="滑点值">
                  <el-input-number v-model="slippageForm.value" :min="0" :step="0.01" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-divider content-position="left">品种特定滑点</el-divider>
            <el-button type="primary" size="small" @click="handleAddSlippageRule" style="margin-bottom: 20px;">
              <el-icon><Plus /></el-icon>
              添加品种规则
            </el-button>
            <el-table :data="slippageRules" border style="width: 100%;">
              <el-table-column prop="symbol" label="合约代码" width="150">
                <template #default="{ row }">
                  <el-select v-model="row.symbol" placeholder="选择合约">
                    <el-option label="AU.SHF" value="AU.SHF" />
                    <el-option label="AG.SHF" value="AG.SHF" />
                    <el-option label="CU.SHF" value="CU.SHF" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="滑点类型" width="120">
                <template #default="{ row }">
                  <el-select v-model="row.type" placeholder="选择类型">
                    <el-option label="固定值" value="fixed" />
                    <el-option label="百分比" value="percentage" />
                    <el-option label="跳数" value="ticks" />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column prop="value" label="滑点值" width="150">
                <template #default="{ row }">
                  <el-input-number v-model="row.value" :min="0" :step="0.01" style="width: 100%;" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button type="danger" size="small" @click="handleDeleteSlippageRule(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="交易限制" name="limits">
          <el-form :model="limitsForm" label-width="200px">
            <el-divider content-position="left">仓位限制</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="单品种最大持仓(手)">
                  <el-input-number v-model="limitsForm.maxPositionPerSymbol" :min="1" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="单品种最大仓位(%)">
                  <el-input-number v-model="limitsForm.maxPositionPercentPerSymbol" :min="1" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="总持仓品种数上限">
                  <el-input-number v-model="limitsForm.maxTotalSymbols" :min="1" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="总仓位上限(%)">
                  <el-input-number v-model="limitsForm.maxTotalPositionPercent" :min="1" :max="100" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">交易频率限制</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="每日最大交易次数">
                  <el-input-number v-model="limitsForm.maxDailyTrades" :min="1" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最小交易间隔(秒)">
                  <el-input-number v-model="limitsForm.minTradeInterval" :min="1" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">止损止盈</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="默认止损比例(%)">
                  <el-input-number v-model="limitsForm.defaultStopLossPercent" :min="0" :max="50" :step="0.1" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="默认止盈比例(%)">
                  <el-input-number v-model="limitsForm.defaultTakeProfitPercent" :min="0" :max="100" :step="0.1" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="交易时间" name="tradingHours">
          <el-form :model="tradingHoursForm" label-width="200px">
            <el-divider content-position="left">主要交易时段</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="上午开盘时间">
                  <el-time-picker v-model="tradingHoursForm.morningOpen" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="上午收盘时间">
                  <el-time-picker v-model="tradingHoursForm.morningClose" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="下午开盘时间">
                  <el-time-picker v-model="tradingHoursForm.afternoonOpen" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="下午收盘时间">
                  <el-time-picker v-model="tradingHoursForm.afternoonClose" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="夜盘开盘时间">
                  <el-time-picker v-model="tradingHoursForm.nightOpen" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="夜盘收盘时间">
                  <el-time-picker v-model="tradingHoursForm.nightClose" placeholder="选择时间" format="HH:mm" value-format="HH:mm" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">交易规则</el-divider>
            <el-form-item label="非交易时段下单">
              <el-radio-group v-model="tradingHoursForm.allowOutOfHoursOrder">
                <el-radio :label="true">允许</el-radio>
                <el-radio :label="false">禁止</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="集合竞价时段下单">
              <el-radio-group v-model="tradingHoursForm.allowAuctionOrder">
                <el-radio :label="true">允许</el-radio>
                <el-radio :label="false">禁止</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Document, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('commission')

const commissionForm = ref({
  openCommission: 0.03,
  closeCommission: 0.03,
  closeTodayCommission: 0.06,
  minCommission: 5
})

const slippageForm = ref({
  type: 'fixed',
  value: 0.2
})

const limitsForm = ref({
  maxPositionPerSymbol: 100,
  maxPositionPercentPerSymbol: 30,
  maxTotalSymbols: 10,
  maxTotalPositionPercent: 80,
  maxDailyTrades: 50,
  minTradeInterval: 5,
  defaultStopLossPercent: 5,
  defaultTakeProfitPercent: 10
})

const tradingHoursForm = ref({
  morningOpen: '09:00',
  morningClose: '11:30',
  afternoonOpen: '13:30',
  afternoonClose: '15:00',
  nightOpen: '21:00',
  nightClose: '02:30',
  allowOutOfHoursOrder: false,
  allowAuctionOrder: true
})

const commissionRules = ref([
  { symbol: 'AU.SHF', openRate: 0.02, closeRate: 0.02, closeTodayRate: 0.04 },
  { symbol: 'AG.SHF', openRate: 0.03, closeRate: 0.03, closeTodayRate: 0.06 }
])

const slippageRules = ref([
  { symbol: 'AU.SHF', type: 'fixed', value: 0.1 },
  { symbol: 'AG.SHF', type: 'ticks', value: 1 }
])

const handleSave = () => {
  ElMessage.success('交易规则设置已保存')
}

const handleAddCommissionRule = () => {
  commissionRules.value.push({ symbol: '', openRate: 0, closeRate: 0, closeTodayRate: 0 })
}

const handleDeleteCommissionRule = (index: number) => {
  commissionRules.value.splice(index, 1)
}

const handleAddSlippageRule = () => {
  slippageRules.value.push({ symbol: '', type: 'fixed', value: 0 })
}

const handleDeleteSlippageRule = (index: number) => {
  slippageRules.value.splice(index, 1)
}
</script>

<style scoped>
.trade-rules-container {
  padding: 20px;
}

.rules-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .trade-rules-container {
    padding: 10px;
  }
}
</style>

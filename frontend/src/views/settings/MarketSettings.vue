<template>
  <div class="market-settings-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>行情设置</span>
          <el-button type="primary" @click="saveSettings">
            <el-icon><Document /></el-icon>
            保存设置
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基础设置" name="basic">
          <el-form :model="basicForm" label-width="180px">
            <el-form-item label="行情刷新频率">
              <el-select v-model="basicForm.refreshRate" style="width: 200px;">
                <el-option label="实时" value="realtime" />
                <el-option label="1秒" value="1s" />
                <el-option label="3秒" value="3s" />
                <el-option label="5秒" value="5s" />
                <el-option label="10秒" value="10s" />
                <el-option label="30秒" value="30s" />
                <el-option label="1分钟" value="1m" />
              </el-select>
            </el-form-item>
            <el-form-item label="K线周期默认">
              <el-select v-model="basicForm.defaultKline" style="width: 200px;">
                <el-option label="1分钟" value="1min" />
                <el-option label="5分钟" value="5min" />
                <el-option label="15分钟" value="15min" />
                <el-option label="30分钟" value="30min" />
                <el-option label="1小时" value="1hour" />
                <el-option label="1日线" value="1day" />
                <el-option label="1周线" value="1week" />
              </el-select>
            </el-form-item>
            <el-form-item label="数据保留天数">
              <el-input-number v-model="basicForm.dataRetentionDays" :min="7" :max="365" style="width: 200px;" />
            </el-form-item>
            <el-form-item label="自动刷新行情">
              <el-switch v-model="basicForm.autoRefresh" />
            </el-form-item>
            <el-form-item label="显示涨跌停价格">
              <el-switch v-model="basicForm.showLimitPrice" />
            </el-form-item>
            <el-form-item label="显示买卖盘口">
              <el-switch v-model="basicForm.showOrderBook" />
            </el-form-item>
            <el-form-item label="盘口档位">
              <el-radio-group v-model="basicForm.orderBookDepth">
                <el-radio-button :value="5">5档</el-radio-button>
                <el-radio-button :value="10">10档</el-radio-button>
                <el-radio-button :value="20">20档</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="预警设置" name="alert">
          <el-form :model="alertForm" label-width="180px">
            <el-divider content-position="left">价格预警</el-divider>
            <el-form-item label="启用价格预警">
              <el-switch v-model="alertForm.priceAlertEnabled" />
            </el-form-item>
            <el-form-item label="预警声音">
              <el-switch v-model="alertForm.alertSound" />
            </el-form-item>
            <el-form-item label="弹窗通知">
              <el-switch v-model="alertForm.alertPopup" />
            </el-form-item>
            
            <el-divider content-position="left">涨跌幅预警</el-divider>
            <el-form-item label="涨跌幅预警阈值%">
              <el-input-number v-model="alertForm.changeThreshold" :min="1" :max="20" :step="0.5" style="width: 200px;" />
            </el-form-item>
            <el-form-item label="启用涨跌幅预警">
              <el-switch v-model="alertForm.changeAlertEnabled" />
            </el-form-item>

            <el-divider content-position="left">波动率预警</el-divider>
            <el-form-item label="波动率预警阈值%">
              <el-input-number v-model="alertForm.volatilityThreshold" :min="1" :max="50" :step="1" style="width: 200px;" />
            </el-form-item>
            <el-form-item label="启用波动率预警">
              <el-switch v-model="alertForm.volatilityAlertEnabled" />
            </el-form-item>
          </el-form>

          <el-card class="alert-list-card" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>自定义预警列表</span>
                <el-button type="primary" size="small" @click="showAddAlertDialog">
                  <el-icon><Plus /></el-icon>
                  添加预警
                </el-button>
              </div>
            </template>
            <el-table :data="customAlerts" stripe style="width: 100%;">
              <el-table-column prop="symbol" label="标的代码" width="120" />
              <el-table-column prop="name" label="标的名称" width="150" />
              <el-table-column prop="alertType" label="预警类型" width="120">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.alertType === 'price' ? '价格' : row.alertType === 'change' ? '涨跌幅' : '波动率' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="condition" label="条件" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.condition === 'above' ? '高于' : '低于' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="threshold" label="阈值" width="120">
                <template #default="{ row }">
                  {{ row.alertType === 'price' ? '¥' : '' }}{{ row.threshold }}{{ row.alertType !== 'price' ? '%' : '' }}
                </template>
              </el-table-column>
              <el-table-column prop="enabled" label="状态" width="80">
                <template #default="{ row }">
                  <el-switch v-model="row.enabled" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" size="small" link @click="editAlert(row)">编辑</el-button>
                  <el-button type="danger" size="small" link @click="deleteAlert(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="自选股设置" name="watchlist">
          <el-form :model="watchlistForm" label-width="180px">
            <el-form-item label="自选股分组">
              <el-select v-model="watchlistForm.selectedGroup" style="width: 200px;">
                <el-option label="默认分组" value="default" />
                <el-option label="科技股" value="tech" />
                <el-option label="消费股" value="consumer" />
                <el-option label="金融股" value="finance" />
              </el-select>
              <el-button type="primary" size="small" style="margin-left: 10px;" @click="showAddGroupDialog">
                <el-icon><Plus /></el-icon>
                新建分组
              </el-button>
            </el-form-item>
            <el-form-item label="添加标的">
              <el-input v-model="watchlistForm.newSymbol" placeholder="请输入标的代码" style="width: 200px;" />
              <el-button type="primary" size="small" style="margin-left: 10px;" @click="addSymbol">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </el-form-item>
          </el-form>

          <el-card class="watchlist-card" style="margin-top: 20px;">
            <template #header>
              <div class="card-header">
                <span>自选股列表</span>
                <el-button type="primary" size="small" @click="importWatchlist">
                  <el-icon><Upload /></el-icon>
                  导入
                </el-button>
                <el-button type="success" size="small" @click="exportWatchlist">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
            </template>
            <el-table :data="watchlistSymbols" stripe style="width: 100%;" row-key="symbol">
              <el-table-column type="index" width="60" />
              <el-table-column prop="symbol" label="代码" width="100" />
              <el-table-column prop="name" label="名称" width="150" />
              <el-table-column prop="price" label="最新价" width="120">
                <template #default="{ row }">
                  <span :style="{ color: row.change >= 0 ? '#67C23A' : '#F56C6C' }">
                    ¥{{ row.price.toFixed(2) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="change" label="涨跌幅" width="120">
                <template #default="{ row }">
                  <span :style="{ color: row.change >= 0 ? '#67C23A' : '#F56C6C' }">
                    {{ row.change >= 0 ? '+' : '' }}{{ row.change.toFixed(2) }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="volume" label="成交量" width="150">
                <template #default="{ row }">
                  {{ (row.volume / 10000).toFixed(2) }}万
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button type="danger" size="small" link @click="removeSymbol(row)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog
      v-model="addAlertDialogVisible"
      title="添加预警"
      width="500px"
    >
      <el-form :model="alertFormData" label-width="100px">
        <el-form-item label="标的代码">
          <el-input v-model="alertFormData.symbol" placeholder="请输入标的代码" />
        </el-form-item>
        <el-form-item label="预警类型">
          <el-select v-model="alertFormData.alertType" style="width: 100%;">
            <el-option label="价格预警" value="price" />
            <el-option label="涨跌幅预警" value="change" />
            <el-option label="波动率预警" value="volatility" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件">
          <el-select v-model="alertFormData.condition" style="width: 100%;">
            <el-option label="高于" value="above" />
            <el-option label="低于" value="below" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值">
          <el-input-number v-model="alertFormData.threshold" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addAlertDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAlert">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Document, Plus, Upload, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')
const addAlertDialogVisible = ref(false)

const basicForm = reactive({
  refreshRate: '5s',
  defaultKline: '1day',
  dataRetentionDays: 90,
  autoRefresh: true,
  showLimitPrice: true,
  showOrderBook: true,
  orderBookDepth: 10
})

const alertForm = reactive({
  priceAlertEnabled: true,
  alertSound: true,
  alertPopup: true,
  changeThreshold: 5,
  changeAlertEnabled: true,
  volatilityThreshold: 10,
  volatilityAlertEnabled: false
})

const watchlistForm = reactive({
  selectedGroup: 'default',
  newSymbol: ''
})

const alertFormData = reactive({
  symbol: '',
  alertType: 'price',
  condition: 'above',
  threshold: 0
})

const customAlerts = ref([
  { symbol: '600519', name: '贵州茅台', alertType: 'price', condition: 'above', threshold: 2000, enabled: true },
  { symbol: '000001', name: '平安银行', alertType: 'change', condition: 'above', threshold: 5, enabled: true },
  { symbol: '601318', name: '中国平安', alertType: 'price', condition: 'below', threshold: 40, enabled: false }
])

const watchlistSymbols = ref([
  { symbol: '600519', name: '贵州茅台', price: 1850.50, change: 2.35, volume: 125600 },
  { symbol: '000001', name: '平安银行', price: 11.75, change: -0.85, volume: 5268000 },
  { symbol: '601318', name: '中国平安', price: 45.50, change: 1.25, volume: 2568900 },
  { symbol: '000858', name: '五粮液', price: 162.50, change: 3.45, volume: 896500 },
  { symbol: '600036', name: '招商银行', price: 34.80, change: -0.45, volume: 3568700 }
])

const saveSettings = () => {
  ElMessage.success('设置保存成功')
}

const showAddAlertDialog = () => {
  Object.assign(alertFormData, {
    symbol: '',
    alertType: 'price',
    condition: 'above',
    threshold: 0
  })
  addAlertDialogVisible.value = true
}

const saveAlert = () => {
  customAlerts.value.push({
    ...alertFormData,
    name: alertFormData.symbol,
    enabled: true
  })
  addAlertDialogVisible.value = false
  ElMessage.success('预警添加成功')
}

const editAlert = (row: any) => {
  Object.assign(alertFormData, row)
  addAlertDialogVisible.value = true
}

const deleteAlert = (row: any) => {
  const index = customAlerts.value.findIndex(item => item.symbol === row.symbol && item.alertType === row.alertType)
  if (index > -1) {
    customAlerts.value.splice(index, 1)
    ElMessage.success('删除成功')
  }
}

const showAddGroupDialog = () => {
  ElMessage.info('新建分组功能')
}

const addSymbol = () => {
  if (watchlistForm.newSymbol) {
    watchlistSymbols.value.push({
      symbol: watchlistForm.newSymbol,
      name: watchlistForm.newSymbol,
      price: 10.00,
      change: 0,
      volume: 0
    })
    watchlistForm.newSymbol = ''
    ElMessage.success('添加成功')
  }
}

const removeSymbol = (row: any) => {
  const index = watchlistSymbols.value.findIndex(item => item.symbol === row.symbol)
  if (index > -1) {
    watchlistSymbols.value.splice(index, 1)
    ElMessage.success('删除成功')
  }
}

const importWatchlist = () => {
  ElMessage.info('导入自选股功能')
}

const exportWatchlist = () => {
  ElMessage.success('导出成功')
}

onMounted(() => {
})
</script>

<style scoped>
.market-settings-container {
  padding: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-list-card,
.watchlist-card {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .market-settings-container {
    padding: 10px;
  }
}
</style>

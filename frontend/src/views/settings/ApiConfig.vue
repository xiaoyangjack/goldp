<template>
  <div class="api-config-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>API配置</span>
          <el-button type="primary" @click="saveConfig">
            <el-icon><Document /></el-icon>
            保存配置
          </el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="数据源API" name="datasource">
          <el-form :model="dataSourceForm" label-width="150px">
            <el-form-item label="API基础地址">
              <el-input v-model="dataSourceForm.baseUrl" placeholder="请输入API基础地址" />
            </el-form-item>
            <el-form-item label="API密钥">
              <el-input v-model="dataSourceForm.apiKey" type="password" placeholder="请输入API密钥" show-password />
            </el-form-item>
            <el-form-item label="API密钥密钥">
              <el-input v-model="dataSourceForm.apiSecret" type="password" placeholder="请输入API密钥密钥" show-password />
            </el-form-item>
            <el-form-item label="请求超时(ms)">
              <el-input-number v-model="dataSourceForm.timeout" :min="1000" :max="60000" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="启用状态">
              <el-switch v-model="dataSourceForm.enabled" />
            </el-form-item>
            <el-divider />
            <el-form-item>
              <el-button type="primary" @click="testConnection">
                <el-icon><Connection /></el-icon>
                测试连接
              </el-button>
              <el-button @click="resetDataSource">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="交易API" name="trading">
          <el-form :model="tradingForm" label-width="150px">
            <el-form-item label="交易API地址">
              <el-input v-model="tradingForm.baseUrl" placeholder="请输入交易API地址" />
            </el-form-item>
            <el-form-item label="账户ID">
              <el-input v-model="tradingForm.accountId" placeholder="请输入账户ID" />
            </el-form-item>
            <el-form-item label="API密钥">
              <el-input v-model="tradingForm.apiKey" type="password" placeholder="请输入API密钥" show-password />
            </el-form-item>
            <el-form-item label="API密钥">
              <el-input v-model="tradingForm.apiSecret" type="password" placeholder="请输入API密钥密钥" show-password />
            </el-form-item>
            <el-form-item label="实盘/模拟">
              <el-radio-group v-model="tradingForm.env">
                <el-radio-button value="paper">模拟交易</el-radio-button>
                <el-radio-button value="live">实盘交易</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-divider />
            <el-form-item>
              <el-button type="primary" @click="testTradingConnection">测试连接</el-button>
              <el-button @click="resetTrading">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="通知API" name="notification">
          <el-form :model="notificationForm" label-width="150px">
            <el-form-item label="启用通知">
              <el-switch v-model="notificationForm.enabled" />
            </el-form-item>
            <el-divider content-position="left">邮件通知</el-divider>
            <el-form-item label="SMTP服务器">
              <el-input v-model="notificationForm.smtpHost" placeholder="smtp.example.com" />
            </el-form-item>
            <el-form-item label="SMTP端口">
              <el-input-number v-model="notificationForm.smtpPort" :min="1" :max="65535" style="width: 100%;" />
            </el-form-item>
            <el-form-item label="发件人">
              <el-input v-model="notificationForm.fromEmail" placeholder="sender@example.com" />
            </el-form-item>
            <el-form-item label="收件人">
              <el-input v-model="notificationForm.toEmail" placeholder="receiver@example.com" />
            </el-form-item>
            <el-divider content-position="left">Webhook</el-divider>
            <el-form-item label="Webhook URL">
              <el-input v-model="notificationForm.webhookUrl" placeholder="https://example.com/webhook" />
            </el-form-item>
            <el-form-item label="Webhook密钥">
              <el-input v-model="notificationForm.webhookSecret" type="password" placeholder="可选" show-password />
            </el-form-item>
            <el-divider />
            <el-form-item>
              <el-button type="primary" @click="sendTestNotification">发送测试通知</el-button>
              <el-button @click="resetNotification">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-card class="status-card" style="margin-top: 20px;">
      <template #header>
        <span>API状态</span>
      </template>
      <el-table :data="apiStatusList" style="width: 100%">
        <el-table-column prop="name" label="API名称" width="200" />
        <el-table-column prop="type" label="类型" width="150" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === '正常' ? 'success' : row.status === '异常' ? 'danger' : 'warning'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastCheck" label="最后检查" width="180" />
        <el-table-column prop="latency" label="延迟" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="primary" size="small" link @click="checkApiStatus(scope.row)">检查</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="history-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>API调用日志</span>
          <el-button type="danger" size="small" @click="clearLogs">清空日志</el-button>
        </div>
      </template>
      <el-table :data="apiLogs" style="width: 100%">
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="api" label="API" width="150" />
        <el-table-column prop="endpoint" label="接口" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="row.method === 'GET' ? 'info' : row.method === 'POST' ? 'primary' : 'warning'" size="small">
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status >= 200 && row.status < 300 ? 'success' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Document, Connection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('datasource')

const dataSourceForm = ref({
  baseUrl: 'https://api.example.com',
  apiKey: '',
  apiSecret: '',
  timeout: 10000,
  enabled: true
})

const tradingForm = ref({
  baseUrl: 'https://trading.example.com',
  accountId: '',
  apiKey: '',
  apiSecret: '',
  env: 'paper'
})

const notificationForm = ref({
  enabled: true,
  smtpHost: 'smtp.example.com',
  smtpPort: 587,
  fromEmail: 'noreply@goldquant.com',
  toEmail: '',
  webhookUrl: '',
  webhookSecret: ''
})

const apiStatusList = ref([
  { name: '市场数据API', type: '数据源', status: '正常', lastCheck: '2024-04-16 10:30:00', latency: '45ms' },
  { name: '基本面数据API', type: '数据源', status: '正常', lastCheck: '2024-04-16 10:30:05', latency: '52ms' },
  { name: '交易API', type: '交易', status: '正常', lastCheck: '2024-04-16 10:29:55', latency: '38ms' },
  { name: '通知服务', type: '通知', status: '未配置', lastCheck: '-', latency: '-' }
])

const apiLogs = ref([
  { timestamp: '2024-04-16 10:35:20', api: '市场数据', endpoint: '/api/market/quote', method: 'GET', status: 200, duration: '45ms' },
  { timestamp: '2024-04-16 10:35:15', api: '市场数据', endpoint: '/api/market/kline', method: 'GET', status: 200, duration: '62ms' },
  { timestamp: '2024-04-16 10:35:10', api: '交易', endpoint: '/api/account/info', method: 'GET', status: 200, duration: '38ms' },
  { timestamp: '2024-04-16 10:35:05', api: '基本面', endpoint: '/api/fundamental/financial', method: 'GET', status: 200, duration: '125ms' }
])

const cardHeader = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
}

const saveConfig = () => {
  ElMessage.success('配置保存成功')
}

const testConnection = () => {
  ElMessage.info('正在测试连接...')
  setTimeout(() => {
    ElMessage.success('连接测试成功')
    apiStatusList.value[0].status = '正常'
    apiStatusList.value[0].lastCheck = new Date().toLocaleString()
    apiStatusList.value[0].latency = `${Math.floor(Math.random() * 50 + 30)}ms`
  }, 1000)
}

const resetDataSource = () => {
  dataSourceForm.value = {
    baseUrl: 'https://api.example.com',
    apiKey: '',
    apiSecret: '',
    timeout: 10000,
    enabled: true
  }
  ElMessage.info('已重置数据源配置')
}

const testTradingConnection = () => {
  ElMessage.info('正在测试交易API连接...')
  setTimeout(() => {
    ElMessage.success('交易API连接测试成功')
    apiStatusList.value[2].status = '正常'
    apiStatusList.value[2].lastCheck = new Date().toLocaleString()
    apiStatusList.value[2].latency = `${Math.floor(Math.random() * 50 + 30)}ms`
  }, 1000)
}

const resetTrading = () => {
  tradingForm.value = {
    baseUrl: 'https://trading.example.com',
    accountId: '',
    apiKey: '',
    apiSecret: '',
    env: 'paper'
  }
  ElMessage.info('已重置交易配置')
}

const sendTestNotification = () => {
  ElMessage.success('测试通知已发送')
}

const resetNotification = () => {
  notificationForm.value = {
    enabled: true,
    smtpHost: 'smtp.example.com',
    smtpPort: 587,
    fromEmail: 'noreply@goldquant.com',
    toEmail: '',
    webhookUrl: '',
    webhookSecret: ''
  }
  ElMessage.info('已重置通知配置')
}

const checkApiStatus = (api: any) => {
  ElMessage.info(`正在检查 ${api.name}...`)
  setTimeout(() => {
    api.status = '正常'
    api.lastCheck = new Date().toLocaleString()
    api.latency = `${Math.floor(Math.random() * 50 + 30)}ms`
    ElMessage.success(`${api.name} 检查完成`)
  }, 800)
}

const clearLogs = () => {
  apiLogs.value = []
  ElMessage.success('日志已清空')
}
</script>

<style scoped>
.api-config-container {
  padding: 20px;
}

.config-card,
.status-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .api-config-container {
    padding: 10px;
  }
}
</style>

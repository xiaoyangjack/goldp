<template>
  <div class="api-access-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>API接入</span>
        </div>
      </template>
      <div class="data-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="API文档" name="docs">
            <div class="docs-content">
              <el-collapse v-model="activeDocs">
                <el-collapse-item title="行情数据API" name="market">
                  <div class="api-item">
                    <h4>获取股票行情</h4>
                    <el-card class="code-card">
                      <pre><code>GET /api/market/quote
参数:
  symbol: 股票代码
  startDate: 开始日期
  endDate: 结束日期</code></pre>
                    </el-card>
                  </div>
                </el-collapse-item>
                <el-collapse-item title="财务数据API" name="finance">
                  <div class="api-item">
                    <h4>获取财务报表</h4>
                    <el-card class="code-card">
                      <pre><code>GET /api/finance/report
参数:
  symbol: 股票代码
  period: 报告期</code></pre>
                    </el-card>
                  </div>
                </el-collapse-item>
                <el-collapse-item title="因子数据API" name="factor">
                  <div class="api-item">
                    <h4>获取因子数据</h4>
                    <el-card class="code-card">
                      <pre><code>GET /api/factor/data
参数:
  factor: 因子名称
  date: 日期</code></pre>
                    </el-card>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="API密钥管理" name="keys">
            <div class="keys-content">
              <el-button type="primary" @click="showCreateDialog">
                <el-icon><Plus /></el-icon>
                生成新密钥
              </el-button>
              <el-table :data="apiKeys" style="width: 100%; margin-top: 20px;">
                <el-table-column prop="name" label="密钥名称" />
                <el-table-column prop="key" label="API Key">
                  <template #default="scope">
                    <span>{{ maskKey(scope.row.key) }}</span>
                    <el-button type="primary" size="small" link @click="copyKey(scope.row.key)">
                      复制
                    </el-button>
                  </template>
                </el-table-column>
                <el-table-column prop="createdAt" label="创建时间" />
                <el-table-column prop="status" label="状态">
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
                      {{ scope.row.status === 'active' ? '启用' : '禁用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="200">
                  <template #default="scope">
                    <el-button size="small" link @click="toggleStatus(scope.row)">
                      {{ scope.row.status === 'active' ? '禁用' : '启用' }}
                    </el-button>
                    <el-button type="danger" size="small" link @click="deleteKey(scope.row)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="使用统计" name="stats">
            <div class="stats-content">
              <el-row :gutter="20">
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-title">今日调用次数</div>
                    <div class="stat-value">1,234</div>
                  </el-card>
                </el-col>
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-title">本月调用次数</div>
                    <div class="stat-value">45,678</div>
                  </el-card>
                </el-col>
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-title">剩余配额</div>
                    <div class="stat-value">54,322</div>
                  </el-card>
                </el-col>
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-title">成功率</div>
                    <div class="stat-value">99.5%</div>
                  </el-card>
                </el-col>
              </el-row>
              <el-card style="margin-top: 20px;">
                <template #header>调用趋势</template>
                <div ref="chartRef" class="chart" style="height: 350px;"></div>
              </el-card>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
    
    <el-dialog v-model="createDialogVisible" title="生成新API密钥" width="500px">
      <el-form :model="keyForm" label-width="100px">
        <el-form-item label="密钥名称">
          <el-input v-model="keyForm.name" placeholder="请输入密钥名称" />
        </el-form-item>
        <el-form-item label="权限范围">
          <el-checkbox-group v-model="keyForm.permissions">
            <el-checkbox label="read">读取权限</el-checkbox>
            <el-checkbox label="write">写入权限</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createKey">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('docs')
const activeDocs = ref(['market'])
const createDialogVisible = ref(false)
const chartRef = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()

const apiKeys = ref([
  { name: '生产环境', key: 'gk_abc123def456ghi789jkl', createdAt: '2024-01-01 10:00:00', status: 'active' },
  { name: '测试环境', key: 'gk_xyz987wvu654tsr321qpo', createdAt: '2024-01-05 14:30:00', status: 'active' }
])

const keyForm = reactive({
  name: '',
  permissions: ['read']
})

const maskKey = (key: string) => {
  return key.substring(0, 6) + '****' + key.substring(key.length - 4)
}

const copyKey = (key: string) => {
  navigator.clipboard.writeText(key)
  ElMessage.success('已复制到剪贴板')
}

const toggleStatus = (row: any) => {
  row.status = row.status === 'active' ? 'inactive' : 'active'
  ElMessage.success(row.status === 'active' ? '已启用' : '已禁用')
}

const deleteKey = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个API密钥吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    apiKeys.value = apiKeys.value.filter(item => item.key !== row.key)
    ElMessage.success('删除成功')
  } catch {
    ElMessage.info('已取消操作')
  }
}

const showCreateDialog = () => {
  keyForm.name = ''
  keyForm.permissions = ['read']
  createDialogVisible.value = true
}

const createKey = () => {
  if (!keyForm.name) {
    ElMessage.warning('请输入密钥名称')
    return
  }
  const newKey = 'gk_' + Math.random().toString(36).substring(2, 24)
  apiKeys.value.unshift({
    name: keyForm.name,
    key: newKey,
    createdAt: new Date().toLocaleString(),
    status: 'active'
  })
  createDialogVisible.value = false
  ElMessage.success('API密钥生成成功')
}

const initChart = () => {
  if (process.env.NODE_ENV !== 'test' && chartRef.value) {
    chart.value = echarts.init(chartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['调用次数', '成功次数']
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
        data: ['1日', '2日', '3日', '4日', '5日', '6日', '7日', '8日', '9日', '10日']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '调用次数',
          type: 'line',
          data: [1200, 1350, 1180, 1420, 1280, 1350, 1480, 1320, 1250, 1234],
          smooth: true,
          lineStyle: {
            color: '#165DFF'
          }
        },
        {
          name: '成功次数',
          type: 'line',
          data: [1190, 1340, 1170, 1410, 1270, 1340, 1470, 1310, 1240, 1228],
          smooth: true,
          lineStyle: {
            color: '#67C23A'
          }
        }
      ]
    }
    chart.value.setOption(option)
  }
}

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.api-access-container {
  padding: 20px;
}

.data-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-content {
  padding: 10px 0;
}

.docs-content {
  padding: 10px 0;
}

.code-card {
  margin-top: 10px;
  background-color: #f5f7fa;
}

.code-card pre {
  margin: 0;
  font-family: 'Courier New', monospace;
}

.stat-card {
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #165DFF;
}

.chart {
  width: 100%;
  height: 350px;
}

@media (max-width: 768px) {
  .api-access-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
}
</style>

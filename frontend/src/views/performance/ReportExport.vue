<template>
  <div class="report-export-container">
    <el-card class="config-card">
      <template #header>
        <span>报告配置</span>
      </template>
      <el-form :model="reportConfig" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="报告类型">
              <el-select v-model="reportConfig.type" placeholder="请选择">
                <el-option label="综合绩效报告" value="comprehensive" />
                <el-option label="风险分析报告" value="risk" />
                <el-option label="交易行为报告" value="behavior" />
                <el-option label="持仓分析报告" value="position" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="时间周期">
              <el-date-picker v-model="reportConfig.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="报告格式">
              <el-select v-model="reportConfig.format" placeholder="请选择">
                <el-option label="PDF" value="pdf" />
                <el-option label="Excel" value="excel" />
                <el-option label="Word" value="word" />
                <el-option label="HTML" value="html" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">报告内容</el-divider>
        <el-checkbox-group v-model="reportConfig.sections">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-checkbox label="overview">绩效概览</el-checkbox>
            </el-col>
            <el-col :span="6">
              <el-checkbox label="returns">收益分析</el-checkbox>
            </el-col>
            <el-col :span="6">
              <el-checkbox label="risk">风险指标</el-checkbox>
            </el-col>
            <el-col :span="6">
              <el-checkbox label="drawdown">回撤分析</el-checkbox>
            </el-col>
          </el-row>
          <el-row :gutter="20" style="margin-top: 10px;">
            <el-col :span="6">
              <el-checkbox label="position">持仓分析</el-checkbox>
            </el-col>
            <el-col :span="6">
              <el-checkbox label="behavior">交易行为</el-checkbox>
            </el-col>
            <el-col :span="6">
              <el-checkbox label="attribution">归因分析</el-checkbox>
            </el-col>
            <el-col :span="6">
              <el-checkbox label="charts">可视化图表</el-checkbox>
            </el-col>
          </el-row>
        </el-checkbox-group>
        <el-form-item label="报告标题" style="margin-top: 20px;">
          <el-input v-model="reportConfig.title" placeholder="请输入报告标题" />
        </el-form-item>
        <el-form-item label="报告备注">
          <el-input v-model="reportConfig.remarks" type="textarea" :rows="3" placeholder="请输入报告备注信息" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handlePreview">
            <el-icon><View /></el-icon>
            预览报告
          </el-button>
          <el-button type="success" @click="handleGenerate">
            <el-icon><Document /></el-icon>
            生成报告
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置配置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="templates-card" style="margin-top: 20px;">
      <template #header>
        <span>报告模板</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6" v-for="tpl in reportTemplates" :key="tpl.id">
          <el-card class="template-card" shadow="hover" @click="handleSelectTemplate(tpl)">
            <div class="template-icon">
              <el-icon :size="40" :color="tpl.color">
                <component :is="tpl.icon" />
              </el-icon>
            </div>
            <div class="template-name">{{ tpl.name }}</div>
            <div class="template-desc">{{ tpl.description }}</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="history-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>历史报告</span>
          <el-button type="primary" size="small" @click="handleRefreshHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <el-skeleton v-if="loading" :rows="8" animated />
      <el-table v-else :data="historyList" stripe style="width: 100%">
        <el-table-column prop="reportId" label="报告ID" width="150" />
        <el-table-column prop="title" label="报告标题" width="200" />
        <el-table-column prop="type" label="报告类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="报告周期" width="200" />
        <el-table-column prop="format" label="格式" width="80" />
        <el-table-column prop="createTime" label="生成时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已完成' ? 'success' : 'warning'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleDownload(scope.row)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button type="info" size="small" @click="handleView(scope.row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :total="total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" style="margin-top: 20px; justify-content: center;" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { View, Document, Refresh, Download, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface ReportTemplate {
  id: string
  name: string
  description: string
  icon: any
  color: string
}

interface HistoryReport {
  reportId: string
  title: string
  type: string
  period: string
  format: string
  createTime: string
  status: string
}

const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const reportConfig = ref({
  type: 'comprehensive',
  dateRange: null as [Date, Date] | null,
  format: 'pdf',
  sections: ['overview', 'returns', 'risk', 'drawdown', 'position', 'behavior', 'attribution', 'charts'],
  title: '绩效分析报告',
  remarks: ''
})

const reportTemplates: ReportTemplate[] = [
  { id: 'daily', name: '日报模板', description: '每日绩效概览', icon: Document, color: '#409EFF' },
  { id: 'weekly', name: '周报模板', description: '每周详细分析', icon: Document, color: '#67C23A' },
  { id: 'monthly', name: '月报模板', description: '月度综合报告', icon: Document, color: '#E6A23C' },
  { id: 'annual', name: '年报模板', description: '年度深度分析', icon: Document, color: '#F56C6C' }
]

const mockHistory: HistoryReport[] = [
  { reportId: 'R20240415001', title: '2024年4月绩效报告', type: 'comprehensive', period: '2024-04-01 至 2024-04-15', format: 'PDF', createTime: '2024-04-15 18:30:00', status: '已完成' },
  { reportId: 'R20240410001', title: '风险分析报告', type: 'risk', period: '2024-03-01 至 2024-04-10', format: 'Excel', createTime: '2024-04-10 14:20:00', status: '已完成' },
  { reportId: 'R20240405001', title: 'Q1季度报告', type: 'comprehensive', period: '2024-01-01 至 2024-03-31', format: 'PDF', createTime: '2024-04-05 10:15:00', status: '已完成' },
  { reportId: 'R20240330001', title: '交易行为分析', type: 'behavior', period: '2024-03-01 至 2024-03-30', format: 'HTML', createTime: '2024-03-30 16:45:00', status: '已完成' }
]

const historyList = ref<HistoryReport[]>(mockHistory)

const getTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'comprehensive': '综合绩效',
    'risk': '风险分析',
    'behavior': '交易行为',
    'position': '持仓分析'
  }
  return typeMap[type] || type
}

const handlePreview = () => {
  ElMessage.info('正在生成报告预览...')
}

const handleGenerate = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('报告生成成功')
  }, 2000)
}

const handleReset = () => {
  reportConfig.value = {
    type: 'comprehensive',
    dateRange: null,
    format: 'pdf',
    sections: ['overview', 'returns', 'risk', 'drawdown', 'position', 'behavior', 'attribution', 'charts'],
    title: '绩效分析报告',
    remarks: ''
  }
  ElMessage.info('已重置配置')
}

const handleSelectTemplate = (tpl: ReportTemplate) => {
  reportConfig.value.title = `${tpl.name} - ${new Date().toLocaleDateString()}`
  ElMessage.success(`已选择${tpl.name}`)
}

const handleRefreshHistory = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('已刷新')
  }, 500)
}

const handleDownload = (row: HistoryReport) => {
  ElMessage.success(`正在下载报告: ${row.title}`)
}

const handleView = (row: HistoryReport) => {
  ElMessage.info(`查看报告: ${row.title}`)
}

const handleDelete = async (row: HistoryReport) => {
  try {
    await ElMessageBox.confirm('确定要删除该报告吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('报告已删除')
  } catch {
  }
}

onMounted(() => {
  total.value = mockHistory.length
})
</script>

<style scoped>
.report-export-container {
  padding: 20px;
}

.config-card,
.templates-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-card {
  cursor: pointer;
  text-align: center;
  padding: 20px;
}

.template-icon {
  margin-bottom: 15px;
}

.template-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .report-export-container {
    padding: 10px;
  }
}
</style>

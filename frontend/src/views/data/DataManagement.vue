<template>
  <div class="data-management-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>数据管理</span>
        </div>
      </template>
      <div class="data-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="数据导入" name="import">
            <el-upload
              class="upload-demo"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              multiple>
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持CSV、Excel格式文件
                </div>
              </template>
            </el-upload>
            <div v-if="uploadedFiles.length > 0" class="file-list">
              <h4>已选择文件：</h4>
              <el-table :data="uploadedFiles" style="width: 100%">
                <el-table-column prop="name" label="文件名" />
                <el-table-column prop="size" label="大小" />
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button type="danger" size="small" link @click="removeFile(scope.$index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-button type="primary" style="margin-top: 20px;" @click="importData">开始导入</el-button>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="数据导出" name="export">
            <el-form :model="exportForm" label-width="120px">
              <el-form-item label="数据类型">
                <el-select v-model="exportForm.dataType" placeholder="请选择数据类型">
                  <el-option label="行情数据" value="market" />
                  <el-option label="财务数据" value="finance" />
                  <el-option label="因子数据" value="factor" />
                </el-select>
              </el-form-item>
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="exportForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                />
              </el-form-item>
              <el-form-item label="导出格式">
                <el-radio-group v-model="exportForm.format">
                  <el-radio label="csv">CSV</el-radio>
                  <el-radio label="excel">Excel</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="exportData">导出数据</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="数据清理" name="clean">
            <el-form :model="cleanForm" label-width="150px">
              <el-form-item label="数据类型">
                <el-select v-model="cleanForm.dataType" placeholder="请选择数据类型">
                  <el-option label="行情数据" value="market" />
                  <el-option label="财务数据" value="finance" />
                  <el-option label="所有数据" value="all" />
                </el-select>
              </el-form-item>
              <el-form-item label="清理规则">
                <el-checkbox-group v-model="cleanForm.rules">
                  <el-checkbox label="duplicate">删除重复数据</el-checkbox>
                  <el-checkbox label="missing">处理缺失值</el-checkbox>
                  <el-checkbox label="outlier">去除异常值</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="cleanForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="cleanData">开始清理</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('import')
const uploadedFiles = ref<any[]>([])

const exportForm = reactive({
  dataType: '',
  dateRange: [],
  format: 'csv'
})

const cleanForm = reactive({
  dataType: '',
  rules: [],
  dateRange: []
})

const handleFileChange = (file: any) => {
  uploadedFiles.value.push({
    name: file.name,
    size: (file.size / 1024).toFixed(2) + ' KB'
  })
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

const importData = async () => {
  try {
    await ElMessageBox.confirm('确定要导入这些文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    ElMessage.success('数据导入成功')
    uploadedFiles.value = []
  } catch {
    ElMessage.info('已取消操作')
  }
}

const exportData = () => {
  ElMessage.success('数据导出成功')
}

const cleanData = async () => {
  try {
    await ElMessageBox.confirm('数据清理操作不可逆，确定要继续吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('数据清理完成')
  } catch {
    ElMessage.info('已取消操作')
  }
}
</script>

<style scoped>
.data-management-container {
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

.upload-demo {
  width: 100%;
}

.file-list {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .data-management-container {
    padding: 10px;
  }
}
</style>

<template>
  <div class="custom-factor-container">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="editor-card">
          <template #header>
            <div class="card-header">
              <span>因子编辑器</span>
              <el-button-group>
                <el-button type="primary" size="small" @click="handleSave">
                  <el-icon><Document /></el-icon>
                  保存
                </el-button>
                <el-button type="success" size="small" @click="handleTest">
                  <el-icon><VideoPlay /></el-icon>
                  测试
                </el-button>
              </el-button-group>
            </div>
          </template>
          
          <el-form :model="factorForm" label-width="100px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="因子名称" required>
                  <el-input v-model="factorForm.name" placeholder="请输入因子名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="因子代码" required>
                  <el-input v-model="factorForm.code" placeholder="请输入因子代码" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="因子类别">
                  <el-select v-model="factorForm.category" placeholder="请选择">
                    <el-option label="技术类" value="technical" />
                    <el-option label="基本面类" value="fundamental" />
                    <el-option label="情绪类" value="sentiment" />
                    <el-option label="另类数据" value="alternative" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="回测周期">
                  <el-select v-model="factorForm.period" placeholder="请选择">
                    <el-option label="日频" value="daily" />
                    <el-option label="周频" value="weekly" />
                    <el-option label="月频" value="monthly" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="因子描述">
              <el-input v-model="factorForm.description" type="textarea" :rows="2" placeholder="请输入因子描述" />
            </el-form-item>
            <el-form-item label="因子公式">
              <div class="formula-editor-wrapper">
                <div class="toolbar">
                  <el-button-group>
                    <el-button size="small" @click="insertVariable('close')">收盘价</el-button>
                    <el-button size="small" @click="insertVariable('open')">开盘价</el-button>
                    <el-button size="small" @click="insertVariable('high')">最高价</el-button>
                    <el-button size="small" @click="insertVariable('low')">最低价</el-button>
                    <el-button size="small" @click="insertVariable('volume')">成交量</el-button>
                  </el-button-group>
                  <el-button-group style="margin-left: 10px;">
                    <el-button size="small" @click="insertFunction('MA')">MA</el-button>
                    <el-button size="small" @click="insertFunction('STD')">STD</el-button>
                    <el-button size="small" @click="insertFunction('RSI')">RSI</el-button>
                    <el-button size="small" @click="insertFunction('MACD')">MACD</el-button>
                    <el-button size="small" @click="insertFunction('CORR')">CORR</el-button>
                  </el-button-group>
                </div>
                <el-input
                  ref="formulaInputRef"
                  v-model="factorForm.formula"
                  type="textarea"
                  :rows="6"
                  placeholder="请输入因子计算公式，例如：(close - MA(close, 20)) / STD(close, 20)"
                  class="formula-input"
                />
              </div>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="code-card" style="margin-top: 20px;">
          <template #header>
            <span>Python代码实现</span>
          </template>
          <el-input
            v-model="factorForm.pythonCode"
            type="textarea"
            :rows="15"
            placeholder="请输入Python代码实现"
            class="code-input"
          />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="template-card">
          <template #header>
            <span>因子模板</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="template in factorTemplates"
              :key="template.id"
              :timestamp="template.category"
              placement="top"
            >
              <div class="template-item">
                <div class="template-name">{{ template.name }}</div>
                <div class="template-desc">{{ template.description }}</div>
                <el-button type="primary" size="small" link @click="useTemplate(template)">
                  使用模板
                </el-button>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>

        <el-card class="history-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>自定义因子历史</span>
              <el-button type="primary" size="small" link @click="loadMoreHistory">更多</el-button>
            </div>
          </template>
          <el-table :data="customFactorHistory" size="small" style="width: 100%">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
                  {{ row.status === 'active' ? '启用' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="primary" size="small" link @click="editFactor(scope.row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="deleteFactor(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="test-card" style="margin-top: 20px;">
          <template #header>
            <span>测试结果</span>
          </template>
          <el-skeleton v-if="testing" :rows="5" animated />
          <div v-else-if="testResult" class="test-result">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="IC值">{{ testResult.ic?.toFixed(4) }}</el-descriptions-item>
              <el-descriptions-item label="ICIR">{{ testResult.icir?.toFixed(4) }}</el-descriptions-item>
              <el-descriptions-item label="T值">{{ testResult.tvalue?.toFixed(4) }}</el-descriptions-item>
              <el-descriptions-item label="换手率">{{ testResult.turnover?.toFixed(2) }}%</el-descriptions-item>
              <el-descriptions-item label="收益率">{{ testResult.return?.toFixed(2) }}%</el-descriptions-item>
            </el-descriptions>
          </div>
          <el-empty v-else description="点击测试按钮查看结果" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Document, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const formulaInputRef = ref()

const factorForm = ref({
  name: '',
  code: '',
  category: 'technical',
  period: 'daily',
  description: '',
  formula: '',
  pythonCode: `def calculate_factor(data):
    """
    计算自定义因子
    data: 包含OHLCV数据的DataFrame
    返回: 因子值Series
    """
    # 在这里实现因子计算逻辑
    close = data['close']
    
    # 示例：计算标准化动量因子
    ma_20 = close.rolling(window=20).mean()
    std_20 = close.rolling(window=20).std()
    
    factor = (close - ma_20) / std_20
    
    return factor`
})

const factorTemplates = [
  {
    id: 'tpl001',
    name: '动量因子',
    category: '技术类',
    description: '基于过去N日收益率的动量因子',
    formula: '(close / shift(close, 20) - 1) * 100',
    code: 'MOMENTUM'
  },
  {
    id: 'tpl002',
    name: '反转因子',
    category: '技术类',
    description: '基于过去N日收益率的反转因子',
    formula: '(shift(close, 5) / close - 1) * 100',
    code: 'REVERSAL'
  },
  {
    id: 'tpl003',
    name: '波动率因子',
    category: '技术类',
    description: '基于历史波动率的因子',
    formula: 'STD(close, 20) / MA(close, 20)',
    code: 'VOLATILITY'
  },
  {
    id: 'tpl004',
    name: '量价因子',
    category: '技术类',
    description: '结合成交量和价格的因子',
    formula: 'CORR(volume, close, 10)',
    code: 'PRICE_VOLUME'
  }
]

const customFactorHistory = ref([
  { id: 'c001', name: '我的动量因子', status: 'active' },
  { id: 'c002', name: '改进波动率', status: 'active' },
  { id: 'c003', name: '实验因子A', status: 'inactive' }
])

const testing = ref(false)
const testResult = ref<any>(null)

const insertVariable = (variable: string) => {
  factorForm.value.formula += variable
}

const insertFunction = (func: string) => {
  factorForm.value.formula += `${func}()`
  nextTick(() => {
    const textarea = formulaInputRef.value?.textarea
    if (textarea) {
      const pos = factorForm.value.formula.length - 1
      textarea.focus()
      textarea.setSelectionRange(pos, pos)
    }
  })
}

const useTemplate = (template: any) => {
  factorForm.value.name = template.name
  factorForm.value.code = template.code
  factorForm.value.formula = template.formula
  factorForm.value.category = template.category === '技术类' ? 'technical' : 'fundamental'
  ElMessage.success('已加载模板')
}

const handleSave = async () => {
  if (!factorForm.value.name || !factorForm.value.code || !factorForm.value.formula) {
    ElMessage.error('请填写必填字段')
    return
  }
  
  try {
    await ElMessageBox.confirm('确认保存该因子吗?', '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    ElMessage.success('因子保存成功')
    customFactorHistory.value.unshift({
      id: `c${Date.now()}`,
      name: factorForm.value.name,
      status: 'active'
    })
  } catch {
  }
}

const handleTest = () => {
  testing.value = true
  testResult.value = null
  
  setTimeout(() => {
    testing.value = false
    testResult.value = {
      ic: 0.085 + Math.random() * 0.05,
      icir: 1.5 + Math.random() * 1,
      tvalue: 2.0 + Math.random() * 1.5,
      turnover: 20 + Math.random() * 30,
      return: 5 + Math.random() * 15
    }
    ElMessage.success('测试完成')
  }, 1500)
}

const editFactor = (factor: any) => {
  factorForm.value.name = factor.name
  ElMessage.info(`正在编辑: ${factor.name}`)
}

const deleteFactor = async (factor: any) => {
  try {
    await ElMessageBox.confirm(`确认删除因子 ${factor.name} 吗?`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const index = customFactorHistory.value.findIndex(f => f.id === factor.id)
    if (index > -1) {
      customFactorHistory.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch {
  }
}

const loadMoreHistory = () => {
  ElMessage.info('加载更多历史记录')
}
</script>

<style scoped>
.custom-factor-container {
  padding: 20px;
}

.editor-card,
.template-card,
.history-card,
.test-card,
.code-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.formula-editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.toolbar {
  padding: 10px;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.formula-input,
.code-input {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.template-item {
  padding: 5px 0;
}

.template-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.test-result {
  padding: 10px 0;
}

@media (max-width: 768px) {
  .custom-factor-container {
    padding: 10px;
  }
}
</style>

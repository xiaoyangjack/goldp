<template>
  <div class="capital-flow-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>资金流数据</span>
          <el-button type="primary" size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="data-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="summary-card">
              <template #header>
                <div class="card-header">今日资金概览</div>
              </template>
              <el-skeleton v-if="loading" :rows="4" animated />
              <div v-else class="summary-content">
                <div class="summary-item">
                  <span class="label">主力净流入</span>
                  <span class="value positive">+12.34亿</span>
                </div>
                <div class="summary-item">
                  <span class="label">超大单净流入</span>
                  <span class="value positive">+8.56亿</span>
                </div>
                <div class="summary-item">
                  <span class="label">大单净流入</span>
                  <span class="value positive">+3.78亿</span>
                </div>
                <div class="summary-item">
                  <span class="label">中单净流入</span>
                  <span class="value negative">-1.23亿</span>
                </div>
                <div class="summary-item">
                  <span class="label">小单净流入</span>
                  <span class="value negative">-0.56亿</span>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">资金流向趋势</div>
              </template>
              <el-skeleton v-if="loading" :rows="8" animated />
              <div v-else ref="chartRef" class="chart" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card class="list-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>个股资金流向</span>
            </div>
          </template>
          <el-skeleton v-if="loading" :rows="8" animated />
          <el-table v-else :data="stockFlowData" stripe style="width: 100%">
            <el-table-column prop="code" label="代码" width="100" />
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="price" label="最新价" width="100" />
            <el-table-column prop="change" label="涨跌幅" width="100">
              <template #default="scope">
                <span :class="scope.row.change >= 0 ? 'positive' : 'negative'">
                  {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="netInflow" label="主力净流入" width="120">
              <template #default="scope">
                <span :class="scope.row.netInflow >= 0 ? 'positive' : 'negative'">
                  {{ scope.row.netInflow >= 0 ? '+' : '' }}{{ scope.row.netInflow }}亿
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="netInflowRate" label="净占比" width="100">
              <template #default="scope">
                <span :class="scope.row.netInflowRate >= 0 ? 'positive' : 'negative'">
                  {{ scope.row.netInflowRate >= 0 ? '+' : '' }}{{ scope.row.netInflowRate }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const chartRef = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()

const stockFlowData = ref([
  { code: '600519', name: '贵州茅台', price: 1850.00, change: 2.3, netInflow: 5.67, netInflowRate: 12.3 },
  { code: '000858', name: '五粮液', price: 156.78, change: 1.8, netInflow: 3.45, netInflowRate: 8.7 },
  { code: '601318', name: '中国平安', price: 45.67, change: -0.5, netInflow: -1.23, netInflowRate: -3.2 },
  { code: '000001', name: '平安银行', price: 12.34, change: 0.8, netInflow: 0.89, netInflowRate: 5.6 },
  { code: '600036', name: '招商银行', price: 32.45, change: 1.2, netInflow: 2.34, netInflowRate: 7.8 }
])

const initChart = () => {
  if (process.env.NODE_ENV !== 'test' && chartRef.value) {
    chart.value = echarts.init(chartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['主力净流入', '超大单净流入', '大单净流入']
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
        data: ['09:30', '10:00', '10:30', '11:00', '11:30', '13:00', '13:30', '14:00', '14:30', '15:00']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}亿'
        }
      },
      series: [
        {
          name: '主力净流入',
          type: 'line',
          data: [2.1, 3.5, 5.2, 6.8, 8.5, 9.3, 10.7, 11.2, 12.5, 12.3],
          smooth: true,
          lineStyle: {
            color: '#165DFF'
          },
          areaStyle: {
            color: 'rgba(22, 93, 255, 0.1)'
          }
        },
        {
          name: '超大单净流入',
          type: 'line',
          data: [1.2, 2.5, 3.8, 4.5, 5.8, 6.5, 7.2, 7.8, 8.5, 8.6],
          smooth: true,
          lineStyle: {
            color: '#67C23A'
          }
        },
        {
          name: '大单净流入',
          type: 'line',
          data: [0.9, 1.0, 1.4, 2.3, 2.7, 2.8, 3.5, 3.4, 4.0, 3.7],
          smooth: true,
          lineStyle: {
            color: '#E6A23C'
          }
        }
      ]
    }
    chart.value.setOption(option)
  }
}

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 1000)
}

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.capital-flow-container {
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

.summary-content {
  padding: 10px 0;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.summary-item .label {
  color: #606266;
}

.summary-item .value {
  font-weight: bold;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.chart {
  width: 100%;
  height: 300px;
}

@media (max-width: 768px) {
  .capital-flow-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
}
</style>

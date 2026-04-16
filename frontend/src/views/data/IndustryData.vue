<template>
  <div class="industry-data-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>行业数据</span>
          <el-button type="primary" size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="data-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="行业指数" name="index">
            <el-skeleton v-if="loading" :rows="10" animated />
            <el-table v-else :data="industryIndexData" stripe style="width: 100%">
              <el-table-column prop="name" label="行业名称" width="150" />
              <el-table-column prop="index" label="指数" width="120" />
              <el-table-column prop="change" label="涨跌幅" width="100">
                <template #default="scope">
                  <span :class="scope.row.change >= 0 ? 'positive' : 'negative'">
                    {{ scope.row.change >= 0 ? '+' : '' }}{{ scope.row.change }}%
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="leadStock" label="领涨股" width="120" />
              <el-table-column prop="leadChange" label="领涨股涨幅" width="120">
                <template #default="scope">
                  <span class="positive">+{{ scope.row.leadChange }}%</span>
                </template>
              </el-table-column>
              <el-table-column prop="turnover" label="换手率" width="100" />
              <el-table-column prop="pe" label="PE" width="80" />
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="行业轮动" name="rotation">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <div class="card-header">近一月行业涨幅</div>
                  </template>
                  <el-skeleton v-if="loading" :rows="8" animated />
                  <div v-else ref="barChartRef" class="chart" style="height: 350px;"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <div class="card-header">行业轮动热力图</div>
                  </template>
                  <el-skeleton v-if="loading" :rows="8" animated />
                  <div v-else ref="heatmapChartRef" class="chart" style="height: 350px;"></div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('index')
const loading = ref(false)
const barChartRef = ref<HTMLElement>()
const heatmapChartRef = ref<HTMLElement>()
const barChart = ref<echarts.ECharts>()
const heatmapChart = ref<echarts.ECharts>()

const industryIndexData = ref([
  { name: '电力设备', index: 5234.56, change: 3.2, leadStock: '宁德时代', leadChange: 5.6, turnover: '3.5%', pe: 45 },
  { name: '汽车', index: 4123.45, change: 2.8, leadStock: '比亚迪', leadChange: 4.2, turnover: '4.2%', pe: 38 },
  { name: '有色金属', index: 3876.54, change: 2.1, leadStock: '紫金矿业', leadChange: 3.8, turnover: '5.1%', pe: 25 },
  { name: '电子', index: 4567.89, change: 1.5, leadStock: '立讯精密', leadChange: 3.1, turnover: '3.8%', pe: 42 },
  { name: '医药生物', index: 3234.56, change: -0.5, leadStock: '恒瑞医药', leadChange: 1.2, turnover: '2.8%', pe: 55 },
  { name: '房地产', index: 2123.45, change: -1.2, leadStock: '万科A', leadChange: 0.5, turnover: '1.8%', pe: 18 }
])

const initBarChart = () => {
  if (process.env.NODE_ENV !== 'test' && barChartRef.value) {
    barChart.value = echarts.init(barChartRef.value)
    const industries = ['电力设备', '汽车', '有色金属', '电子', '计算机', '医药生物', '房地产', '银行']
    const data = [12.5, 10.3, 8.7, 7.2, 5.8, 2.1, -1.5, -2.3]
    const colors = data.map(val => val >= 0 ? '#67C23A' : '#F56C6C')
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      yAxis: {
        type: 'category',
        data: industries
      },
      series: [
        {
          name: '涨幅',
          type: 'bar',
          data: data.map((value, index) => ({
            value: value,
            itemStyle: {
              color: colors[index]
            }
          }))
        }
      ]
    }
    barChart.value.setOption(option)
  }
}

const initHeatmapChart = () => {
  if (process.env.NODE_ENV !== 'test' && heatmapChartRef.value) {
    heatmapChart.value = echarts.init(heatmapChartRef.value)
    const industries = ['电力设备', '汽车', '有色金属', '电子', '计算机', '医药生物']
    const months = ['1月', '2月', '3月', '4月', '5月', '6月']
    
    const data = []
    for (let i = 0; i < industries.length; i++) {
      for (let j = 0; j < months.length; j++) {
        data.push([j, i, (Math.random() - 0.3) * 20])
      }
    }
    
    const option = {
      tooltip: {
        position: 'top',
        formatter: (params: any) => {
          return `${industries[params.data[1]]} ${months[params.data[0]]}<br/>涨幅: ${params.data[2].toFixed(2)}%`
        }
      },
      grid: {
        height: '50%',
        top: '10%'
      },
      xAxis: {
        type: 'category',
        data: months,
        splitArea: {
          show: true
        }
      },
      yAxis: {
        type: 'category',
        data: industries,
        splitArea: {
          show: true
        }
      },
      visualMap: {
        min: -10,
        max: 10,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: {
          color: ['#F56C6C', '#FFFFFF', '#67C23A']
        }
      },
      series: [
        {
          name: '行业涨幅',
          type: 'heatmap',
          data: data,
          label: {
            show: true
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    heatmapChart.value.setOption(option)
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
  initBarChart()
  initHeatmapChart()
})
</script>

<style scoped>
.industry-data-container {
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

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.chart {
  width: 100%;
  height: 350px;
}

@media (max-width: 768px) {
  .industry-data-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
}
</style>

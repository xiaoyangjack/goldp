<template>
  <div class="news-sentiment-container">
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>新闻舆情</span>
          <el-button type="primary" size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div class="data-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="sentiment-card">
              <template #header>
                <div class="card-header">市场情绪</div>
              </template>
              <el-skeleton v-if="loading" :rows="5" animated />
              <div v-else class="sentiment-content">
                <div class="sentiment-score">
                  <div class="score-value" :class="sentimentScore >= 50 ? 'positive' : 'negative'">
                    {{ sentimentScore }}
                  </div>
                  <div class="score-label">情绪指数</div>
                </div>
                <div class="sentiment-stats">
                  <div class="stat-item">
                    <span class="stat-label">正面新闻</span>
                    <span class="stat-value positive">{{ positiveNews }}条</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">负面新闻</span>
                    <span class="stat-value negative">{{ negativeNews }}条</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">中性新闻</span>
                    <span class="stat-value">{{ neutralNews }}条</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="16">
            <el-card class="chart-card">
              <template #header>
                <div class="card-header">情绪趋势</div>
              </template>
              <el-skeleton v-if="loading" :rows="8" animated />
              <div v-else ref="chartRef" class="chart" style="height: 300px;"></div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card class="news-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>财经新闻</span>
              <div class="header-actions">
                <el-radio-group v-model="newsType" size="small">
                  <el-radio-button label="all">全部</el-radio-button>
                  <el-radio-button label="positive">正面</el-radio-button>
                  <el-radio-button label="negative">负面</el-radio-button>
                  <el-radio-button label="neutral">中性</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>
          <el-skeleton v-if="loading" :rows="8" animated />
          <div v-else class="news-list">
            <div v-for="item in filteredNews" :key="item.id" class="news-item">
              <div class="news-header">
                <el-tag :type="getSentimentType(item.sentiment)" size="small">
                  {{ getSentimentLabel(item.sentiment) }}
                </el-tag>
                <span class="news-source">{{ item.source }}</span>
                <span class="news-time">{{ item.time }}</span>
              </div>
              <div class="news-title" @click="viewNews(item)">
                {{ item.title }}
              </div>
              <div class="news-summary">{{ item.summary }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const loading = ref(false)
const newsType = ref('all')
const chartRef = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()

const sentimentScore = ref(65)
const positiveNews = ref(45)
const negativeNews = ref(20)
const neutralNews = ref(35)

const newsData = ref([
  { id: 1, title: '央行降准0.5个百分点，释放长期资金约1万亿元', summary: '中国人民银行决定下调金融机构存款准备金率0.5个百分点，本次下调后，金融机构加权平均存款准备金率约为7.6%。', source: '新华社', time: '2024-01-15 10:30', sentiment: 'positive' },
  { id: 2, title: '新能源汽车销量再创新高，产业链受益明显', summary: '据中汽协数据，12月新能源汽车销量达120万辆，同比增长45%，全年销量突破1000万辆。', source: '证券时报', time: '2024-01-15 09:15', sentiment: 'positive' },
  { id: 3, title: '房地产市场持续低迷，多家房企债务承压', summary: '受市场需求不足影响，房地产销售持续下滑，部分房企面临较大的债务偿还压力。', source: '经济观察报', time: '2024-01-14 16:45', sentiment: 'negative' },
  { id: 4, title: '科创板注册制改革深化，更多优质企业有望上市', summary: '监管层表示将进一步深化科创板注册制改革，优化上市条件，提升市场包容性和吸引力。', source: '上海证券报', time: '2024-01-14 14:20', sentiment: 'neutral' },
  { id: 5, title: '消费电子行业复苏迹象明显，苹果供应链订单增长', summary: '随着全球经济逐步复苏，消费电子需求有所回升，苹果主要供应商四季度订单环比增长15%。', source: '第一财经', time: '2024-01-14 11:30', sentiment: 'positive' }
])

const filteredNews = computed(() => {
  if (newsType.value === 'all') return newsData.value
  return newsData.value.filter(item => item.sentiment === newsType.value)
})

const getSentimentType = (sentiment: string) => {
  const map: Record<string, any> = { positive: 'success', negative: 'danger', neutral: 'info' }
  return map[sentiment] || 'info'
}

const getSentimentLabel = (sentiment: string) => {
  const map: Record<string, string> = { positive: '正面', negative: '负面', neutral: '中性' }
  return map[sentiment] || '中性'
}

const initChart = () => {
  if (process.env.NODE_ENV !== 'test' && chartRef.value) {
    chart.value = echarts.init(chartRef.value)
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['情绪指数', '正面新闻占比']
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
        data: ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00']
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: [
        {
          name: '情绪指数',
          type: 'line',
          data: [55, 58, 62, 60, 63, 65, 65],
          smooth: true,
          lineStyle: {
            color: '#165DFF'
          },
          areaStyle: {
            color: 'rgba(22, 93, 255, 0.1)'
          }
        },
        {
          name: '正面新闻占比',
          type: 'line',
          data: [45, 48, 52, 50, 55, 58, 58],
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

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
  }, 1000)
}

const viewNews = (item: any) => {
  ElMessage.info(`查看新闻：${item.title}`)
}

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.news-sentiment-container {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.data-content {
  padding: 10px 0;
}

.sentiment-content {
  padding: 20px 0;
  text-align: center;
}

.sentiment-score {
  margin-bottom: 30px;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 10px;
}

.score-label {
  font-size: 14px;
  color: #606266;
}

.positive {
  color: #67C23A;
}

.negative {
  color: #F56C6C;
}

.sentiment-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: bold;
}

.news-list {
  padding: 10px 0;
}

.news-item {
  padding: 15px 0;
  border-bottom: 1px solid #EBEEF5;
}

.news-item:last-child {
  border-bottom: none;
}

.news-header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.news-source {
  font-size: 12px;
  color: #909399;
}

.news-time {
  font-size: 12px;
  color: #909399;
}

.news-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
  cursor: pointer;
}

.news-title:hover {
  color: #165DFF;
}

.news-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.chart {
  width: 100%;
  height: 300px;
}

@media (max-width: 768px) {
  .news-sentiment-container {
    padding: 10px;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}
</style>

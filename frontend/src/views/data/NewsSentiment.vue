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
import { newsApi } from '../../api'

const loading = ref(false)
const newsType = ref('all')
const chartRef = ref<HTMLElement>()
const chart = ref<echarts.ECharts>()

const sentimentScore = ref(65)
const positiveNews = ref(45)
const negativeNews = ref(20)
const neutralNews = ref(35)

const newsData = ref<any[]>([])

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

const fetchSentimentStats = async () => {
  try {
    const response = await newsApi.getSentimentStats()
    if (response.code === 200) {
      sentimentScore.value = response.data.sentiment_score
      positiveNews.value = response.data.positive_news
      negativeNews.value = response.data.negative_news
      neutralNews.value = response.data.neutral_news
    }
  } catch (error) {
    console.error('Failed to get sentiment stats:', error)
  }
}

const fetchNewsList = async () => {
  try {
    const response = await newsApi.getNewsList()
    if (response.code === 200) {
      newsData.value = response.data
    }
  } catch (error) {
    console.error('Failed to get news list:', error)
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([fetchSentimentStats(), fetchNewsList()])
    ElMessage.success('刷新成功')
  } catch (error) {
    console.error('Failed to refresh data:', error)
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const viewNews = (item: any) => {
  if (item.url) {
    window.open(item.url, '_blank')
  } else {
    ElMessage.info(`查看新闻：${item.title}`)
  }
}

onMounted(async () => {
  initChart()
  await refreshData()
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

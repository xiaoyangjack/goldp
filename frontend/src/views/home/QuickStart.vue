<template>
  <div class="quickstart-container">
    <el-card class="quickstart-card">
      <template #header>
        <div class="card-header">
          <span>快速开始</span>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="24">
          <el-alert
            title="欢迎使用GoldQuant量化投研平台"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            <template #default>
              以下是快速开始指南，帮助您在5分钟内开始使用平台的核心功能。
            </template>
          </el-alert>
        </el-col>
      </el-row>
      
      <el-timeline>
        <el-timeline-item
          v-for="(item, index) in quickStartItems"
          :key="index"
          :timestamp="item.time"
          placement="top"
          :type="item.type"
        >
          <el-card>
            <h4>{{ item.title }}</h4>
            <p>{{ item.description }}</p>
            <el-button type="primary" size="small" @click="goToRoute(item.route)">
              立即前往
            </el-button>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      
      <el-divider />
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <el-card class="shortcut-card" shadow="hover" @click="goToRoute('/data/market')">
            <el-icon :size="30" style="color: #165DFF;"><DataLine /></el-icon>
            <h4>查看行情数据</h4>
            <p>浏览市场行情数据</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="shortcut-card" shadow="hover" @click="goToRoute('/strategy/templates')">
            <el-icon :size="30" style="color: #67C23A;"><MagicStick /></el-icon>
            <h4>使用策略模板</h4>
            <p>从模板库选择策略</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="shortcut-card" shadow="hover" @click="goToRoute('/trading/order')">
            <el-icon :size="30" style="color: #E6A23C;"><TrendCharts /></el-icon>
            <h4>开始模拟交易</h4>
            <p>体验模拟交易功能</p>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { DataLine, MagicStick, TrendCharts } from '@element-plus/icons-vue'

const router = useRouter()

const quickStartItems = ref([
  {
    time: '第1步',
    title: '浏览市场数据',
    description: '在数据中心查看最新的市场行情数据，了解市场动态。',
    route: '/data/market',
    type: 'primary'
  },
  {
    time: '第2步',
    title: '研究投资因子',
    description: '在因子研究模块探索有效的投资因子，为策略开发做准备。',
    route: '/factor/library',
    type: 'success'
  },
  {
    time: '第3步',
    title: '选择或开发策略',
    description: '从策略模板库选择策略，或使用策略编辑器开发您的专属策略。',
    route: '/strategy/templates',
    type: 'warning'
  },
  {
    time: '第4步',
    title: '运行策略回测',
    description: '在回测引擎中运行策略回测，验证策略的历史表现。',
    route: '/backtest/execution',
    type: 'danger'
  },
  {
    time: '第5步',
    title: '开始模拟交易',
    description: '满意回测结果后，在模拟交易中开始实盘模拟，感受真实交易体验。',
    route: '/trading/overview',
    type: 'info'
  }
])

const goToRoute = (route: string) => {
  router.push(route)
}
</script>

<style scoped>
.quickstart-container {
  padding: 20px;
}

.quickstart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.shortcut-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.shortcut-card:hover {
  transform: translateY(-5px);
}

.shortcut-card h4 {
  margin: 10px 0 5px 0;
}

.shortcut-card p {
  color: #909399;
  font-size: 14px;
}
</style>

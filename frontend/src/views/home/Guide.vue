<template>
  <div class="guide-container">
    <el-card class="guide-card">
      <template #header>
        <div class="card-header">
          <span>新手引导</span>
        </div>
      </template>
      <el-steps :active="currentStep" finish-status="success" align-center style="margin: 40px 0;">
        <el-step title="注册登录" description="创建账户并登录系统" />
        <el-step title="数据导入" description="导入市场数据" />
        <el-step title="因子研究" description="研究有效因子" />
        <el-step title="策略开发" description="开发交易策略" />
        <el-step title="策略回测" description="回测验证策略" />
        <el-step title="模拟交易" description="进行模拟交易" />
      </el-steps>
      
      <el-divider content-position="left">快速开始</el-divider>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="step-card" shadow="hover" @click="goToStep(0)">
            <el-icon class="step-icon" :size="40"><User /></el-icon>
            <h3>第一步：注册登录</h3>
            <p>创建您的GoldQuant账户，开始量化投研之旅</p>
            <el-button type="primary" link>立即开始</el-button>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="step-card" shadow="hover" @click="goToStep(1)">
            <el-icon class="step-icon" :size="40"><DataLine /></el-icon>
            <h3>第二步：数据导入</h3>
            <p>导入市场数据，获取基础研究素材</p>
            <el-button type="primary" link>查看数据</el-button>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card class="step-card" shadow="hover" @click="goToStep(2)">
            <el-icon class="step-icon" :size="40"><Histogram /></el-icon>
            <h3>第三步：因子研究</h3>
            <p>研究和选择有效的投资因子</p>
            <el-button type="primary" link>因子研究</el-button>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card class="step-card" shadow="hover" @click="goToStep(3)">
            <el-icon class="step-icon" :size="40"><MagicStick /></el-icon>
            <h3>第四步：策略开发</h3>
            <p>基于因子开发您的交易策略</p>
            <el-button type="primary" link>策略开发</el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, DataLine, Histogram, MagicStick } from '@element-plus/icons-vue'

const router = useRouter()
const currentStep = ref(0)

const goToStep = (step: number) => {
  currentStep.value = step
  const routes = ['/home/overview', '/data/market', '/factor/library', '/strategy/templates']
  if (routes[step]) {
    router.push(routes[step])
  }
}
</script>

<style scoped>
.guide-container {
  padding: 20px;
}

.guide-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.step-card:hover {
  transform: translateY(-5px);
}

.step-icon {
  color: #165DFF;
  margin-bottom: 10px;
}

.step-card h3 {
  margin: 10px 0;
  color: #303133;
}

.step-card p {
  color: #909399;
  margin-bottom: 15px;
}
</style>

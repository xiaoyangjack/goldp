<template>
  <div class="sidebar-container">
    <div class="logo">
      <h1>GoldQuant</h1>
    </div>
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      background-color="#165DFF"
      text-color="#fff"
      active-text-color="#ffd04b"
      @select="handleMenuSelect"
    >
      <el-sub-menu index="1">
        <template #title>
          <el-icon><House /></el-icon>
          <span>首页</span>
        </template>
        <el-menu-item index="/home/overview">平台概览</el-menu-item>
        <el-menu-item index="/home/guide">新手引导</el-menu-item>
        <el-menu-item index="/home/quickstart">快速开始</el-menu-item>
        <el-menu-item index="/home/favorites">我的收藏</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="2">
        <template #title>
          <el-icon><DataLine /></el-icon>
          <span>数据中心</span>
        </template>
        <el-menu-item index="/data/market">行情数据</el-menu-item>
        <el-menu-item index="/data/fundamental">基本面数据</el-menu-item>
        <el-menu-item index="/data/capital">资金流数据</el-menu-item>
        <el-menu-item index="/data/industry">行业数据</el-menu-item>
        <el-menu-item index="/data/news">新闻舆情</el-menu-item>
        <el-menu-item index="/data/management">数据管理</el-menu-item>
        <el-menu-item index="/data/api">API接入</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="3">
        <template #title>
          <el-icon><Histogram /></el-icon>
          <span>因子研究</span>
        </template>
        <el-menu-item index="/factor/library">因子库</el-menu-item>
        <el-menu-item index="/factor/calculation">因子计算</el-menu-item>
        <el-menu-item index="/factor/preprocessing">因子预处理</el-menu-item>
        <el-menu-item index="/factor/analysis">因子有效性分析</el-menu-item>
        <el-menu-item index="/factor/selection">因子筛选</el-menu-item>
        <el-menu-item index="/factor/visualization">因子可视化</el-menu-item>
        <el-menu-item index="/factor/custom">自定义因子</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="4">
        <template #title>
          <el-icon><MagicStick /></el-icon>
          <span>策略开发</span>
        </template>
        <el-menu-item index="/strategy/templates">策略模板库</el-menu-item>
        <el-menu-item index="/strategy/editor">策略编辑器</el-menu-item>
        <el-menu-item index="/strategy/parameters">参数配置</el-menu-item>
        <el-menu-item index="/strategy/debug">策略调试</el-menu-item>
        <el-menu-item index="/strategy/custom">自定义策略</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="5">
        <template #title>
          <el-icon><Timer /></el-icon>
          <span>回测引擎</span>
        </template>
        <el-menu-item index="/backtest/tasks">回测任务管理</el-menu-item>
        <el-menu-item index="/backtest/execution">回测执行</el-menu-item>
        <el-menu-item index="/backtest/report">回测报告</el-menu-item>
        <el-menu-item index="/backtest/optimization">参数优化</el-menu-item>
        <el-menu-item index="/backtest/sensitivity">敏感性分析</el-menu-item>
        <el-menu-item index="/backtest/overfitting">过拟合检验</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="6">
        <template #title>
          <el-icon><TrendCharts /></el-icon>
          <span>模拟交易</span>
        </template>
        <el-menu-item index="/trading/overview">模拟账户总览</el-menu-item>
        <el-menu-item index="/trading/order">交易下单</el-menu-item>
        <el-menu-item index="/trading/position">持仓管理</el-menu-item>
        <el-menu-item index="/trading/entrust">委托记录</el-menu-item>
        <el-menu-item index="/trading/execution">成交明细</el-menu-item>
        <el-menu-item index="/trading/settlement">交割单</el-menu-item>
        <el-menu-item index="/trading/risk">风险控制</el-menu-item>
        <el-menu-item index="/trading/condition">条件单管理</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="7">
        <template #title>
          <el-icon><PieChart /></el-icon>
          <span>绩效分析</span>
        </template>
        <el-menu-item index="/performance/return">收益分析</el-menu-item>
        <el-menu-item index="/performance/risk">风险分析</el-menu-item>
        <el-menu-item index="/performance/attribution">归因分析</el-menu-item>
        <el-menu-item index="/performance/position">持仓分析</el-menu-item>
        <el-menu-item index="/performance/behavior">交易行为分析</el-menu-item>
        <el-menu-item index="/performance/export">报告导出</el-menu-item>
      </el-sub-menu>
      <el-sub-menu index="8">
        <template #title>
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </template>
        <el-menu-item index="/settings/account">账户设置</el-menu-item>
        <el-menu-item index="/settings/api">API配置</el-menu-item>
        <el-menu-item index="/settings/market">行情设置</el-menu-item>
        <el-menu-item index="/settings/rules">交易规则设置</el-menu-item>
        <el-menu-item index="/settings/cache">数据缓存</el-menu-item>
        <el-menu-item index="/settings/help">帮助中心</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { House, DataLine, Histogram, MagicStick, Timer, TrendCharts, PieChart, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const activeMenu = ref('')

const handleMenuSelect = (key: string) => {
  router.push(key)
  // 手动更新activeMenu
  activeMenu.value = key
}

const updateActiveMenu = () => {
  const currentPath = router.currentRoute.value.path
  activeMenu.value = currentPath
}

onMounted(() => {
  updateActiveMenu()
  router.afterEach(updateActiveMenu)
  
  // 确保初始路由正确设置
  activeMenu.value = router.currentRoute.value.path
})
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  color: white;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
}

.sidebar-menu :deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 40px;
  line-height: 40px;
}
</style>
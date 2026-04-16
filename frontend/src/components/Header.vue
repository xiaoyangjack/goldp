<template>
  <div class="header-container">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="item in breadcrumbItems" :key="item.path">
          <router-link v-if="item.path" :to="item.path">{{ item.title }}</router-link>
          <span v-else>{{ item.title }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right">
      <el-dropdown>
        <span class="user-info">
          <el-avatar :size="32" :src="userAvatar"></el-avatar>
          <span class="user-name">{{ userName }}</span>
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人中心</el-dropdown-item>
            <el-dropdown-item>账户设置</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <el-button type="primary" size="small" style="margin-left: 10px;">
        <el-icon><Plus /></el-icon>
        新建
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const userName = ref('用户')
const userAvatar = ref('')

const breadcrumbItems = computed(() => {
  const path = router.currentRoute.value.path
  const segments = path.split('/').filter(Boolean)
  const items = [
    { title: '首页', path: '/' }
  ]

  let currentPath = ''
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`
    let title = segment
    
    // 映射路径到中文标题
    const titleMap: Record<string, string> = {
      'home': '首页',
      'overview': '平台概览',
      'guide': '新手引导',
      'quickstart': '快速开始',
      'favorites': '我的收藏',
      'data': '数据中心',
      'market': '行情数据',
      'fundamental': '基本面数据',
      'capital': '资金流数据',
      'industry': '行业数据',
      'news': '新闻舆情',
      'management': '数据管理',
      'api': 'API接入',
      'factor': '因子研究',
      'library': '因子库',
      'calculation': '因子计算',
      'preprocessing': '因子预处理',
      'analysis': '因子有效性分析',
      'selection': '因子筛选',
      'visualization': '因子可视化',
      'custom': '自定义因子',
      'strategy': '策略开发',
      'templates': '策略模板库',
      'editor': '策略编辑器',
      'parameters': '参数配置',
      'debug': '策略调试',
      'backtest': '回测引擎',
      'tasks': '回测任务管理',
      'execution': '回测执行',
      'report': '回测报告',
      'optimization': '参数优化',
      'sensitivity': '敏感性分析',
      'overfitting': '过拟合检验',
      'trading': '模拟交易',
      'position': '持仓管理',
      'entrust': '委托记录',
      'settlement': '交割单',
      'risk': '风险控制',
      'condition': '条件单管理',
      'performance': '绩效分析',
      'return': '收益分析',
      'risk': '风险分析',
      'attribution': '归因分析',
      'position': '持仓分析',
      'behavior': '交易行为分析',
      'export': '报告导出',
      'settings': '系统设置',
      'account': '账户设置',
      'market': '行情设置',
      'rules': '交易规则设置',
      'cache': '数据缓存',
      'help': '帮助中心'
    }

    if (titleMap[segment]) {
      title = titleMap[segment]
    }

    items.push({
      title,
      path: index === segments.length - 1 ? '' : currentPath
    })
  })

  return items
})
</script>

<style scoped>
.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-name {
  margin: 0 10px;
  font-size: 14px;
}

.el-breadcrumb {
  font-size: 14px;
}
</style>
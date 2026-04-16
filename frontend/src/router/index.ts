import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/home/overview'
  },
  {
    path: '/home',
    redirect: '/home/overview',
    children: [
      {
        path: 'overview',
        name: 'HomeOverview',
        component: () => import('../views/home/Overview.vue')
      },
      {
        path: 'guide',
        name: 'HomeGuide',
        component: () => import('../views/home/Overview.vue')
      },
      {
        path: 'quickstart',
        name: 'HomeQuickStart',
        component: () => import('../views/home/Overview.vue')
      },
      {
        path: 'favorites',
        name: 'HomeFavorites',
        component: () => import('../views/home/Favorites.vue')
      }
    ]
  },
  {
    path: '/data',
    redirect: '/data/market',
    children: [
      {
        path: 'market',
        name: 'DataMarket',
        component: () => import('../views/data/DataCenter.vue')
      },
      {
        path: 'fundamental',
        name: 'DataFundamental',
        component: () => import('../views/data/FundamentalData.vue')
      },
      {
        path: 'capital',
        name: 'DataCapital',
        component: () => import('../views/data/CapitalFlowData.vue')
      },
      {
        path: 'industry',
        name: 'DataIndustry',
        component: () => import('../views/data/IndustryData.vue')
      },
      {
        path: 'news',
        name: 'DataNews',
        component: () => import('../views/data/NewsSentiment.vue')
      },
      {
        path: 'management',
        name: 'DataManagement',
        component: () => import('../views/data/DataManagement.vue')
      },
      {
        path: 'api',
        name: 'DataApi',
        component: () => import('../views/data/ApiAccess.vue')
      }
    ]
  },
  {
    path: '/factor',
    redirect: '/factor/library',
    children: [
      {
        path: 'library',
        name: 'FactorLibrary',
        component: () => import('../views/factor/FactorResearch.vue')
      },
      {
        path: 'calculation',
        name: 'FactorCalculation',
        component: () => import('../views/factor/FactorCalculation.vue')
      },
      {
        path: 'preprocessing',
        name: 'FactorPreprocessing',
        component: () => import('../views/factor/FactorPreprocessing.vue')
      },
      {
        path: 'analysis',
        name: 'FactorAnalysis',
        component: () => import('../views/factor/FactorAnalysis.vue')
      },
      {
        path: 'selection',
        name: 'FactorSelection',
        component: () => import('../views/factor/FactorSelection.vue')
      },
      {
        path: 'visualization',
        name: 'FactorVisualization',
        component: () => import('../views/factor/FactorVisualization.vue')
      },
      {
        path: 'custom',
        name: 'FactorCustom',
        component: () => import('../views/factor/CustomFactor.vue')
      }
    ]
  },
  {
    path: '/strategy',
    redirect: '/strategy/templates',
    children: [
      {
        path: 'templates',
        name: 'StrategyTemplates',
        component: () => import('../views/strategy/StrategyDevelopment.vue')
      },
      {
        path: 'editor',
        name: 'StrategyEditor',
        component: () => import('../views/strategy/StrategyEditor.vue')
      },
      {
        path: 'parameters',
        name: 'StrategyParameters',
        component: () => import('../views/strategy/StrategyParameters.vue')
      },
      {
        path: 'debug',
        name: 'StrategyDebug',
        component: () => import('../views/strategy/StrategyDebug.vue')
      },
      {
        path: 'custom',
        name: 'StrategyCustom',
        component: () => import('../views/strategy/CustomStrategy.vue')
      }
    ]
  },
  {
    path: '/backtest',
    redirect: '/backtest/tasks',
    children: [
      {
        path: 'tasks',
        name: 'BacktestTasks',
        component: () => import('../views/backtest/BacktestTasks.vue')
      },
      {
        path: 'execution',
        name: 'BacktestExecution',
        component: () => import('../views/backtest/BacktestEngine.vue')
      },
      {
        path: 'report',
        name: 'BacktestReport',
        component: () => import('../views/backtest/BacktestReport.vue')
      },
      {
        path: 'optimization',
        name: 'BacktestOptimization',
        component: () => import('../views/backtest/ParameterOptimization.vue')
      },
      {
        path: 'sensitivity',
        name: 'BacktestSensitivity',
        component: () => import('../views/backtest/SensitivityAnalysis.vue')
      },
      {
        path: 'overfitting',
        name: 'BacktestOverfitting',
        component: () => import('../views/backtest/OverfittingCheck.vue')
      }
    ]
  },
  {
    path: '/trading',
    redirect: '/trading/overview',
    children: [
      {
        path: 'overview',
        name: 'TradingOverview',
        component: () => import('../views/trading/AccountOverview.vue')
      },
      {
        path: 'order',
        name: 'TradingOrder',
        component: () => import('../views/trading/PaperTrading.vue')
      },
      {
        path: 'position',
        name: 'TradingPosition',
        component: () => import('../views/trading/PositionManagement.vue')
      },
      {
        path: 'entrust',
        name: 'TradingEntrust',
        component: () => import('../views/trading/EntrustRecords.vue')
      },
      {
        path: 'execution',
        name: 'TradingExecution',
        component: () => import('../views/trading/TradeDetails.vue')
      },
      {
        path: 'settlement',
        name: 'TradingSettlement',
        component: () => import('../views/trading/SettlementSheet.vue')
      },
      {
        path: 'risk',
        name: 'TradingRisk',
        component: () => import('../views/trading/RiskControl.vue')
      },
      {
        path: 'condition',
        name: 'TradingCondition',
        component: () => import('../views/trading/ConditionOrder.vue')
      }
    ]
  },
  {
    path: '/performance',
    redirect: '/performance/return',
    children: [
      {
        path: 'return',
        name: 'PerformanceReturn',
        component: () => import('../views/performance/PerformanceAnalysis.vue')
      },
      {
        path: 'risk',
        name: 'PerformanceRisk',
        component: () => import('../views/performance/RiskAnalysis.vue')
      },
      {
        path: 'attribution',
        name: 'PerformanceAttribution',
        component: () => import('../views/performance/AttributionAnalysis.vue')
      },
      {
        path: 'position',
        name: 'PerformancePosition',
        component: () => import('../views/performance/PositionAnalysis.vue')
      },
      {
        path: 'behavior',
        name: 'PerformanceBehavior',
        component: () => import('../views/performance/BehaviorAnalysis.vue')
      },
      {
        path: 'export',
        name: 'PerformanceExport',
        component: () => import('../views/performance/ReportExport.vue')
      }
    ]
  },
  {
    path: '/settings',
    redirect: '/settings/account',
    children: [
      {
        path: 'account',
        name: 'SettingsAccount',
        component: () => import('../views/settings/AccountSettings.vue')
      },
      {
        path: 'api',
        name: 'SettingsApi',
        component: () => import('../views/settings/ApiConfig.vue')
      },
      {
        path: 'market',
        name: 'SettingsMarket',
        component: () => import('../views/settings/MarketSettings.vue')
      },
      {
        path: 'rules',
        name: 'SettingsRules',
        component: () => import('../views/settings/TradeRules.vue')
      },
      {
        path: 'cache',
        name: 'SettingsCache',
        component: () => import('../views/settings/DataCache.vue')
      },
      {
        path: 'help',
        name: 'SettingsHelp',
        component: () => import('../views/settings/HelpCenter.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
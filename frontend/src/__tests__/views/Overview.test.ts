import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Overview from '../../views/home/Overview.vue'
import ElementPlus from 'element-plus'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/home/overview', component: Overview }
  ]
})

const pinia = createPinia()

describe('Overview Component', () => {
  test('renders welcome card with buttons', () => {
    const wrapper = mount(Overview, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查欢迎卡片是否渲染
    const welcomeCard = wrapper.find('.welcome-card')
    expect(welcomeCard.exists()).toBe(true)

    // 检查欢迎信息是否显示
    expect(welcomeCard.text()).toContain('欢迎使用 GoldQuant')
    expect(welcomeCard.text()).toContain('专业级量化投研与交易平台')

    // 检查按钮是否渲染
    const buttons = wrapper.findAll('.el-button')
    expect(buttons.length).toBe(2)
    expect(buttons[0].text()).toContain('新手引导')
    expect(buttons[1].text()).toContain('快速开始')
  })

  test('renders account info card', () => {
    const wrapper = mount(Overview, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查账户信息卡片是否渲染
    const infoCards = wrapper.findAll('.info-card')
    expect(infoCards.length).toBe(3)

    // 检查第一个卡片是否是账户信息
    const accountCard = infoCards[0]
    expect(accountCard.text()).toContain('账户信息')
    expect(accountCard.text()).toContain('总资产')
    expect(accountCard.text()).toContain('可用资金')
    expect(accountCard.text()).toContain('持仓市值')
    expect(accountCard.text()).toContain('总盈亏')
  })

  test('renders recent backtests table', () => {
    const wrapper = mount(Overview, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查最近回测卡片是否渲染
    const backtestCard = wrapper.findAll('.info-card')[1]
    expect(backtestCard.text()).toContain('最近回测')

    // 检查表格是否渲染
    const table = backtestCard.find('.el-table')
    expect(table.exists()).toBe(true)

    // 检查表格数据是否正确
    const tableRows = backtestCard.findAll('.el-table__row')
    expect(tableRows.length).toBe(3)
  })

  test('renders market overview', () => {
    const wrapper = mount(Overview, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查市场概览卡片是否渲染
    const marketCard = wrapper.findAll('.info-card')[2]
    expect(marketCard.text()).toContain('市场概览')

    // 检查市场数据是否显示
    expect(marketCard.text()).toContain('上证指数')
    expect(marketCard.text()).toContain('深证成指')
    expect(marketCard.text()).toContain('创业板指')
    expect(marketCard.text()).toContain('沪深300')
  })

  test('renders收益曲线图表', () => {
    const wrapper = mount(Overview, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查图表卡片是否渲染
    const chartCard = wrapper.find('.chart-card')
    expect(chartCard.exists()).toBe(true)
    expect(chartCard.text()).toContain('模拟账户收益曲线')

    // 检查图表容器是否渲染
    const chartContainer = wrapper.find('.chart')
    expect(chartContainer.exists()).toBe(true)
  })
})

import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Sidebar from '../../components/Sidebar.vue'
import ElementPlus from 'element-plus'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/home/overview' },
    { path: '/home/overview', component: { template: '<div>Home Overview</div>' } }
  ]
})

const pinia = createPinia()

describe('Sidebar Component', () => {
  test('renders sidebar with menu items', async () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查侧边栏是否渲染
    expect(wrapper.exists()).toBe(true)

    // 检查logo是否渲染
    expect(wrapper.find('.logo h1').text()).toBe('GoldQuant')

    // 检查菜单项是否渲染
    const menuItems = wrapper.findAll('.el-menu-item')
    expect(menuItems.length).toBeGreaterThan(0)

    // 检查首页菜单项
    const homeOverviewItem = menuItems.find(item => item.text() === '平台概览')
    expect(homeOverviewItem).toBeTruthy()
    expect(homeOverviewItem?.text()).toBe('平台概览')
  })

  test('navigates to correct route when menu item is clicked', async () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 直接测试handleMenuSelect函数
    const handleMenuSelect = wrapper.vm.handleMenuSelect
    handleMenuSelect('/home/overview')

    // 等待路由跳转完成
    await new Promise(resolve => setTimeout(resolve, 100))

    // 检查路由是否正确跳转
    expect(router.currentRoute.value.path).toBe('/home/overview')
  })

  test('updates activeMenu based on current route', async () => {
    // 导航到平台概览页面
    await router.push('/home/overview')

    const wrapper = mount(Sidebar, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查activeMenu是否正确更新
    expect(wrapper.vm.activeMenu).toBe('/home/overview')
  })
})

import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Header from '../../components/Header.vue'
import ElementPlus from 'element-plus'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/home/overview' },
    { path: '/home/overview', component: { template: '<div>Home Overview</div>' } }
  ]
})

const pinia = createPinia()

describe('Header Component', () => {
  test('renders header with breadcrumb', async () => {
    // 导航到平台概览页面
    await router.push('/home/overview')

    const wrapper = mount(Header, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查头部是否渲染
    expect(wrapper.exists()).toBe(true)

    // 检查面包屑是否渲染
    const breadcrumb = wrapper.find('.el-breadcrumb')
    expect(breadcrumb.exists()).toBe(true)

    // 检查面包屑项是否正确
    const breadcrumbItems = wrapper.findAll('.el-breadcrumb__item')
    expect(breadcrumbItems.length).toBe(3) // 首页 / 首页 / 平台概览
    expect(breadcrumbItems[0].text()).toContain('首页')
    expect(breadcrumbItems[1].text()).toContain('首页')
    expect(breadcrumbItems[2].text()).toContain('平台概览')
  })

  test('renders user info and dropdown', () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查用户信息是否渲染
    const userInfo = wrapper.find('.user-info')
    expect(userInfo.exists()).toBe(true)

    // 检查用户名是否显示
    const userName = wrapper.find('.user-name')
    expect(userName.text()).toBe('用户')

    // 检查用户头像是否渲染
    const userAvatar = wrapper.find('.el-avatar')
    expect(userAvatar.exists()).toBe(true)

    // 检查下拉菜单是否存在
    const dropdown = wrapper.find('.el-dropdown')
    expect(dropdown.exists()).toBe(true)
  })

  test('renders new button', () => {
    const wrapper = mount(Header, {
      global: {
        plugins: [router, pinia, ElementPlus]
      }
    })

    // 检查新建按钮是否渲染
    const newButton = wrapper.find('.el-button--primary')
    expect(newButton.exists()).toBe(true)
    expect(newButton.text()).toContain('新建')
  })
})

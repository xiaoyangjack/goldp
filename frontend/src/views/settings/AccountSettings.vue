<template>
  <div class="account-settings-container">
    <el-card class="settings-card">
      <template #header>
        <span>账户设置</span>
      </template>
      <div class="settings-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-form :model="basicForm" label-width="120px" style="max-width: 600px;">
              <el-form-item label="用户名">
                <el-input v-model="basicForm.username" disabled />
              </el-form-item>
              <el-form-item label="昵称">
                <el-input v-model="basicForm.nickname" placeholder="请输入昵称" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="basicForm.email" placeholder="请输入邮箱" />
              </el-form-item>
              <el-form-item label="手机号">
                <el-input v-model="basicForm.phone" placeholder="请输入手机号" />
              </el-form-item>
              <el-form-item label="头像">
                <el-upload
                  class="avatar-uploader"
                  :show-file-list="false"
                  :before-upload="beforeAvatarUpload">
                  <img v-if="basicForm.avatar" :src="basicForm.avatar" class="avatar" />
                  <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
                </el-upload>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveBasicInfo">保存修改</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="密码修改" name="password">
            <el-form :model="passwordForm" label-width="120px" style="max-width: 600px;">
              <el-form-item label="当前密码">
                <el-input v-model="passwordForm.currentPassword" type="password" placeholder="请输入当前密码" show-password />
              </el-form-item>
              <el-form-item label="新密码">
                <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
              </el-form-item>
              <el-form-item label="确认密码">
                <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="changePassword">修改密码</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="安全设置" name="security">
            <el-card class="security-item">
              <div class="security-header">
                <div class="security-info">
                  <div class="security-title">登录验证</div>
                  <div class="security-desc">开启后，每次登录都需要进行验证</div>
                </div>
                <el-switch v-model="securitySettings.loginVerify" />
              </div>
            </el-card>
            <el-card class="security-item" style="margin-top: 20px;">
              <div class="security-header">
                <div class="security-info">
                  <div class="security-title">交易密码</div>
                  <div class="security-desc">开启后，下单时需要输入交易密码</div>
                </div>
                <el-switch v-model="securitySettings.tradePassword" />
              </div>
            </el-card>
            <el-card class="security-item" style="margin-top: 20px;">
              <div class="security-header">
                <div class="security-info">
                  <div class="security-title">设备管理</div>
                  <div class="security-desc">管理已登录的设备</div>
                </div>
                <el-button type="primary" link>管理</el-button>
              </div>
            </el-card>
            <el-card class="security-item" style="margin-top: 20px;">
              <div class="security-header">
                <div class="security-info">
                  <div class="security-title">登录记录</div>
                  <div class="security-desc">查看最近登录记录</div>
                </div>
                <el-button type="primary" link>查看</el-button>
              </div>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

const basicForm = reactive({
  username: 'goldquant_user',
  nickname: '量化投资者',
  email: 'user@goldquant.com',
  phone: '138****8888',
  avatar: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const securitySettings = reactive({
  loginVerify: false,
  tradePassword: true
})

const beforeAvatarUpload = (file: File) => {
  const isJPGOrPNG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPGOrPNG) {
    ElMessage.error('头像图片只能是 JPG 或 PNG 格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过 2MB!')
    return false
  }
  return true
}

const saveBasicInfo = () => {
  ElMessage.success('基本信息保存成功')
}

const changePassword = () => {
  if (!passwordForm.currentPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!passwordForm.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  ElMessage.success('密码修改成功，请重新登录')
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}
</script>

<style scoped>
.account-settings-container {
  padding: 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.settings-content {
  padding: 10px 0;
}

.avatar-uploader {
  text-align: center;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 50%;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  cursor: pointer;
}

.avatar-uploader-icon:hover {
  border-color: #165DFF;
  color: #165DFF;
}

.security-item {
  border: 1px solid #EBEEF5;
}

.security-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.security-info {
  flex: 1;
}

.security-title {
  font-weight: 500;
  margin-bottom: 5px;
}

.security-desc {
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .account-settings-container {
    padding: 10px;
  }
}
</style>

<template>
  <div class="help-center-container">
    <el-card class="search-card">
      <el-input v-model="searchKeyword" placeholder="搜索问题或关键词..." clearable size="large">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('quickstart')">
          <div class="category-icon">
            <el-icon :size="40" color="#409EFF">
              <Guide />
            </el-icon>
          </div>
          <div class="category-name">快速入门</div>
          <div class="category-count">12 篇文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('factor')">
          <div class="category-icon">
            <el-icon :size="40" color="#67C23A">
              <DataAnalysis />
            </el-icon>
          </div>
          <div class="category-name">因子研究</div>
          <div class="category-count">25 篇文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('strategy')">
          <div class="category-icon">
            <el-icon :size="40" color="#E6A23C">
              <Setting />
            </el-icon>
          </div>
          <div class="category-name">策略开发</div>
          <div class="category-count">18 篇文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('backtest')">
          <div class="category-icon">
            <el-icon :size="40" color="#F56C6C">
              <Document />
            </el-icon>
          </div>
          <div class="category-name">回测引擎</div>
          <div class="category-count">20 篇文档</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('trading')">
          <div class="category-icon">
            <el-icon :size="40" color="#909399">
              <TrendCharts />
            </el-icon>
          </div>
          <div class="category-name">模拟交易</div>
          <div class="category-count">15 篇文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('performance')">
          <div class="category-icon">
            <el-icon :size="40" color="#409EFF">
              <DataLine />
            </el-icon>
          </div>
          <div class="category-name">绩效分析</div>
          <div class="category-count">16 篇文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('settings')">
          <div class="category-icon">
            <el-icon :size="40" color="#67C23A">
              <Tools />
            </el-icon>
          </div>
          <div class="category-name">系统设置</div>
          <div class="category-count">10 篇文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="category-card" shadow="hover" @click="handleCategory('api')">
          <div class="category-icon">
            <el-icon :size="40" color="#E6A23C">
              <Link />
            </el-icon>
          </div>
          <div class="category-name">API 文档</div>
          <div class="category-count">30 篇文档</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="faq-card">
          <template #header>
            <div class="card-header">
              <span>常见问题</span>
            </div>
          </template>
          <el-collapse v-model="activeFaq">
            <el-collapse-item title="如何创建一个新的因子？" name="1">
              <p>1. 进入因子研究模块</p>
              <p>2. 点击"自定义因子"选项卡</p>
              <p>3. 在公式编辑器中输入因子公式</p>
              <p>4. 配置因子参数和回测区间</p>
              <p>5. 点击"计算"按钮进行因子计算</p>
            </el-collapse-item>
            <el-collapse-item title="如何进行策略回测？" name="2">
              <p>1. 在策略开发模块创建或选择策略</p>
              <p>2. 配置策略参数</p>
              <p>3. 进入回测引擎模块</p>
              <p>4. 设置回测参数（起止时间、初始资金等）</p>
              <p>5. 点击"开始回测"按钮</p>
              <p>6. 查看回测报告和分析结果</p>
            </el-collapse-item>
            <el-collapse-item title="如何优化策略参数？" name="3">
              <p>1. 在回测引擎模块选择"参数优化"选项</p>
              <p>2. 选择要优化的策略和参数范围</p>
              <p>3. 配置优化算法和目标函数</p>
              <p>4. 启动参数优化任务</p>
              <p>5. 查看优化结果和参数敏感性分析</p>
            </el-collapse-item>
            <el-collapse-item title="如何配置数据源API？" name="4">
              <p>1. 进入系统设置模块</p>
              <p>2. 选择"API配置"选项</p>
              <p>3. 输入数据源API密钥和地址</p>
              <p>4. 测试API连接</p>
              <p>5. 保存配置</p>
            </el-collapse-item>
            <el-collapse-item title="如何导出绩效报告？" name="5">
              <p>1. 进入绩效分析模块</p>
              <p>2. 选择"报告导出"选项</p>
              <p>3. 配置报告类型、时间周期和格式</p>
              <p>4. 选择报告包含的内容</p>
              <p>5. 点击"生成报告"或"预览报告"</p>
              <p>6. 下载生成的报告文件</p>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="contact-card">
          <template #header>
            <span>联系支持</span>
          </template>
          <el-space direction="vertical" style="width: 100%;">
            <div class="contact-item">
              <el-icon><ChatDotRound /></el-icon>
              <span>在线客服</span>
              <el-button type="primary" size="small">立即咨询</el-button>
            </div>
            <el-divider />
            <div class="contact-item">
              <el-icon><Phone /></el-icon>
              <span>技术支持热线</span>
              <div class="contact-info">400-888-8888</div>
            </div>
            <el-divider />
            <div class="contact-item">
              <el-icon><Message /></el-icon>
              <span>邮箱</span>
              <div class="contact-info">support@goldquant.com</div>
            </div>
            <el-divider />
            <div class="contact-item">
              <el-icon><Document /></el-icon>
              <span>用户手册</span>
              <el-button type="primary" size="small" link>下载PDF</el-button>
            </div>
            <el-divider />
            <div class="contact-item">
              <el-icon><VideoPlay /></el-icon>
              <span>视频教程</span>
              <el-button type="primary" size="small" link>查看视频</el-button>
            </div>
            <el-divider />
            <div class="contact-item">
              <el-icon><Share /></el-icon>
              <span>社区论坛</span>
              <el-button type="primary" size="small" link>访问论坛</el-button>
            </div>
          </el-space>
        </el-card>

        <el-card class="update-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>版本信息</span>
              <el-tag type="success">v1.0.0</el-tag>
            </div>
          </template>
          <div class="update-content">
            <p><strong>最新更新：</strong></p>
            <ul>
              <li>新增因子筛选功能</li>
              <li>优化回测引擎性能</li>
              <li>修复若干已知问题</li>
            </ul>
            <el-button type="primary" size="small" style="margin-top: 10px;">
              <el-icon><Refresh /></el-icon>
              检查更新
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, Guide, DataAnalysis, Setting, Document, TrendCharts, DataLine, Tools, Link, ChatDotRound, Phone, Message, VideoPlay, Share, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const searchKeyword = ref('')
const activeFaq = ref(['1'])

const handleCategory = (category: string) => {
  ElMessage.info(`正在查看 ${category} 分类文档...`)
}
</script>

<style scoped>
.help-center-container {
  padding: 20px;
}

.search-card,
.faq-card,
.contact-card,
.update-card {
  margin-bottom: 20px;
}

.category-card {
  cursor: pointer;
  text-align: center;
  padding: 20px;
  transition: all 0.3s;
}

.category-card:hover {
  transform: translateY(-5px);
}

.category-icon {
  margin-bottom: 15px;
}

.category-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.category-count {
  font-size: 12px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
}

.contact-info {
  flex: 1;
  color: #606266;
}

.update-content ul {
  padding-left: 20px;
  margin: 10px 0;
}

.update-content li {
  margin: 5px 0;
  color: #606266;
}

@media (max-width: 768px) {
  .help-center-container {
    padding: 10px;
  }
}
</style>

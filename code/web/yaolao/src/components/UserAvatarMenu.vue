<template>
  <div class="user-avatar-menu">
    <el-dropdown 
      trigger="click" 
      placement="bottom-end"
      @command="handleCommand"
    >
      <div class="avatar-wrapper">
        <el-avatar 
          :size="32" 
          :src="userInfo.avatar"
          :alt="userInfo.username"
        >
          {{ userInfo.username?.charAt(0) }}
        </el-avatar>
        <span class="username">{{ userInfo.username }}</span>
        <el-icon><arrow-down /></el-icon>
      </div>

      <template #dropdown>
        <el-dropdown-menu>
          <!-- 用户信息展示 -->
          <el-dropdown-item disabled class="user-info-item">
            <div class="user-info">
              <el-avatar :size="32" :src="userInfo.avatar" />
              <div class="user-details">
                <div class="name">{{ userInfo.username }}</div>
                <div class="email">{{ userInfo.email }}</div>
              </div>
            </div>
          </el-dropdown-item>

          <el-dropdown-item divided command="profile">
            <el-icon><User /></el-icon>
            <span>个人资料</span>
          </el-dropdown-item>

          <el-dropdown-item command="userSettings">
            <el-icon><Setting /></el-icon>
            <span>用户设置</span>
          </el-dropdown-item>

          <el-dropdown-item command="systemSettings">
            <el-icon><Tools /></el-icon>
            <span>系统设置</span>
          </el-dropdown-item>

          <el-dropdown-item divided command="logout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowDown, 
  User, 
  Setting, 
  Tools, 
  SwitchButton 
} from '@element-plus/icons-vue'

const router = useRouter()

// 用户信息
const storedUserInfo = localStorage.getItem("userInfo");

const userInfo = reactive({
  id: storedUserInfo,
  username: storedUserInfo,
  email: storedUserInfo,
  avatar: storedUserInfo,
});

onMounted(() => {
  const storedUserInfo = localStorage.getItem("userInfo");
  if (storedUserInfo) {
    const parsedUserInfo = JSON.parse(storedUserInfo);
    userInfo.id = parsedUserInfo.id;
    userInfo.username = parsedUserInfo.username;
    userInfo.email = parsedUserInfo.email;
    userInfo.avatar = parsedUserInfo.avatar;
  }
});

// 菜单命令处理
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'userSettings':
      ElMessage.info('打开用户设置')
      break
    case 'systemSettings':
      ElMessage.info('打开系统设置')
      break
    case 'logout':
      await handleLogout()
      break
  }
}

// 退出登录处理
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 实际项目中调用退出登录 API
    // await logoutApi()
    
    // 跳转到登录页
    localStorage.setItem('isLoggedIn', 'false')
    router.push('/login')
    ElMessage.success('退出成功')
  } catch (error) {
    // 用户取消退出
    console.log('取消退出')
  }
}
</script>

<style scoped>
.user-avatar-menu {
  display: inline-block;
}

.avatar-wrapper {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  border-radius: 4px;
}

.avatar-wrapper:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.avatar-wrapper .username {
  margin: 0 8px;
  font-size: 14px;
  color: white;
}

.avatar-wrapper .el-icon {
  margin-left: 4px;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.user-info-item) {
  opacity: 1 !important;
  cursor: default;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 8px 0;
  min-width: 180px;
}

.user-details {
  margin-left: 12px;
}

.user-details .name {
  font-weight: 500;
  margin-bottom: 4px;
}

.user-details .email {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
}

:deep(.el-dropdown-menu__item .el-icon) {
  margin-right: 8px;
}
</style>
<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo">
          <h1>Ai聊天助手</h1>
        </div>
        <p>请登录您的账户以继续</p>
      </div>
      <div class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <div class="input-with-icon">
            <el-input
              id="username"
              class="form-custom"
              v-model="username"
              placeholder="请输入用户名"
              size="large"
              @keyup.enter="handleLogin()"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <div class="input-with-icon">
            <el-input
              id="password"
              class="form-custom"
              v-model="password"
              placeholder="请输入密码"
              size="large"
              type="password"
              @keyup.enter="handleLogin()"
              show-password
            />
          </div>
        </div>
      </div>

      <div class="form-options">
        <div class="remember-me">
          <el-checkbox v-model="rememberMe" label="记住我" size="large" />
        </div>
        <a href="#" class="forgot-password">忘记密码?</a>
      </div>
      <el-button class="login-bin" type="primary" loading-icon="Eleme" v-loading="isLoading" @click="handleLogin()">登录</el-button>

      <el-divider class="divider" content-position="center">或者</el-divider>
      <div class="other">
        <el-button class="register-bin" type="success" round>微信</el-button>
        <el-button class="register-bin" type="info" round>GitHub</el-button>
        <el-button class="register-bin" type="primary" round>QQ</el-button>
      </div>

      <div class="signup-link">
        <p>还没有账户? <a href="#">立即注册</a></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const password = ref("");
const rememberMe = ref(false);
const isLoading = ref(false);
const handleLogin = async () => {
  if (!username.value || !password.value) {
    alert("请输入用户名和密码");
    return;
  }
  isLoading.value = true;

  // 模拟登录成功
    if (username.value === 'adm' && password.value === '123') {
      // 存储登录状态
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('username', username.value)

      // 跳转到聊天界面
      router.push('/')
    } else {
      alert('用户名或密码错误')
    }
  isLoading.value = false;
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  position: relative;
  overflow: hidden;
  font-family: "Arial", sans-serif;
}
.login-box {
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 400px;
  padding: 30px;
  position: relative;
  z-index: 10;
  backdrop-filter: blur(10px);
}
.login-header {
  text-align: center;
  margin-bottom: 30px;
}
.logo {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
}
.logo h1 {
  font-size: 24px;
  color: #333;
  margin: 0;
}

.login-header p {
  color: #666;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.forgot-password {
  font-size: 14px;
  color: #4a6cf7;
  text-decoration: none;
  transition: color 0.3s;
}
.login-bin {
  width: 100%;
  padding: 17px;
  font-size: 16px;
  color: white;
  transition: background-color 0.3s;
}

:deep(.divider .el-divider__text) {
  color: #999;
  padding: 0 20px;
}
.other {
  display: flex;
  gap: 10px;
  justify-content: space-between;
}
.signup-link {
  text-align: center;
  margin-top: 20px;
}

.signup-link p {
  font-size: 14px;
  color: #666;
}

.signup-link a {
  color: #3498db;
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  transition: transform 0.3s ease;
  transform-origin: center; /* 从中心点开始缩放 */
}

.signup-link a:hover {
  transform: scale(1.2);
  color: #2980b9;
}
</style>

<!-- src/view/RegisterView.vue -->
<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <div class="logo">
          <h1>Ai聊天助手</h1>
        </div>
        <p>创建新账户以开始使用</p>
      </div>
      <div class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <div class="input-with-icon">
            <el-input
              id="username"
              class="form-custom"
              v-model="username"
              placeholder="请输入用户名"
              size="large"
              @keyup.enter="handleRegister()"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="email">邮箱</label>
          <div class="input-with-icon">
            <el-input
              id="email"
              class="form-custom"
              v-model="email"
              placeholder="请输入邮箱地址"
              size="large"
              type="email"
              @keyup.enter="handleRegister()"
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
              @keyup.enter="handleRegister()"
              show-password
            />
          </div>
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <div class="input-with-icon">
            <el-input
              id="confirmPassword"
              class="form-custom"
              v-model="confirmPassword"
              placeholder="请再次输入密码"
              size="large"
              type="password"
              @keyup.enter="handleRegister()"
              show-password
            />
          </div>
        </div>
      </div>

      <div class="form-options">
        <div class="agree-terms">
          <el-checkbox v-model="agreeTerms" size="large" />
          <span class="terms-text">我同意 <a href="#">服务条款</a> 和 <a href="#">隐私政策</a></span>
        </div>
      </div>
      
      <el-button class="register-bin" type="primary" :loading="isLoading" @click="handleRegister()">注册</el-button>

      <el-divider class="divider" content-position="center">或者</el-divider>
      <div class="other">
        <el-button class="social-bin" type="success" round>微信</el-button>
        <el-button class="social-bin" type="info" round>GitHub</el-button>
        <el-button class="social-bin" type="primary" round>QQ</el-button>
      </div>

      <div class="login-link">
        <p>已有账户? <router-link to="/login">立即登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const agreeTerms = ref(false);
const isLoading = ref(false);

const handleRegister = async () => {
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    alert("请填写所有必填项");
    return;
  }
  
  if (password.value !== confirmPassword.value) {
    alert("两次输入的密码不一致");
    return;
  }
  
  if (!agreeTerms.value) {
    alert("请同意服务条款和隐私政策");
    return;
  }
  
  isLoading.value = true;
  
  // 模拟注册过程
  setTimeout(() => {
    // 注册成功后跳转到登录页
    alert("注册成功！请登录");
    router.push('/login');
    isLoading.value = false;
  }, 1500);
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  position: relative;
  overflow: hidden;
  font-family: "Arial", sans-serif;
}

.register-box {
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 400px;
  padding: 30px;
  position: relative;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.register-header {
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

.register-header p {
  color: #666;
  margin: 0;
}

.register-form {
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
  margin-bottom: 20px;
}

.agree-terms {
  display: flex;
  align-items: center;
  gap: 8px;
}

.terms-text {
  font-size: 14px;
  color: #666;
}

.terms-text a {
  color: #4a6cf7;
  text-decoration: none;
}

.register-bin {
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

.login-link {
  text-align: center;
  margin-top: 20px;
}

.login-link p {
  font-size: 14px;
  color: #666;
}

.login-link a {
  color: #3498db;
  text-decoration: none;
  font-weight: 600;
  display: inline-block;
  transition: transform 0.3s ease;
  transform-origin: center;
}

.login-link a:hover {
  transform: scale(1.2);
  color: #2980b9;
}
</style>
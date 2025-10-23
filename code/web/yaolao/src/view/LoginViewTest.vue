<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo">
          <img src="/favicon.ico" alt="Logo" />
          <h1>AI聊天助手</h1>
        </div>
        <p>请登录您的账户以继续</p>
      </div>

      <div class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <div class="input-with-icon">
            <i class="fas fa-user"></i>
            <input 
              type="text" 
              id="username" 
              v-model="username" 
              placeholder="请输入用户名"
              @keyup.enter="handleLogin"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <div class="input-with-icon">
            <i class="fas fa-lock"></i>
            <input 
              type="password" 
              id="password" 
              v-model="password" 
              placeholder="请输入密码"
              @keyup.enter="handleLogin"
            />
            <span class="password-toggle" @click="togglePassword">
              <i :class="showPassword ? 'fas fa-eye' : 'fas fa-eye-slash'"></i>
            </span>
          </div>
        </div>

        <div class="form-options">
          <div class="remember-me">
            <input type="checkbox" id="remember" v-model="rememberMe">
            <label for="remember">记住我</label>
          </div>
          <a href="#" class="forgot-password">忘记密码?</a>
        </div>

        <button class="login-btn" @click="handleLogin" :disabled="isLoading">
          <span v-if="!isLoading">登录</span>
          <span v-else class="loading-spinner"></span>
        </button>

        <div class="divider">
          <span>或</span>
        </div>

        <div class="social-login">
          <button class="social-btn google-btn">
            <i class="fab fa-google"></i>
            <span>使用Google登录</span>
          </button>
          <button class="social-btn github-btn">
            <i class="fab fa-github"></i>
            <span>使用GitHub登录</span>
          </button>
        </div>

        <div class="signup-link">
          <p>还没有账户? <a href="#">立即注册</a></p>
        </div>
      </div>
    </div>

    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async () => {
  if (!username.value.trim() || !password.value.trim()) {
    alert('请输入用户名和密码')
    return
  }

  isLoading.value = true

  // 模拟登录请求
  setTimeout(() => {
    // 这里应该是实际的API调用
    // 示例: const response = await loginApi(username.value, password.value)

    // 模拟登录成功
    if (username.value === 'admin' && password.value === '123456') {
      // 存储登录状态
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('username', username.value)

      // 跳转到聊天界面
      router.push('/')
    } else {
      alert('用户名或密码错误')
    }

    isLoading.value = false
  }, 1500)
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
  font-family: 'Arial', sans-serif;
}

.login-box {
  background: rgba(255, 255, 255, 0.95);
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

.logo img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 10px;
}

.logo h1 {
  font-size: 24px;
  color: #333;
  margin: 0;
}

.login-header p {
  color: #666;
  font-size: 14px;
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

.input-with-icon {
  position: relative;
}

.input-with-icon i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.input-with-icon input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease;
}

.input-with-icon input:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.2);
}

.password-toggle {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
  padding: 5px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
}

.remember-me input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.remember-me label {
  font-size: 14px;
  color: #666;
  cursor: pointer;
}

.forgot-password {
  font-size: 14px;
  color: #4a6cf7;
  text-decoration: none;
  transition: color 0.3s;
}

.forgot-password:hover {
  color: #3a5ce5;
  text-decoration: underline;
}

.login-btn {
  background: #4a6cf7;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-btn:hover:not(:disabled) {
  background: #3a5ce5;
  box-shadow: 0 5px 15px rgba(74, 108, 247, 0.3);
}

.login-btn:disabled {
  background: #a0c1ff;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.divider {
  display: flex;
  align-items: center;
  margin: 15px 0;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: #ddd;
}

.divider span {
  padding: 0 15px;
  color: #999;
  font-size: 14px;
}

.social-login {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.social-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.social-btn:hover {
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.google-btn:hover {
  border-color: #db4437;
  color: #db4437;
}

.github-btn:hover {
  border-color: #333;
  color: #333;
}

.social-btn i {
  font-size: 18px;
}

.signup-link {
  text-align: center;
  margin-top: 20px;
}

.signup-link p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.signup-link a {
  color: #4a6cf7;
  text-decoration: none;
  font-weight: 600;
}

.signup-link a:hover {
  text-decoration: underline;
}

.background-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.shape-1 {
  width: 300px;
  height: 300px;
  background: white;
  top: -150px;
  right: -150px;
}

.shape-2 {
  width: 200px;
  height: 200px;
  background: white;
  bottom: -100px;
  left: -100px;
}

.shape-3 {
  width: 150px;
  height: 150px;
  background: white;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>
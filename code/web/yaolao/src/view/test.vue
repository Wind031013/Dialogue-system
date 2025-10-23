<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="header-left">
        <div class="logo">
          <img src="/favicon.ico" alt="Logo" />
          <span>AI聊天助手</span>
        </div>
      </div>
      <div class="header-right">
        <button class="settings-btn" @click="toggleSettings">
          <i class="fas fa-cog"></i>
          111
        </button>
      </div>
    </div>

    <div class="chat-messages" ref="messageContainer">
      <div v-for="(message, index) in messages" :key="index" 
           :class="['message', message.role]">
        <div class="avatar">
          <img :src="message.role === 'user' ? '/favicon.ico' : '/favicon.ico'" 
               :alt="message.role">
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ message.time }}</div>
        </div>
      </div>

      <div v-if="isLoading" class="message assistant">
        <div class="avatar">
          <img src="/favicon.ico" alt="assistant">
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-container">
      <div class="input-wrapper">
        <textarea 
          v-model="userInput" 
          @keydown.enter.prevent="handleEnterKey"
          @keydown.shift.enter.prevent="newLine"
          placeholder="输入您的消息..."
          class="chat-input"
          rows="1"
          ref="textarea"
        ></textarea>
        <div class="input-actions">
          <button class="attach-btn" @click="handleAttach">
            <i class="fas fa-paperclip"></i>
          </button>
          <button class="send-btn" @click="sendMessage" :disabled="!userInput.trim()">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 设置面板 -->
    <div v-if="showSettings" class="settings-panel">
      <div class="settings-header">
        <h3>设置</h3>
        <button class="close-btn" @click="toggleSettings">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="settings-content">
        <div class="setting-item">
          <label>模型选择</label>
          <select v-model="selectedModel">
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="gpt-4">GPT-4</option>
          </select>
        </div>
        <div class="setting-item">
          <label>温度</label>
          <input type="range" v-model="temperature" min="0" max="2" step="0.1">
          <span>{{ temperature }}</span>
        </div>
        <div class="setting-item">
          <label>最大长度</label>
          <input type="number" v-model="maxLength" min="1" max="4096">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  time: string
}

const messages = ref<Message[]>([])
const userInput = ref('')
const isLoading = ref(false)
const showSettings = ref(false)
const messageContainer = ref<HTMLElement | null>(null)
const textarea = ref<HTMLTextAreaElement | null>(null)
const selectedModel = ref('gpt-3.5-turbo')
const temperature = ref(0.7)
const maxLength = ref(2048)

// 初始化欢迎消息
onMounted(() => {
  addWelcomeMessage()
})

// 添加欢迎消息
const addWelcomeMessage = () => {
  const now = new Date()
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

  messages.value.push({
    role: 'assistant',
    content: '您好！我是您的AI助手，有什么可以帮助您的吗？',
    time: timeString
  })

  scrollToBottom()
}

// 格式化消息内容（简单处理，实际项目中可能需要更复杂的Markdown渲染）
const formatMessage = (content: string) => {
  // 简单的换行处理
  return content.replace(/\n/g, '<br>')
}

// 处理Enter键
const handleEnterKey = () => {
  if (!userInput.value.trim()) return
  sendMessage()
}

// 处理Shift+Enter换行
const newLine = () => {
  userInput.value += '\n'
  nextTick(() => {
    if (textarea.value) {
      textarea.value.value = userInput.value
      adjustTextareaHeight()
    }
  })
}

// 自动调整文本框高度
const adjustTextareaHeight = () => {
  if (textarea.value) {
    textarea.value.style.height = 'auto'
    textarea.value.style.height = Math.min(textarea.value.scrollHeight, 150) + 'px'
  }
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim()) return

  // 添加用户消息
  const now = new Date()
  const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`

  messages.value.push({
    role: 'user',
    content: userInput.value,
    time: timeString
  })

  const userMessage = userInput.value
  userInput.value = ''
  isLoading.value = true

  // 重置文本框高度
  if (textarea.value) {
    textarea.value.style.height = 'auto'
  }

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 模拟AI响应
  setTimeout(() => {
    const aiResponse = generateAIResponse(userMessage)
    messages.value.push({
      role: 'assistant',
      content: aiResponse,
      time: timeString
    })
    isLoading.value = false
    scrollToBottom()
  }, 1000)
}

// 生成AI响应（模拟）
const generateAIResponse = (userMessage: string): string => {
  // 简单模拟AI响应，实际项目中应该调用API
  const responses = [
    '我理解您的问题。这是一个很好的问题，让我来帮您解答。',
    '根据您的描述，我认为这可能是因为...',
    '我理解您的困惑，让我为您详细解释一下。',
    '这是一个有趣的话题，让我分享一些相关信息。',
    '感谢您的提问，我会尽力为您提供有用的信息。'
  ]

  // 根据用户消息的关键词生成不同的响应
  if (userMessage.includes('你好') || userMessage.includes('您好')) {
    return '您好！很高兴为您服务，请问有什么可以帮助您的吗？'
  } else if (userMessage.includes('谢谢')) {
    return '不客气！如果您还有其他问题，随时可以问我。'
  } else {
    return responses[Math.floor(Math.random() * responses.length)]
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

// 切换设置面板
const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

// 处理附件上传
const handleAttach = () => {
  // 实际项目中应该实现文件上传功能
  alert('附件上传功能待实现')
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
  font-family: 'Arial', sans-serif;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #4a6cf7;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.2rem;
  font-weight: bold;
}

.logo img {
  width: 30px;
  height: 30px;
  margin-right: 10px;
  border-radius: 50%;
}

.header-right {
  display: flex;
  align-items: center;
}

.settings-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.settings-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  display: flex;
  gap: 10px;
  max-width: 80%;
  animation: fadeIn 0.3s ease-in-out;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.assistant {
  align-self: flex-start;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.message-text {
  padding: 12px 15px;
  border-radius: 18px;
  background-color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
}

.message.user .message-text {
  background-color: #4a6cf7;
  color: white;
}

.message-time {
  font-size: 0.75rem;
  color: #999;
  align-self: flex-end;
}

.typing-indicator {
  display: flex;
  padding: 12px 15px;
  background-color: white;
  border-radius: 18px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  display: inline-block;
  margin: 0 2px;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

.chat-input-container {
  padding: 15px;
  background-color: white;
  border-top: 1px solid #eee;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.chat-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 12px 15px;
  resize: none;
  font-size: 1rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.3s;
}

.chat-input:focus {
  border-color: #4a6cf7;
}

.input-actions {
  display: flex;
  gap: 5px;
}

.attach-btn, .send-btn {
  background: none;
  border: none;
  color: #4a6cf7;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.3s;
}

.send-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.attach-btn:hover, .send-btn:hover:not(:disabled) {
  background-color: rgba(74, 108, 247, 0.1);
}

.settings-panel {
  position: fixed;
  right: 0;
  top: 0;
  height: 100%;
  width: 300px;
  background-color: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
  transform: translateX(0);
  transition: transform 0.3s ease-in-out;
}

.settings-panel.hidden {
  transform: translateX(100%);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.settings-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  color: #666;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
}

.settings-content {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item label {
  font-weight: bold;
  color: #555;
}

.setting-item select,
.setting-item input[type="number"] {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.setting-item input[type="range"] {
  width: 100%;
}

.setting-item span {
  align-self: flex-end;
  color: #666;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
  100% {
    transform: translateY(0);
  }
}
</style>
<template>
  <div class="chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-content">
        <div class="logo">
          <div class="logo-icon">
            <img src="/favicon.ico" alt="Logo" />
          </div>
          <div class="logo-text">
            <h2>角色扮演AI聊天室</h2>
            <p class="status">
              <span class="status-dot"></span>
              <span>药老在线</span>
            </p>
          </div>
        </div>
        <div class="header-actions">
          <el-button 
            class="clear-btn" 
            text 
            @click="handleClearChat"
            :disabled="messages.length === 0"
          >
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
          <el-button 
            class="setting-btn" 
            text 
            @click="settingDrawer = true"
          >
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 欢迎消息 -->
      <div v-if="messages.length === 0" class="welcome-message">
        <div class="welcome-avatar">
          <img src="/favicon.ico" alt="Assistant" />
        </div>
        <div class="welcome-content">
          <h3>欢迎来到角色扮演AI聊天室！</h3>
          <p>我是药老，有什么问题尽管问我吧～</p>
          <div class="suggestions">
            <el-tag 
              v-for="(suggestion, index) in quickSuggestions" 
              :key="index"
              class="suggestion-tag"
              @click="handleSuggestionClick(suggestion)"
            >
              {{ suggestion }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role]"
      >
        <div class="avatar">
          <img
            :src="message.role === 'user' ? '/user-avatar.png' : '/favicon.ico'"
            :alt="message.role"
          />
        </div>
        <div class="message-content">
          <div class="message-header">
            <span class="sender-name">{{ message.role === 'user' ? '你' : '药老' }}</span>
            <span class="message-time">{{ message.time }}</span>
          </div>
          <div class="message-bubble">
            <div
              class="message-text"
              v-html="formatMessage(message.content)"
            ></div>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="message assistant">
        <div class="avatar">
          <img src="/favicon.ico" alt="Assistant" />
        </div>
        <div class="message-content">
          <div class="message-header">
            <span class="sender-name">药老</span>
          </div>
          <div class="message-bubble">
            <div class="message-text loading">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              正在思考中...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-container">
      <div class="input-wrapper">
        <el-input
          type="textarea"
          placeholder="输入您的消息..."
          :autosize="{ minRows: 1, maxRows: 4 }"
          resize="none"
          v-model="inputMessage"
          @keyup.enter.exact="handleSendMessage"
          class="message-input"
          maxlength="1000"
          show-word-limit
        >
        </el-input>
        <div class="input-actions">
          <el-button
            class="send-btn"
            type="primary"
            @click="handleSendMessage"
            :disabled="loading || inputMessage.trim() === ''"
            :loading="loading"
          >
            <template #loading>
              <span class="loading-text">发送中</span>
            </template>
            <template #default>
              <span class="send-text">发送</span>
              <el-icon class="send-icon"><Promotion /></el-icon>
            </template>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 设置抽屉 -->
    <el-drawer v-model="settingDrawer" title="设置" direction="rtl" size="350px">
      <template #header>
        <h3>聊天设置</h3>
      </template>
      <div class="settings-content">
        <div class="setting-item">
          <h4>角色选择</h4>
          <el-select v-model="selectedRole" placeholder="选择角色">
            <el-option label="药老" value="yaolao" />
            <el-option label="其他角色" value="other" />
          </el-select>
        </div>
        <div class="setting-item">
          <h4>对话风格</h4>
          <el-select v-model="chatStyle" placeholder="选择风格">
            <el-option label="正式" value="formal" />
            <el-option label="轻松" value="casual" />
            <el-option label="幽默" value="humorous" />
          </el-select>
        </div>
        <div class="setting-item">
          <h4>其他设置</h4>
          <el-switch v-model="autoScroll" active-text="自动滚动" />
          <el-switch v-model="soundEnabled" active-text="提示音" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { Setting, Delete, Promotion } from "@element-plus/icons-vue";
import { nextTick, ref, onMounted, watch } from "vue";

interface Message {
  role: "user" | "assistant";
  content: string;
  time: string;
}

// 响应式数据
const messages = ref<Message[]>([]);
const inputMessage = ref<string>("");
const messagesContainer = ref<HTMLElement | null>(null);
const loading = ref<boolean>(false);
const settingDrawer = ref<boolean>(false);
const selectedRole = ref<string>("yaolao");
const chatStyle = ref<string>("casual");
const autoScroll = ref<boolean>(true);
const soundEnabled = ref<boolean>(true);

// 快速建议
const quickSuggestions = ref([
  "介绍一下你自己",
  "你有什么能力？",
  "如何提升修为？",
  "炼丹有什么技巧？"
]);

// 滚动到底部
const scrollToBottom = () => {
  if (!autoScroll.value) return;
  
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 初始化示例消息
onMounted(() => {
  // 可以在这里加载历史消息
});

// 格式化消息内容
const formatMessage = (content: string) => {
  return content.replace(/\n/g, "<br>");
};

// 处理发送消息
const handleSendMessage = () => {
  if (inputMessage.value.trim() === "" || loading.value) return;
  
  const newMessage: Message = {
    role: "user",
    content: inputMessage.value,
    time: new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
  };

  messages.value.push(newMessage);
  inputMessage.value = "";
  loading.value = true;

  scrollToBottom();

  // 模拟助手回复
  setTimeout(() => {
    const assistantReply: Message = {
      role: "assistant",
      content: generateReply(newMessage.content),
      time: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    messages.value.push(assistantReply);
    loading.value = false;
    scrollToBottom();
  }, 2000 + Math.random() * 2000); // 随机延迟2-4秒，更真实
};

// 生成回复内容
const generateReply = (userMessage: string) => {
  // 这里可以根据用户消息生成不同的回复
  const replies = [
    `关于"${userMessage}"，老夫认为这其中大有玄机。`,
    `小友问得好！"${userMessage}"这个问题确实值得深思。`,
    `哈哈，你问到点子上了。"${userMessage}"这个问题老夫可以给你详细说说。`,
    `"${userMessage}"？这倒是让老夫想起了当年的一段往事...`
  ];
  
  return replies[Math.floor(Math.random() * replies.length)];
};

// 处理清空对话
const handleClearChat = () => {
  messages.value = [];
};

// 处理快速建议点击
const handleSuggestionClick = (suggestion: string) => {
  inputMessage.value = suggestion;
  // 自动聚焦到输入框
  nextTick(() => {
    const textarea = document.querySelector('.message-input textarea') as HTMLTextAreaElement;
    if (textarea) {
      textarea.focus();
    }
  });
};
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Helvetica Neue', Arial, sans-serif;
}

/* 头部样式 */
.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo-icon img {
  width: 70%;
  height: 70%;
  object-fit: contain;
}

.logo-text h2 {
  margin: 0;
  color: white;
  font-size: 1.4rem;
  font-weight: 600;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #4ade80;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.header-actions {
  display: flex;
  gap: 10px;
}

.clear-btn, .setting-btn {
  color: white;
  border: none;
}

.clear-btn:hover, .setting-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* 消息区域样式 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  scroll-behavior: smooth;
}

/* 欢迎消息样式 */
.welcome-message {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 10px;
  animation: fadeIn 0.6s ease-out;
}

.welcome-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.welcome-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.welcome-content h3 {
  margin: 0 0 8px;
  color: #333;
}

.welcome-content p {
  margin: 0 0 15px;
  color: #666;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* 消息样式 */
.message {
  display: flex;
  animation: fadeInUp 0.4s ease-out;
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
  margin: 0 12px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}

.sender-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.message-time {
  font-size: 0.75rem;
  color: #999;
}

.message-bubble {
  border-radius: 18px;
  padding: 12px 16px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  position: relative;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 6px;
}

.message.assistant .message-bubble {
  background: white;
  color: #333;
  border-bottom-left-radius: 6px;
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
}

.message-text.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-style: italic;
}

.typing-indicator {
  display: flex;
  gap: 3px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  border-radius: 50%;
  background-color: #999;
  display: inline-block;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 输入区域样式 */
.chat-input-container {
  padding: 15px 20px;
  background-color: white;
  border-top: 1px solid #eaeaea;
  position: relative;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-input {
  border-radius: 12px;
  overflow: hidden;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
  transition: all 0.2s;
}

.message-input :deep(.el-textarea__inner:focus) {
  border-color: #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.send-btn {
  border-radius: 20px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: all 0.2s;
}

.send-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  transform: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  opacity: 0.6;
}

.send-text {
  margin-right: 5px;
}

.send-icon {
  font-size: 0.9rem;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 设置抽屉样式 */
.settings-content {
  padding: 0 20px;
}

.setting-item {
  margin-bottom: 25px;
}

.setting-item h4 {
  margin: 0 0 12px;
  color: #333;
  font-size: 1rem;
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 0 15px;
  }
  
  .logo-text h2 {
    font-size: 1.2rem;
  }
  
  .chat-messages {
    padding: 15px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-input-container {
    padding: 12px 15px;
  }
}
</style>
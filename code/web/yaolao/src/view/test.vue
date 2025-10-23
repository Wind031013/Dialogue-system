<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="header-left">
        <div class="logo">
          <img src="/favicon.ico" alt="Logo" />
          <span>角色扮演AI聊天室</span>
        </div>
      </div>

      <div class="header-right">
        <Setting class="setting-icon" @click="showSettings = true" />
      </div>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.role]"
      >
        <div class="avatar">
          <img
            :src="message.role === 'user' ? '/favicon.ico' : '/favicon.ico'"
            :alt="message.role"
          />
        </div>

        <div class="message-content">
          <div class="message-text-content">
            <div
              class="message-text"
              v-html="formatMessage(message.content)"
            ></div>
          </div>
          <div class="message-time">{{ message.time }}</div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="message assistant">
        <div class="avatar">
          <img src="/favicon.ico" alt="assistant" />
        </div>
        <div class="message-content">
          <div class="message-text-content">
            <div class="message-text loading">
              药老正在思考...
              <span class="loading-dots">
                <span>.</span><span>.</span><span>.</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-container">
      <div class="input-wrapper">
        <el-input
          type="textarea"
          placeholder="输入您的消息..."
          :autosize="{ minRows: 4, maxRows: 6 }"
          resize="none"
          v-model="inputMessage"
          @keyup.enter="handleSendMessage"
          :disabled="loading"
        >
        </el-input>
        <div class="send-button-wrapper">
          <el-button
            class="send-btn"
            type="primary"
            @click="handleSendMessage"
            :disabled="loading || !inputMessage.trim()"
            :loading="loading"
          >
            {{ loading ? "发送中..." : "发送" }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="设置" width="400px">
      <div class="settings-content">
        <el-form label-width="80px">
          <el-form-item label="API地址">
            <el-input v-model="apiBase" placeholder="http://localhost:8000" />
          </el-form-item>
          <el-form-item label="最大长度">
            <el-input-number v-model="maxTokens" :min="100" :max="1000" />
          </el-form-item>
          <el-form-item label="温度">
            <el-slider
              v-model="temperature"
              :min="0.1"
              :max="1.0"
              :step="0.1"
            />
          </el-form-item>
        </el-form>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Setting } from "@element-plus/icons-vue";
import { ref, reactive, nextTick } from "vue";
import { ElMessage } from "element-plus";

interface Message {
  role: "user" | "assistant";
  content: string;
  time: string;
}

// 响应式数据
const messages = ref<Message[]>([]);
const inputMessage = ref<string>("");
const loading = ref<boolean>(false);
const messagesContainer = ref<HTMLElement | null>(null);
const showSettings = ref<boolean>(false);

// API配置
const apiBase = ref<string>("http://localhost:8000");
const maxTokens = ref<number>(512);
const temperature = ref<number>(0.7);

// 工具函数
const getCurrentTime = (): string => {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
};

// 初始化欢迎消息
messages.value = [
  {
    role: "assistant",
    content: "你好！我是药老，有什么可以帮助你的吗？",
    time: getCurrentTime(),
  },
];

const formatMessage = (content: string): string => {
  return content.replace(/\n/g, "<br>");
};

const scrollToBottom = (): void => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 发送消息函数
const handleSendMessage = async (): Promise<void> => {
  if (inputMessage.value.trim() === "" || loading.value) return;

  const userMessage: Message = {
    role: "user",
    content: inputMessage.value.trim(),
    time: getCurrentTime(),
  };

  // 添加用户消息
  messages.value.push(userMessage);
  inputMessage.value = "";
  loading.value = true;

  scrollToBottom();

  try {
    const response = await fetch(`${apiBase.value}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages: messages.value.map((msg) => ({
          role: msg.role,
          content: msg.content,
          time: msg.time,
        })),
        max_tokens: maxTokens.value,
        temperature: temperature.value,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`
      );
    }

    const data = await response.json();

    // 添加助手回复
    messages.value.push({
      role: "assistant",
      content: data.content,
      time: data.time,
    });
  } catch (error) {
    console.error("请求错误:", error);
    ElMessage.error("发送失败，请检查网络连接或API服务状态");

    // 添加错误回复
    messages.value.push({
      role: "assistant",
      content: "抱歉，我暂时无法回复，请稍后再试。",
      time: getCurrentTime(),
    });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

// 监听Enter键（不带Shift）
const handleKeyUp = (event: KeyboardEvent) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    handleSendMessage();
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  flex-direction: column;
  background-color: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #4a6cf7;
  border-radius: 8px;
  padding: 10px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
}

.logo img {
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.logo span {
  color: white;
  font-weight: bold;
}

.setting-icon {
  color: white;
  width: 1.5rem;
  cursor: pointer;
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
  animation: fadeIn 0.6s ease-out;
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
  margin: 0 10px;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 80rem;
}

.message.user .message-content {
  align-items: flex-end;
}

.message.assistant .message-content {
  align-items: flex-start;
}

.message-text {
  background-color: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
}

.message.user .message-text {
  background-color: #4a6cf7;
  color: white;
}

.message-time {
  margin-top: 5px;
  font-size: 0.8rem;
  color: #999;
}

.chat-input-container {
  padding: 15px;
  background-color: white;
  border-top: 1px solid #eee;
  position: relative;
}

.input-wrapper {
  display: flex;
  margin-bottom: 10px;
}

.send-button-wrapper {
  position: absolute;
  bottom: 30px;
  right: 20px;
  z-index: 10;
}

.loading {
  color: #666;
  font-style: italic;
}

.loading-dots span {
  animation: blink 1.4s infinite both;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0% {
    opacity: 0.2;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0.2;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-content {
  padding: 10px 0;
}
</style>

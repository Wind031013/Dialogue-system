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
        <UserAvatarMenu />
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
        <!-- 消息内容 -->
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
          <img src="/favicon.ico" alt="Assistant" />
        </div>
        <div>
          <div class="message-content">
            <div class="message-text-content">
              <div class="message-text loading">
                药老正在思考...<br />
                <span class="loading-dots">
                  <span>.</span><span>.</span><span>.</span>
                </span>
              </div>
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
          :autosize="{ minRows: 4, maxRows: 6 }"
          resize="none"
          v-model="inputMessage"
          @keyup.enter="handleSendMessage()"
        >
        </el-input>
        <div class="send-button-wrapper">
          <el-button
            class="send-btn"
            type="primary"
            @click="handleSendMessage()"
            :disabled="loading"
          >
            {{ loading ? "发送中" : "发送" }}
            <span v-if="loading" class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </el-button>
        </div>
      </div>
    </div>
    <!-- 设置 -->
    <el-drawer v-model="settingDrawer" title="设置" :with-header="false">
      <span>Hi there!</span>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from "vue";
import { ElMessage } from "element-plus";
import UserAvatarMenu from "@/components/UserAvatarMenu.vue";
interface Message {
  role: "user" | "assistant";
  content: string;
  time: string;
}

const messages = ref<Message[]>([]);
const inputMessage = ref<string>("");
const messagesContainer = ref<HTMLElement | null>(null);
const loading = ref<boolean>(false);
const disableSend = ref<boolean>(false);
const settingDrawer = ref<boolean>(false);

//API 配置
const apiUrl = import.meta.env.VITE_API_URL;
const repetition_penalty = ref<number>(1.1);
const temperature = ref<number>(0.7);
const max_tokens = ref<number>(512);

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

messages.value = [];
const formatMessage = (content: string) => {
  let filteredContent = content.replace(/<think>.*?<\/think>/gs, "");
  // 移除单独的think标签（防止格式不完整）
  filteredContent = filteredContent.replace(/<\/?think>/g, "");
  // 清理多余的空白行
  filteredContent = filteredContent.replace(/^\s*[\r\n]/gm, "").trim();
  // 处理换行符
  return filteredContent.replace(/\n/g, "<br>");
};

const handleSendMessage = async () => {
  if (inputMessage.value.trim() === "") return;
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

  try {
    const requestData = {
      messages: messages.value.map((msg) => ({
        role: msg.role,
        content: msg.content,
      })),
      repetition_penalty: repetition_penalty.value,
      temperature: temperature.value,
      max_tokens: max_tokens.value,
    };
    const response = await fetch(`${apiUrl}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });
    const responseData = await response.json();
    if (!response.ok) {
      // 使用已保存的数据
      const errorData = responseData;
      ElMessage.error(errorData.message || "请求失败");
      return;
    }
    const data = responseData;

    const assistantReply: Message = {
      role: "assistant",
      content: data.content,
      time: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    messages.value.push(assistantReply);
  } catch (error) {
    console.error("发送消息失败:", error);
    ElMessage.error("发送失败，请检查网络连接或API服务状态");
  } finally {
    loading.value = false;
    scrollToBottom();
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
.avatar-wrapper {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.3s;
  border-radius: 4px;
}

.avatar-wrapper:hover {
  background-color: var(--el-color-primary-light-9);
}

.avatar-wrapper .username {
  margin: 0 8px;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.avatar-wrapper .el-icon {
  margin-left: 4px;
  color: var(--el-text-color-placeholder);
}
.setting-icon {
  color: white;
  width: 1.5rem;
  cursor: pointer;
}

.setting-icon:hover {
  color: #409eff;
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
  padding: 10px 16px;
  border-radius: 12px;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
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
</style>

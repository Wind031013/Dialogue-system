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
        <Setting class="setting-icon" />
      </div>
    </div>

    <div class="chat-messages">
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
          <div
            class="message-text"
            v-html="formatMessage(message.content)"
          ></div>
          <div class="message-time">{{ message.time }}</div>
        </div>
      </div>

      <div class="chat-input">

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Setting } from "@element-plus/icons-vue";
import { ref } from "vue";

interface Message {
  role: "user" | "assistant";
  content: string;
  time: string;
}

const messages = ref<Message[]>([]);
messages.value = [
  { role: "user", content: "你好", time: "10:00 AM" },
  {
    role: "assistant",
    content: "你好！有什么我可以帮您的吗？",
    time: "10:01 AM",
  },
];

const formatMessage = (content: string) => {
  return content.replace(/\n/g, "<br>");
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
}
.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.message-content {
  display: flex;
  flex-direction: column;
}
.message-text {
  background-color: white;
  padding: 10px 15px;
  border-radius: 12px;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
}
.message-time {
  margin-top: 5px;
  font-size: 0.8rem;
  color: #999;
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

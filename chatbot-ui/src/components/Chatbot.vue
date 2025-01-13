<template>
    <div class="chatbot-container">
        <div class="chat-window">
            <!-- Loading Spinner -->
            <div v-if="isLoading" class="loading-spinner">
                Loading...
            </div>

            <div v-for="(message, index) in messages" :key="index" :class="['message-container', message.sender]">
                <img :src="message.sender === 'bot' ? botIcon : userIcon" alt="User Icon" class="user-icon" />
                <div class="message">
                    <p>{{ message.text }}</p>
                </div>
            </div>
        </div>
        <div class="input-container">
            <input v-model="userInput" @keydown.enter="sendMessage" placeholder="Type a message..." />
            <button @click="sendMessage">Send</button>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import botIcon from "../assets/fmi.png";
import userIcon from "../assets/user.png";
import { sendMessageToApi } from "../service/chatService";

interface Message {
    sender: "user" | "bot";
    text: string;
}

export default defineComponent({
    name: "Chatbot",
    setup() {
        const userInput = ref<string>("");
        const messages = ref<Message[]>([
            { sender: "bot", text: "Hello! How can I help you today?" },
        ]);

        const isLoading = ref<boolean>(false);

        const sendMessage = async () => {
            const trimmedInput = userInput.value.trim();
            if (!trimmedInput) return;

            // Add user message
            messages.value.push({ sender: "user", text: trimmedInput });
            userInput.value = "";

            isLoading.value = true;

            // Fetch bot response from API and display msg
            const botResponse = await sendMessageToApi(trimmedInput);
            messages.value.push({ sender: "bot", text: botResponse });

            // Hide loading indicator
            isLoading.value = false;
        };

        return {
            userInput,
            messages,
            sendMessage,
            botIcon,
            userIcon,
        };
    },
});
</script>

<style scoped>
.chatbot-container {
    display: flex;
    flex-direction: column;
    height: 70vh;
    width: 400px;
    margin: 0 auto;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    font-family: Arial, sans-serif;
}

.chat-window {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    background: #f9f9f9;
}

.loading-spinner {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 16px;
    font-weight: bold;
    color: #555;
}

.message-container {
    display: flex;
    align-items: flex-start;
    margin-bottom: 12px;
}

.message-container.user {
    flex-direction: row-reverse;
}

.user-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin: 0 8px;
}

.message {
    background: #d1e7dd;
    padding: 10px;
    border-radius: 8px;
    max-width: 70%;
    word-wrap: break-word;
}

.message-container.user .message {
    background: #d1e7dd;
}

.message-container.bot .message {
    background: #f8d7da;
}

.input-container {
    display: flex;
    padding: 8px;
    background: #fff;
    border-top: 1px solid #ddd;
}

input {
    flex: 1;
    padding: 8px;
    font-size: 14px;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-right: 8px;
}

button {
    padding: 8px 16px;
    font-size: 14px;
    border: none;
    background: #007bff;
    color: #fff;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background: #0056b3;
}
</style>
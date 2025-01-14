<template>
    <div :class="['phone', { 'dark-mode': isDarkMode }]">
        <div class="screen">
            <div class="top-bar">
                <div class="top-left">
                    <span class="battery">100%</span>
                </div>
                <div class="top-center">
                    <span class="time">12:45</span>
                </div>
                <div class="top-right">
                    <span class="signal">5G</span>
                </div>
            </div>
            <div class="content">
                <div class="chatbot-container">
                    <!-- Chatbar title with FMI and moon/sun icons -->
                    <div class="chatbar-title">
                        <span class="chat-title">Chat with FMI</span>
                                <!-- Dark Mode Toggler -->
                        <button @click="toggleDarkMode" class="dark-mode-toggler">
                            <img :src="isDarkMode ? sunIcon : moonIcon" alt="Mode Icon" class="mode-icon" />
                        </button>
                    </div>

                    <div class="chat-window">
                        <!-- Loading Spinner -->
                        <div v-if="isLoading" class="loading-spinner">
                            Loading...
                        </div>

                        <!-- Chat messages -->
                        <div
                            v-for="(message, index) in messages"
                            :key="index"
                            :class="['message-container', message.sender]"
                        >
                            <img
                                :src="message.sender === 'bot' ? botIcon : userIcon"
                                alt="User Icon"
                                class="user-icon"
                            />
                            <div class="message" v-html="message.text"></div>
                        </div>
                    </div>
                    <!-- Input container -->
                    <div class="input-container">
                        <input v-model="userInput" @keydown.enter="sendMessage" placeholder="Type a message..." />
                        <button @click="sendMessage">Send</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Home Button -->
        <div class="home-button"></div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import botIcon from "../assets/fmi.png";
import userIcon from "../assets/user.png";
import moonIcon from "../assets/moon.png";
import sunIcon from "../assets/sun.png";
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
        const isDarkMode = ref<boolean>(false);

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

        const toggleDarkMode = () => {
            isDarkMode.value = !isDarkMode.value;
        };

        return {
            userInput,
            messages,
            sendMessage,
            botIcon,
            userIcon,
            isDarkMode,
            toggleDarkMode,
            moonIcon,
            sunIcon,
        };
    },
});
</script>
<style scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-family: Arial, sans-serif;
}

/* Dark Mode Styles */
.dark-mode {
    background-color: #181818;
    color: #e0e0e0;
}

.dark-mode.phone {
    background-color: #121212; /* Dark background for the phone */
}

.dark-mode .screen {
    background-color: #262626;
}

.dark-mode .top-bar {
    background-color: #333;
    color: #fff;
}

.dark-mode .message-container.bot .message {
    background-color: lightgray;
}

.dark-mode .message-container.user .message {
    background-color: #0a84ff;
    color: white;
}

.dark-mode .input-container input {
    background: grey;
    color: white;
    border: 1px solid #555;
}

.dark-mode .input-container button {
    background-color: #0a84ff;
    border: none;
}

.dark-mode .loading-spinner {
    color: #0a84ff;
}

.dark-mode .chatbar-title {
    background-color: #2a2a2a;
    color: #fff;
}

.dark-mode .chatbar-title .mode-icon {
    filter: invert(1);
}

.dark-mode .user-icon {
    background: white;
}

/* Phone container */
.phone {
    width: 350px;
    height: 700px;
    background-color: #f5f5f5;
    border-radius: 40px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

/* Phone screen */
.screen {
    width: 100%;
    height: 92%;
    background-color: #ffffff;
    padding: 10px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    border-radius: 30px;
    position: relative;
}

/* Top Bar (simulating phone status bar) */
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 20px;
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    background-color: #f2f2f2;
    border-radius: 15px;
    font-size: 12px;
    color: #333;
}

.top-left, .top-right, .top-center {
    display: flex;
    align-items: center;
}

/* Left side (Battery & Wi-Fi) */
.top-left {
    display: flex;
    gap: 5px;
}

.battery {
    font-weight: bold;
}

.wifi {
    font-weight: bold;
}

/* Center section (Time) */
.top-center {
    font-weight: bold;
}

/* Right side (Signal) */
.top-right {
    font-weight: bold;
}

/* Chatbot container */
.chatbot-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

/* Chatbar Title */
.chatbar-title {
    display: flex;
    gap: 10px;
    padding: 10px;
    position: absolute;
    top: 25px;
    left: 0;
    width: 100%;
    border-bottom: 1px solid #ddd;
    background-color: #f5f5f5;
    font-weight: bold;
    align-items: center;
    color: #333;
}

.chatbar-title .mode-icon {
    width: 20px;
    height: 20px;
}

/* Chat window */
.chat-window {
    overflow-y: auto;
    max-height: 510px;
    margin-bottom: 10px;
    display: flex;
    flex-direction: column;
    padding-right: 10px;
}

/* Message container for bot and user */
.message-container {
    display: flex;
    align-items: flex-start;
    margin: 10px 0;
}

.message-container.bot {
    justify-content: flex-start;
}

.message-container.user {
    justify-content: flex-end;
}

.user-icon {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    margin-right: 10px;
}

.message-container .message {
    max-width: 80%;
    padding: 10px;
    border-radius: 20px;
    background-color: #f0f0f0;
    font-size: 16px;
}

/* Different colors for user and bot messages */
.message-container.bot .message {
    background-color: lightgray;
    color: black;
}

.message-container.user .message {
    background-color: #0a84ff;
    color: white;

}

/* Loading spinner */
.loading-spinner {
    color: #0a84ff;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
}

/* Input container */
.input-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}

.input-container input {
    width: 80%;
    padding: 10px;
    border-radius: 25px;
    border: 1px solid #ccc;
    font-size: 14px;
    outline: none;
    background: lightgray;
    color: black;
}

.input-container input:focus {
    border-color: #0a84ff;
}

.input-container button {
    padding: 10px 15px;
    background-color: #0a84ff;
    color: white;
    border: none;
    border-radius: 25px;
    font-size: 14px;
    cursor: pointer;
}

.input-container button:hover {
    background-color: #0073e6;
}

/* Dark Mode Toggler */
.dark-mode-toggler {
    background: none;
    float: right;
    border: none;
    cursor: pointer;
    padding: 10px;
    right: -5px;
    position: absolute;
}

.mode-icon {
    width: 30px;
    height: 30px;
}

/* Home button */
.home-button {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 10px;
    background-color: #ccc;
    border-radius: 20px;
}
</style>

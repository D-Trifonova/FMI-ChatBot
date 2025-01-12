<template>
  <Chatbot />
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Chatbot from "./components/Chatbot.vue";

export default defineComponent({
  name: "App",
  components: {
    Chatbot,
  },
});
</script>

<script setup lang="ts">
import { RouterView } from "vue-router";
import { useAlertStore } from "@/stores";

import MainNavbar from "@/components/MainNavbar.vue";
import AlertToast from "@/components/AlertToast.vue";
import ProgressBar from "./components/ProgressBar.vue";

const alertStore = useAlertStore();
</script>

<template>
  <!-- Progress bar -->
  <ProgressBar />

  <!-- Navbar -->
  <MainNavbar />

  <!-- Main content -->
  <main>
    <RouterView />
  </main>

  <!-- Alert system -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <AlertToast
      v-for="q in alertStore.queue"
      :id="q.id"
      :key="q.id"
      :type="q.type"
      :message="q.message"
    />
  </div>
</template>

<style>
body,
#app {
  min-height: 100vh;
}
</style>

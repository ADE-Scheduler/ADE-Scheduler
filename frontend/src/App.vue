<script setup lang="ts">
import { useDark } from "@vueuse/core";
import { RouterView } from "vue-router";
import { useAlertStore } from "@/stores";

import MainNavbar from "@/components/MainNavbar.vue";
import AlertToast from "@/components/AlertToast.vue";
import ProgressBar from "@/components/ProgressBar.vue";

const alertStore = useAlertStore();

// initialize the dark mode selection accross the whole app
useDark({
  selector: "html",
  attribute: "data-bs-theme",
  storageKey: "ade-scheduler-theme",
});
</script>

<template>
  <!-- Progress bar -->
  <ProgressBar />

  <!-- Navbar -->
  <MainNavbar />

  <!-- Main content -->
  <main class="container-fluid">
    <RouterView v-slot="{ Component }">
      <KeepAlive>
        <Component :is="Component" />
      </KeepAlive>
    </RouterView>
  </main>

  <!-- Alert system -->
  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <AlertToast
      v-for="{ id, type, message } in alertStore.queue"
      :id="id"
      :key="id"
      :type="type"
      :message="message"
    />
  </div>
</template>

<style>
body,
#app {
  min-height: 100vh;
}
</style>

<script setup lang="ts">
import { RouterView } from "vue-router";
import { useAlertStore } from "@/stores/alert";

import MainNavbar from "@/components/MainNavbar.vue";
import AlertToast from "@/components/AlertToast.vue";

const alertStore = useAlertStore();
</script>

<template>
  <div>
    <!-- Navbar -->
    <MainNavbar />

    <!-- Main content -->
    <RouterView />

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
  </div>
</template>

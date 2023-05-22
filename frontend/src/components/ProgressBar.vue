<script setup lang="ts">
import { progress, isLoading } from "@/api";
</script>

<template>
  <Transition
    name="fade"
    role="progressbar"
    class="progress position-fixed fixed-top"
    style="height: 2px"
    data-bs-theme="dark"
    v-show="isLoading"
    :style="{ width: ((progress as number) * 100).toFixed(0) + '%' }"
  >
    <div class="progress-bar" />
  </Transition>
</template>

<style scoped>
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

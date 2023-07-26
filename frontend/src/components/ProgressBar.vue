<script setup lang="ts">
import { progress, isLoading } from "@/api";
</script>

<template>
  <Transition name="fade">
    <div
      v-show="isLoading"
      role="progressbar"
      style="height: 2px"
      class="progress position-fixed fixed-top bg-body-tertiary"
      data-bs-theme="dark"
    >
      <div
        class="progress-bar"
        :style="{ width: ((progress as number) * 100).toFixed(0) + '%' }"
      />
    </div>
  </Transition>
</template>

<style scoped>
.fade-leave-active {
  transition: opacity 1s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

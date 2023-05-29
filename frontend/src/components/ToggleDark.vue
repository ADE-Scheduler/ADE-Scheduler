<script setup lang="ts">
import { UseDark } from "@vueuse/components";
</script>

<template>
  <UseDark
    v-slot="{ isDark, toggleDark }"
    selector="html"
    attribute="data-bs-theme"
    storage-key="ade-scheduler-theme"
  >
    <button
      role="button"
      class="btn btn-link link-body-emphasis"
      @click="toggleDark()"
    >
      <Transition name="fade" mode="out-in">
        <i v-if="isDark" class="bi bi-moon-stars" />
        <i v-else class="bi bi-sun" />
      </Transition>
    </button>
  </UseDark>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.1s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

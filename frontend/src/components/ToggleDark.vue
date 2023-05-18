<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { UseDark } from "@vueuse/components";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});
</script>

<template>
  <UseDark
    v-slot="{ isDark, toggleDark }"
    selector="html"
    attribute="data-bs-theme"
    storage-key="ade-scheduler-theme"
  >
    <button
      type="button"
      class="btn btn-link link-body-emphasis"
      @click="toggleDark()"
    >
      <Transition name="fade" mode="out-in">
        <i key="1" v-if="isDark" class="bi bi-moon-stars" />
        <i key="2" v-else class="bi bi-sun" />
      </Transition>
    </button>
  </UseDark>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<i18n lang="yaml">
en:
  dark: Dark
  light: Light
fr:
  dark: Sombre
  light: Clair
</i18n>

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
    <div class="dropdown">
      <button
        class="dropdown-toggle btn btn-link link-body-emphasis"
        type="button"
        data-bs-toggle="dropdown"
      >
        <i v-if="isDark" class="bi bi-moon-stars" />
        <i v-else class="bi bi-sun" />
      </button>
      <ul
        class="dropdown-menu dropdown-menu-end border p-1"
        style="min-width: 150px"
      >
        <li>
          <a
            class="dropdown-item d-flex align-items-center rounded"
            :class="isDark ? '' : 'active'"
            href="#"
            @click="toggleDark(false)"
          >
            <i class="bi bi-sun-fill me-2" />
            {{ t("light") }}
            <i v-if="!isDark" class="bi bi-check ms-auto" />
          </a>
        </li>
        <li class="mt-1">
          <a
            class="dropdown-item d-flex align-items-center rounded"
            :class="isDark ? 'active' : ''"
            href="#"
            @click="toggleDark(true)"
          >
            <i class="bi bi-moon-stars-fill me-2" />
            {{ t("dark") }}
            <i v-if="isDark" class="bi bi-check ms-auto" />
          </a>
        </li>
      </ul>
    </div>
  </UseDark>
</template>

<i18n lang="yaml">
en:
  dark: Dark
  light: Light
fr:
  dark: Sombre
  light: Clair
</i18n>

<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { locale } = useI18n({
  useScope: "global",
});
</script>

<template>
  <div class="dropup">
    <button
      class="dropdown-toggle btn btn-link text-decoration-none link-body-emphasis"
      role="button"
      data-bs-toggle="dropdown"
    >
      {{ locale.toUpperCase() }}
    </button>
    <ul
      class="dropdown-menu dropdown-menu-end border p-1"
      style="min-width: 50px"
    >
      <li>
        <a
          role="button"
          class="dropdown-item text-center rounded"
          :class="locale === 'fr' ? 'active' : ''"
          @click="locale = 'fr'"
        >
          FR
        </a>
      </li>
      <li class="mt-1">
        <a
          role="button"
          class="dropdown-item text-center rounded"
          :class="locale === 'en' ? 'active' : ''"
          @click="locale = 'en'"
        >
          EN
        </a>
      </li>
    </ul>
  </div>
</template>

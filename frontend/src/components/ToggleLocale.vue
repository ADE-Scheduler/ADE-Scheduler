<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { locale } = useI18n({
  useScope: "global",
});
</script>

<template>
  <div class="dropdown">
    <button
      class="dropdown-toggle btn btn-link text-decoration-none link-body-emphasis"
      type="button"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      {{ locale.toUpperCase() }}
    </button>
    <ul
      class="dropdown-menu dropdown-menu-end border p-1"
      style="min-width: 50px"
    >
      <li>
        <a
          class="dropdown-item text-center rounded"
          :class="locale === 'fr' ? 'active' : ''"
          href="#"
          @click="locale = 'fr'"
        >
          FR
        </a>
      </li>
      <li class="mt-1">
        <a
          class="dropdown-item text-center rounded"
          :class="locale === 'en' ? 'active' : ''"
          href="#"
          @click="locale = 'en'"
        >
          EN
        </a>
      </li>
    </ul>
  </div>
</template>

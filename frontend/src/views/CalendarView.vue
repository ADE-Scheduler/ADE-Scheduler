<script setup lang="ts">
import { useI18n } from "vue-i18n";

const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});
</script>

<template>
  <main>
    <h1>{{ t("calendar") }}</h1>
  </main>
</template>

<i18n lang="yaml">
en:
  calendar: "Calendar"
fr:
  calendar: "Calendrier"
</i18n>

<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import bootstrap5Plugin from "@fullcalendar/bootstrap5";
import frLocale from "@fullcalendar/core/locales/fr";

const { locale, t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, bootstrap5Plugin],
  locales: [frLocale],
  locale: locale,
  timeZone: "UTC",
  themeSystem: "bootstrap5",
  headerToolbar: {
    left: "",
    center: "title",
    right: "",
  },
  weekNumbers: true,
  dayMaxEvents: true, // allow "more" link when too many events
  events: "https://fullcalendar.io/api/demo-feeds/events.json",
});
</script>

<template>
  <div class="container py-3">
    <div
      class="p-lg-5 p-2 bg-body-tertiary rounded-3 border border-light-subtle"
    >
      <div class="container-fluid">
        <FullCalendar :options="calendarOptions" />
        <div class="text-warning-emphasis lh-sm fw-light mt-4">
          {{ t("disclaimer") }}
        </div>
      </div>
    </div>
  </div>
</template>

<i18n lang="yaml">
en:
  disclaimer: "Disclaimer: ADE Scheduler is not an official UCLouvain tool. It has been designed with the purpose to help the UCLouvain students with scheduling. This tool is based on ADE UCL but does not replace standard scheduling rules, nor the instructions given by university officials and teachers as those may vary from one course to another."
fr:
  disclaimer: "Attention: ADE Scheduler n'est pas un outil officiel de l'UCLouvain. Il a été développé dans le but d'aider les étudiants de l'UCLouvain pour la composition de leur horaire. Cet outil est basé sur ADE UCL mais ne remplace ni les règles déjà existantes, les instructions données par l'université et les professeurs, car ces informations peuvent changer d'un cours à un autre."
</i18n>

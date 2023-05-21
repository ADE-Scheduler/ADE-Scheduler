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
    left: "prev,next today",
    center: "title",
    right: "dayGridMonth,timeGridWeek",
  },
  weekNumbers: true,
  dayMaxEvents: true, // allow "more" link when too many events
  events: "https://fullcalendar.io/api/demo-feeds/events.json",
});
</script>

<template>
  <div class="container py-3">
    <div
      class="p-lg-4 p-2 pt-3 bg-body-tertiary rounded-3 border border-light-subtle"
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

<style lang="scss">
// Only put FullCalendar CSS here, it's not a scoped style block
// so it will apply website-wide rather than juste on this component.
@import "bootstrap/scss/bootstrap";

// do stuff to accomodate the fc on mobile (below the md breakpoint)
@include media-breakpoint-down(md) {
  .fc-toolbar-chunk > button,
  .fc-toolbar-chunk > * > button {
    font-size: min(3vw, 1rem);
    padding: 3px 6px;
  }
  .fc-toolbar-title {
    display: none;
  }
}

// prevent the buttons to wrap & properly center the title
.fc-toolbar-title {
  text-align: center;
}
.fc-toolbar-chunk {
  display: flex;
  flex-wrap: nowrap;
}
</style>

<i18n lang="yaml">
en:
  disclaimer: "Disclaimer: ADE Scheduler is not an official UCLouvain tool. It has been designed with the purpose to help the UCLouvain students with scheduling. This tool is based on ADE UCL but does not replace standard scheduling rules, nor the instructions given by university officials and teachers as those may vary from one course to another."
fr:
  disclaimer: "Attention: ADE Scheduler n'est pas un outil officiel de l'UCLouvain. Il a été développé dans le but d'aider les étudiants de l'UCLouvain pour la composition de leur horaire. Cet outil est basé sur ADE UCL mais ne remplace ni les règles déjà existantes, les instructions données par l'université et les professeurs, car ces informations peuvent changer d'un cours à un autre."
</i18n>

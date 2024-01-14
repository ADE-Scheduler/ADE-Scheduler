<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { ref, watchEffect, onUnmounted, onActivated } from "vue";
import { getWeekText } from "@/utils/weeknumbers";
import { useBreakpoints } from "@/composables/breakpoints";

import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import bootstrap5Plugin from "@fullcalendar/bootstrap5";
import frLocale from "@fullcalendar/core/locales/fr";

// i18n stuff
const { locale, t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// FC options
const fcOptions = ref({
  // plugins
  plugins: [dayGridPlugin, timeGridPlugin, bootstrap5Plugin],
  // locales
  locales: [frLocale],
  locale: locale,
  // view params
  height: "auto",
  navLinks: true,
  editable: false,
  droppable: false,
  slotMinTime: "08:00:00",
  slotMaxTime: "21:00:00",
  timeZone: "Europe/Brussels",
  themeSystem: "bootstrap5",
  // header
  headerToolbar: {
    left: "prev,next today",
    center: "title",
    right: "", // will be set/updated reactively in the watchEffect
  },
  // weeks
  firstDay: 1,
  weekNumbers: true,
  weekNumberContent: getWeekText,

  events: "https://fullcalendar.io/api/demo-feeds/events.json",
});

// Make the FC reactive
const { isSm } = useBreakpoints();
watchEffect(() => {
  fcOptions.value.headerToolbar.right = isSm.value
    ? "dayGridMonth,timeGridDay"
    : "dayGridMonth,timeGridWeek";
});

// Refresh the FC when loading from cache
const fc = ref<InstanceType<typeof FullCalendar> | null>(null);
onActivated(() => {
  fc.value?.getApi().render();
});
</script>

<template>
  <div class="container py-3">
    <div
      class="p-lg-4 p-2 pt-3 bg-body-tertiary rounded-3 border border-light-subtle"
    >
      <FullCalendar ref="fc" :options="fcOptions" />
      <div class="text-warning-emphasis lh-sm fw-light mt-4">
        {{ t("disclaimer") }}
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

// Fix bug when using height: auto
.fc-col-header-cell {
  color: var(--bs-gray-700);
}
</style>

<i18n lang="yaml">
en:
  disclaimer: "Disclaimer: ADE Scheduler is not an official UCLouvain tool. It has been designed with the purpose to help the UCLouvain students with scheduling. This tool is based on ADE UCL but does not replace standard scheduling rules, nor the instructions given by university officials and teachers as those may vary from one course to another."
fr:
  disclaimer: "Attention: ADE Scheduler n'est pas un outil officiel de l'UCLouvain. Il a été développé dans le but d'aider les étudiants de l'UCLouvain pour la composition de leur horaire. Cet outil est basé sur ADE UCL mais ne remplace ni les règles déjà existantes, les instructions données par l'université et les professeurs, car ces informations peuvent changer d'un cours à un autre."
</i18n>

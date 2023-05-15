<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import bootstrap5Plugin from '@fullcalendar/bootstrap5';
import frLocale from '@fullcalendar/core/locales/fr';

const { locale } = useI18n();

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, bootstrap5Plugin],
  locales: [frLocale],
  locale: locale,
  timeZone: 'UTC',
  themeSystem: 'bootstrap5',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  weekNumbers: true,
  dayMaxEvents: true, // allow "more" link when too many events
  events: 'https://fullcalendar.io/api/demo-feeds/events.json',
});
</script>

<template>
  <div class="container py-4">
    <div class="p-lg-5 p-2 bg-body-tertiary rounded-3 border border-light-subtle">
      <div class="container-fluid">
        <FullCalendar :options="calendarOptions" />
      </div>
    </div>
  </div>
</template>

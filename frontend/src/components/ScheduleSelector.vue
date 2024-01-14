<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { Collapse } from "bootstrap";
import { useToggle } from "@vueuse/core";
import { useScheduleStore } from "@/stores";
import { onMounted, ref, watch } from "vue";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// schedule store
const scheduleStore = useScheduleStore();

// TODO: Select schedule function
function selectSchedule(id: number) {
  scheduleStore.setCurrentSchedule(id);
  showCollapse.value = false;
}

// TODO: Create new schedule function
function newSchedule() {
  scheduleStore.newSchedule();
  showCollapse.value = false;
}

// Collapse management
let bsCollapse: Collapse;
const collapse = ref<Element | null>(null);
const [showCollapse, toggleCollapse] = useToggle(false);
onMounted(() => {
  if (collapse.value === null) {
    throw new Error("Collapse element is null");
  }
  // create the collapse
  bsCollapse = new Collapse(collapse.value, {
    toggle: showCollapse.value,
  });
});
watch(showCollapse, (value) => {
  if (value) {
    bsCollapse.show();
  } else {
    bsCollapse.hide();
  }
});
</script>

<template>
  <a
    role="button"
    class="d-flex justify-content-between flex-nowrap link-body-emphasis text-decoration-none mt-2"
    @click="toggleCollapse()"
  >
    <h5 class="text-truncate fw-medium">
      {{ scheduleStore.currentSchedule.name }}
    </h5>
    <h5
      style="transition: 0.2s"
      :style="{ transform: 'rotate(' + (showCollapse ? 90 : 0) + 'deg)' }"
    >
      <i class="bi bi-chevron-right"></i>
    </h5>
  </a>
  <div class="collapse" ref="collapse">
    <ul class="list-group list-group-flush">
      <RouterLink
        role="button"
        class="list-group-item list-group-item-action bg-body-tertiary fs-6"
        v-for="{ id, name } in scheduleStore.schedules"
        :key="id"
        :to="{ name: 'Schedule', params: { schedule: id } }"
        :class="{
          'text-primary-emphasis':
            id ===
            parseInt(
              Array.isArray($route.params.schedule)
                ? '-1'
                : $route.params.schedule
            ),
        }"
      >
        <div class="text-truncate">
          {{ name }}
        </div>
      </RouterLink>
      <li
        role="button"
        class="list-group-item list-group-item-action bg-body-tertiary"
        @click="newSchedule()"
      >
        <div class="d-flex justify-content-between fw-bold">
          <span>
            {{ t("new-schedule") }}
          </span>
          <i class="bi bi-plus-lg text-success me-0" />
        </div>
      </li>
    </ul>
  </div>
</template>

<i18n lang="yaml">
en:
  new-schedule: New schedule
fr:
  new-schedule: Nouvel horaire
</i18n>

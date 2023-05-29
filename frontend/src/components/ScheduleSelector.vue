<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { Collapse } from "bootstrap";
import { useToggle } from "@vueuse/core";
import { onMounted, ref, watch } from "vue";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// TODO: get this as a prop or from a store
const selectedSchedule = ref(1);
const data = ref([
  { id: 1, name: "Schedule 1" },
  { id: 2, name: "Schedule 2" },
  { id: 3, name: "Schedule 3" },
  { id: 4, name: "Schedule 4 - a very long schedule !" },
]);

// TODO: Select schedule function
function selectSchedule(id: number) {
  selectedSchedule.value = id;
  showCollapse.value = false;
}

// TODO: Create new schedule function
function newSchedule() {
  data.value.push({
    id: data.value.length + 1,
    name: "Schedule " + (data.value.length + 1),
  });
  selectSchedule(data.value.length);
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
    type="button"
    class="d-flex justify-content-between flex-nowrap link-body-emphasis text-decoration-none mt-2"
    @click="toggleCollapse()"
  >
    <h5 class="text-truncate fw-medium">
      {{ data.find((s) => s.id === selectedSchedule)?.name }}
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
      <li
        type="button"
        class="list-group-item list-group-item-action bg-body-tertiary fs-6"
        v-for="schedule in data"
        :key="schedule.id"
        @click="selectSchedule(schedule.id)"
      >
        {{ schedule.name }}
      </li>
      <li
        type="button"
        class="list-group-item list-group-item-action bg-body-tertiary"
        @click="newSchedule()"
      >
        <div class="d-flex justify-content-between fw-bold">
          <span>
            {{ t("new-schedule") }}
          </span>
          <i class="bi bi-plus-lg me-2 text-success" />
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

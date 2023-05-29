<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { Collapse } from "bootstrap";
import { useScheduleStore } from "@/stores";
import { onMounted, ref, watch } from "vue";
import { useToggle, useConfirmDialog } from "@vueuse/core";

import ConfirmModal from "@/components/ConfirmModal.vue";

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
}

// Schedule action buttons
const showBtnAction = ref<number | null>(null);

// TODO: Delete schedule function
const confirmScheduleDelete = useConfirmDialog();
const confirmScheduleDeleteName = ref<string | undefined>(undefined);
async function deleteSchedule(id: number) {
  // get the name of the schedule
  confirmScheduleDeleteName.value = scheduleStore.getScheduleName(id);
  // get user confirmation
  const res = await confirmScheduleDelete.reveal();
  if (!res.isCanceled && res.data) {
    scheduleStore.deleteSchedule(id);
  }
}

// TODO: Edit schedule function
function editSchedule(id: number) {
  console.log("edit schedule", id);
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
  <ConfirmModal
    :reveal="confirmScheduleDelete.isRevealed.value"
    @cancel="confirmScheduleDelete.cancel()"
    @confirm="confirmScheduleDelete.confirm(true)"
  >
    <template #header>{{ t("confirm-delete-header") }}</template>
    <template #body>{{
      t("confirm-delete-body", { s: confirmScheduleDeleteName })
    }}</template>
    <template #action>{{ t("confirm-delete-action") }}</template>
  </ConfirmModal>

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
      <li
        role="button"
        class="list-group-item list-group-item-action bg-body-tertiary fs-6"
        v-for="{ id, name } in scheduleStore.schedules"
        :key="id"
        @mouseover="showBtnAction = id"
        @mouseleave="showBtnAction = null"
        @click="selectSchedule(id)"
      >
        <div
          style="min-height: 26px"
          class="d-flex justify-content-between align-items-center"
        >
          <span class="text-truncate">
            {{ name }}
          </span>
          <div class="d-flex flex-nowrap" v-if="showBtnAction === id">
            <button
              role="button"
              class="btn btn-link link-primary py-0 pe-0"
              @click.stop="editSchedule(id)"
            >
              <i class="bi bi-pencil"></i>
            </button>
            <button
              role="button"
              class="btn btn-link link-danger py-0 pe-0"
              @click.stop="deleteSchedule(id)"
            >
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
      </li>
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
  confirm-delete-header: Delete schedule ?
  confirm-delete-body: The schedule "{s}" will be deleted permanently.
  confirm-delete-action: Delete
fr:
  new-schedule: Nouvel horaire
  confirm-delete-header: Supprimer l'horaire ?
  confirm-delete-body: L'horaire "{s}" sera supprimé définitivement.
  confirm-delete-action: Supprimer
</i18n>

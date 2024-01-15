<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useAlertStore } from "@/stores";
import { useScheduleStore } from "@/stores";
import { useConfirmDialog } from "@vueuse/core";
import { useRoute, useRouter } from "vue-router";

import NavBack from "@/components/NavBack.vue";
import ConfirmModal from "@/components/ConfirmModal.vue";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// stores
const alertStore = useAlertStore();
const scheduleStore = useScheduleStore();

// router
const route = useRoute();
const router = useRouter();

// sanitize the schedule
if (Array.isArray(route.params.schedule)) {
  alertStore.append("danger", t("error-schedule-array"));
  throw new Error("Schedule ID is an array of strings");
}
// TODO: handle errors in parseInt
const sid = ref<number>(parseInt(route.params.schedule));

// Delete schedule
const confirmScheduleDelete = useConfirmDialog();
const confirmScheduleDeleteName = ref<string | undefined>(undefined);
async function deleteSchedule() {
  // get the name of the schedule
  confirmScheduleDeleteName.value = scheduleStore.getScheduleName(sid.value);
  // get user confirmation
  const res = await confirmScheduleDelete.reveal();
  if (!res.isCanceled && res.data) {
    router.push({ name: "Calendar" });
    // only delete the schedule once we nav'd out
    scheduleStore.deleteSchedule(sid.value);
  }
}
</script>

<template>
  <div>
    <!-- Confirm deletion Modal -->
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

    <!-- Main content -->
    <div class="container py-3">
      <NavBack :to="{ name: 'Calendar' }">{{ t("nav-back") }}</NavBack>
      <div class="mt-3">
        <div class="d-flex">
          <h1 class="display-6">{{ scheduleStore.getScheduleName(sid) }}</h1>
          <div class="d-flex ms-auto">
            <button
              role="button"
              class="btn btn-link link-danger ms-auto"
              @click="deleteSchedule()"
            >
              <i class="bi bi-trash3"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<i18n lang="yaml">
en:
  nav-back: "Back to calendar"
  error-schedule-array: "URL schedule argument is an array of strings"
  confirm-delete-header: Delete schedule ?
  confirm-delete-body: The schedule "{s}" will be deleted permanently.
  confirm-delete-action: Delete
fr:
  nav-back: "Retour au calendrier"
  error-schedule-array: "L'argument schedule de l'URL est un tableau de strings"
  confirm-delete-header: Supprimer l'horaire ?
  confirm-delete-body: L'horaire "{s}" sera supprimé définitivement.
  confirm-delete-action: Supprimer
</i18n>

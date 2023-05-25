<script setup lang="ts">
import { Toast } from "bootstrap";
import { useI18n } from "vue-i18n";
import { ref, onMounted, computed } from "vue";
import { useAlertStore } from "@/stores";
import { useEventListener } from "@vueuse/core";

const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// fetch the alert store
const alertStore = useAlertStore();

// props
const props = defineProps<{
  id: number;
  type: string;
  message: string;
}>();

// toast background & title
const toastBg = computed(() => `bg-${props.type}-subtle`);
const toastHd = computed(() => {
  switch (props.type) {
    case "danger":
      return t("danger");
    case "warning":
      return t("warning");
    case "success":
      return t("success");
    default:
      return t("info");
  }
});

// initialize the toast
let bsToast: Toast;
const toast = ref<Element | null>(null);
onMounted(() => {
  if (toast.value === null) {
    throw new Error("Toast element is null");
  }
  // create the toast & show it
  bsToast = new Toast(toast.value);
  bsToast.show();
  // on close, remove the alert from the queue
  // we want bootstrap to do the closing, so that we have the fancy animation
  useEventListener(toast.value, "hide.bs.toast", () => {
    alertStore.remove(props.id);
  });
});
</script>

<template>
  <div class="toast" :class="toastBg" role="alert" ref="toast">
    <!-- Toast header -->
    <div class="toast-header">
      <span class="me-auto">{{ toastHd }}</span>
      <button type="button" class="btn-close" data-bs-dismiss="toast" />
    </div>
    <!-- Toast body -->
    <div class="toast-body">
      {{ message }}
    </div>
  </div>
</template>

<i18n lang="yaml">
en:
  info: "Info"
  danger: "Error"
  warning: "Warning"
  success: "Success"
fr:
  info: "Information"
  danger: "Erreur"
  warning: "Attention"
  success: "Succès !"
</i18n>

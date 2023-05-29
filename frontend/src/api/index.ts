import i18n from "@/i18n";
import { ref, watchEffect } from "vue";
import { createFetch } from "@vueuse/core";
import { useNProgress } from "@vueuse/integrations/useNProgress";
import { useAlertStore } from "@/stores";

// Request loading indicator
const { isLoading, progress } = useNProgress();

// Watch the number of active requests
const count = ref(0);
watchEffect(() => {
  isLoading.value = count.value > 0;
});

const instance = createFetch({
  baseUrl: "/api",
  options: {
    timeout: 5000,
    beforeFetch: () => {
      count.value++;
    },
    afterFetch: (ctx) => {
      count.value--;
      return ctx;
    },
    onFetchError: (ctx) => {
      const alertStore = useAlertStore();
      if (ctx.error.name === "AbortError") {
        // timeout error (abort was called)
        alertStore.append("danger", i18n.global.t("request-timeout"));
      } else {
        // generic error message
        alertStore.append("danger", ctx.error.message);
      }
      count.value--;
      return ctx;
    },
  },
});

export {
  // req progress variables
  isLoading,
  progress,
  // req methods
  instance as fetch,
};

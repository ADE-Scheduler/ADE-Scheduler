import axios from "axios";
import i18n from "@/i18n";
import { useAlertStore } from "@/stores";
import { useNProgress } from "@vueuse/integrations/useNProgress";

// Request loading indicator
const { isLoading, progress } = useNProgress();

// The Axios instance
const instance = axios.create({
  timeout: 5000, // TODO: what timeout is the best ?
  baseURL: "/api",
});

// Interceptors (request)
instance.interceptors.request.use(
  (config) => {
    isLoading.value = true;
    return config;
  },
  (error) => {
    isLoading.value = false;
    return Promise.reject(error);
  }
);

// Interceptors (response)
instance.interceptors.response.use(
  (response) => {
    isLoading.value = false;
    return response;
  },
  (error) => {
    if (error.code === "ECONNABORTED") {
      const alertStore = useAlertStore();
      alertStore.append("danger", i18n.global.t("request-timeout"));
    }
    isLoading.value = false;
    return Promise.reject(error);
  }
);

export {
  // req progress variables
  isLoading,
  progress,
  // req methods
  instance as axios,
};

import { ref } from "vue";
import { defineStore } from "pinia";

interface AlertMessage {
  id: number;
  type: string;
  message: string;
}

export const useAlertStore = defineStore("alert", () => {
  // alert message queue
  const queue = ref<AlertMessage[]>([]);

  // add alert message to queue
  function append(type: string, message: string) {
    const id = Date.now();
    queue.value.push({ id, type, message });
  }

  // remove alert message from queue
  function remove(id: number) {
    queue.value = queue.value.filter((alert) => alert.id !== id);
  }

  return { queue, append, remove };
});

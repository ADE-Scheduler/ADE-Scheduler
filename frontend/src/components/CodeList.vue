<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// TODO: get this as a prop or from a store
// TODO: watcher to fetch events based on this list
const data = ref([
  { id: 1, name: "code 1" },
  { id: 2, name: "code 2" },
  { id: 3, name: "code 3" },
  { id: 4, name: "code 4 - a very long code !" },
]);

// delete button
const showBtnAction = ref<number | null>(null);
function deleteCode(id: number) {
  // TODO: action to delete the events associated to the code
  // TODO: req to backend to track state
  data.value = data.value.filter((code) => code.id !== id);
}

// add code
const inputCode = ref("");
function addCode() {
  // TODO
  if (inputCode.value) {
    data.value.push({ id: data.value.length + 1, name: inputCode.value });
    inputCode.value = "";
  }
}
</script>

<template>
  <ul class="list-group w-100">
    <a
      href="#"
      class="list-group-item list-group-item-action list-group-item-light"
      v-for="code in data"
      :key="code.id"
      @mouseover="showBtnAction = code.id"
      @mouseleave="showBtnAction = null"
    >
      <div class="d-flex justify-content-between">
        <span class="text-truncate">
          {{ code.name }}
        </span>
        <button
          type="button"
          class="btn btn-link link-danger py-0 pe-0"
          @click="deleteCode(code.id)"
          v-show="showBtnAction === code.id"
        >
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
    </a>
    <ul class="list-group-item p-0">
      <div class="bg-transparent">
        <input
          type="text"
          style="padding-end: 40px"
          class="form-control border-0"
          :class="{ 'rounded-top-0': data.length > 0 }"
          :placeholder="t('add-code')"
          @keyup.enter="addCode()"
          v-model="inputCode"
        />
        <button
          type="button"
          class="btn btn-link link-success border-0 position-absolute top-0 end-0"
          @click="addCode()"
        >
          <i class="bi bi-plus-lg"></i>
        </button>
      </div>
    </ul>
  </ul>
</template>

<i18n lang="yaml">
en:
  add-code: "Enter code"
fr:
  add-code: "Entrez un code"
</i18n>

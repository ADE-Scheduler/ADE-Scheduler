<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useScheduleStore } from "@/stores";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// Focus directive
const vFocus = {
  mounted: (el: HTMLElement) => el.focus(),
};

// schedule store
const scheduleStore = useScheduleStore();

// TODO: Add code function
const inputCode = ref("");
function addCode() {
  if (inputCode.value) {
    scheduleStore.addCode(inputCode.value);
    inputCode.value = "";
  }
}
</script>

<template>
  <ul class="list-group w-100">
    <RouterLink
      class="list-group-item list-group-item-action list-group-item-light"
      v-for="{ id, code } in scheduleStore.codes"
      :key="id"
      :class="{ active: $route.params.code === code }"
      :to="{ name: 'Code', params: { code } }"
    >
      <span class="text-truncate">
        {{ code }}
      </span>
    </RouterLink>
    <li class="list-group-item p-0">
      <div class="bg-transparent">
        <input
          type="text"
          style="padding-end: 40px"
          class="form-control border-0"
          :class="{ 'rounded-top-0': scheduleStore.codes.length > 0 }"
          :placeholder="t('add-code')"
          @keyup.enter="addCode()"
          v-model="inputCode"
          v-focus
        />
        <button
          role="button"
          class="btn btn-link link-success border-0 position-absolute top-0 end-0"
          @click="addCode()"
        >
          <i class="bi bi-plus-lg"></i>
        </button>
      </div>
    </li>
  </ul>
</template>

<i18n lang="yaml">
en:
  add-code: "Enter code"
fr:
  add-code: "Entrez un code"
</i18n>

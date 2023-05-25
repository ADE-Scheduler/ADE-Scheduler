<script setup lang="ts">
import { fetch } from "@/api";
import MainCalendar from "@/components/MainCalendar.vue";
import OffcanvasMenu from "@/components/OffcanvasMenu.vue";

const { data } = fetch("calendar").get();
</script>

<template>
  <div class="row">
    <div class="col-md-4 col-lg-3 col-xxl-2 px-0">
      <OffcanvasMenu>
        <template #header> Menu </template>
        <template #body> Body </template>
      </OffcanvasMenu>
    </div>
    <div class="col-md-8 col-lg-9 col-xxl-10 px-0">
      <MainCalendar />
    </div>
  </div>
</template>

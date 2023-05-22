<script setup lang="ts">
import MainCalendar from "@/components/MainCalendar.vue";
import OffcanvasMenu from "@/components/OffcanvasMenu.vue";
</script>

<template>
  <div class="container-fluid d-flex p-0">
    <OffcanvasMenu>
      <template #header> Menu </template>
      <template #body> Body </template>
    </OffcanvasMenu>
    <MainCalendar />
  </div>
</template>

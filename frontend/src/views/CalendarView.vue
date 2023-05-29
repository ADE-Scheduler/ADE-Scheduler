<script setup lang="ts">
import { fetch } from "@/api";
import { onUnmounted } from "vue";
import CodeList from "@/components/CodeList.vue";
import ToggleDark from "@/components/ToggleDark.vue";
import ToggleLocale from "@/components/ToggleLocale.vue";
import MainCalendar from "@/components/MainCalendar.vue";
import OffcanvasMenu from "@/components/OffcanvasMenu.vue";
import ScheduleSelector from "@/components/ScheduleSelector.vue";

const { data, abort } = fetch("calendar").get();
onUnmounted(abort);
</script>

<template>
  <div class="row">
    <div class="col-md-4 col-lg-3 col-xxl-2 px-0">
      <OffcanvasMenu>
        <!-- Offcanvas menu header -->
        <template #header> Menu </template>
        <!-- Offcanvas menu body -->
        <template #body>
          <div class="d-flex flex-column w-100 h-100">
            <!-- Schedule selector -->
            <ScheduleSelector />
            <!-- Code list -->
            <CodeList class="my-3" />
            <!-- Actions & Links -->
            <div class="d-flex justify-content-center mt-auto">
              <ToggleLocale />
              <div class="vr" />
              <ToggleDark />
              <div class="vr" />
              <a
                href="https://www.buymeacoffee.com/adescheduler"
                class="btn btn-link link-warning"
                target="_blank"
              >
                <i class="bi bi-cup-hot-fill"></i>
              </a>
              <div class="vr" />
              <a
                href="https://github.com/ADE-Scheduler/ADE-Scheduler"
                class="btn btn-link link-body-emphasis"
                target="_blank"
              >
                <i class="bi bi-github"></i>
              </a>
            </div>
          </div>
        </template>
      </OffcanvasMenu>
    </div>
    <div class="col-md-8 col-lg-9 col-xxl-10 px-0">
      <MainCalendar />
    </div>
  </div>
</template>

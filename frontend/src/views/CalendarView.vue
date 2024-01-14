<script setup lang="ts">
import CodeList from "@/components/CodeList.vue";
import ToggleDark from "@/components/ToggleDark.vue";
import ToggleLocale from "@/components/ToggleLocale.vue";
import OffcanvasMenu from "@/components/OffcanvasMenu.vue";
import ScheduleSelector from "@/components/ScheduleSelector.vue";
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
      <Transition name="fade" mode="out-in">
        <RouterView v-slot="{ Component, route }">
          <KeepAlive>
            <Component :is="Component" :key="route.path" />
          </KeepAlive>
        </RouterView>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

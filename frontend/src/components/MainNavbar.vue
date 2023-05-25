<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { RouterLink } from "vue-router";

import ToggleDark from "@/components/ToggleDark.vue";
import ToggleLocale from "@/components/ToggleLocale.vue";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});
</script>

<template>
  <nav
    class="navbar navbar-expand-lg shadow sticky-top bg-body-tertiary"
    data-bs-theme="dark"
  >
    <div class="container-fluid">
      <!-- logo -->
      <a class="navbar-brand" href="#">ADE Scheduler</a>
      <!-- collapser -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#main-navbar"
      >
        <span class="navbar-toggler-icon" />
      </button>
      <!-- collapsee -->
      <div id="main-navbar" class="collapse navbar-collapse">
        <!-- nav links -->
        <ul class="navbar-nav">
          <li class="nav-item">
            <RouterLink class="nav-link" to="Calendar" active-class="active">
              {{ t("calendar") }}
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" to="Classroom" active-class="active">
              {{ t("classrooms") }}
            </RouterLink>
          </li>
        </ul>
        <!-- end of navbar -->
        <div class="d-flex justify-content-center ms-auto mt-lg-0 mt-4">
          <ToggleLocale />
          <div class="vr text-light" />
          <ToggleDark />
        </div>
      </div>
    </div>
  </nav>
</template>

<i18n lang="yaml">
en:
  calendar: "Calendar"
  classrooms: "Classrooms"
fr:
  calendar: "Calendrier"
  classrooms: "Locaux"
</i18n>

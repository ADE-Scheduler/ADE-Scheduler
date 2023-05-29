<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { RouterLink } from "vue-router";

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
      <RouterLink class="navbar-brand" role="button" :to="{ name: 'Calendar' }">
        ADE Scheduler
      </RouterLink>
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
            <RouterLink
              class="nav-link"
              active-class="active"
              :to="{ name: 'Calendar' }"
            >
              {{ t("calendar") }}
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink
              class="nav-link"
              active-class="active"
              :to="{ name: 'Classroom' }"
            >
              {{ t("classroom") }}
            </RouterLink>
          </li>
        </ul>
        <!-- end of navbar -->
        <div class="d-flex justify-content-center ms-auto mt-lg-0 mt-4">
          <!-- TODO: login/logout -->
          <button type="button" class="btn btn-sm btn-outline-light">
            {{ t("login") }}
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<i18n lang="yaml">
en:
  login: "Login"
  calendar: "Calendar"
  classroom: "Classrooms"
fr:
  login: "Connexion"
  calendar: "Calendrier"
  classroom: "Locaux"
</i18n>

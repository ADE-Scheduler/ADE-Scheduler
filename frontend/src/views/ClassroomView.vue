<script setup lang="ts">
import { fetch } from "@/api";
import { onUnmounted, ref } from "vue";

import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer } from "@vue-leaflet/vue-leaflet";

// Get the map
const map = ref<InstanceType<typeof LMap> | null>(null);
const zoom = defineModel({ default: 15 });

// Fetch classroom data
const { data, abort } = fetch("classrooms").get();
onUnmounted(abort);
</script>

<template>
  <div class="container py-3">
    <div class="border border-primary-subtle">
      <LMap
        ref="map"
        style="height: 500px"
        v-model:zoom="zoom"
        :center="[50.6681, 4.6118]"
      >
        <LTileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      </LMap>
    </div>
  </div>
</template>

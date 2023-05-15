<script setup lang="ts">
import { RouterView } from 'vue-router';

import Navbar from '@/components/MainNavbar.vue';
</script>

<template>
  <div>
    <Navbar />
    <RouterView />
  </div>
</template>

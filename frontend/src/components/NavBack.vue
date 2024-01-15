<script setup lang="ts">
interface Props {
  to: { name: string; params?: Record<string, string> };
}

const props = defineProps<Props>();
</script>

<template>
  <RouterLink
    :to="props.to"
    class="link-hover link-secondary link-underline-opacity-0"
  >
    <i class="bi bi-arrow-left d-inline-block me-2" />
    <span><slot /></span>
  </RouterLink>
</template>

<style scoped>
.link-hover > i {
  transition: transform 0.2s ease-in-out;
}
.link-hover:hover > i {
  transform: translate(-0.25em, 0);
}
</style>

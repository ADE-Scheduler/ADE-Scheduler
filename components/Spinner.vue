<template>
  <div>
    <div v-show="computing" class="spinner-border text-primary" />
    <div :style="opacity">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  props: ['computing'],
  computed: {
    opacity() {
      return { opacity: this.computing ? '0.2' : '1' };
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../static/css/bootstrap.scss';

.spinner-border {
  position: fixed;
  top: 50%;
  left: 50%;
  z-index: 100;
}
</style>

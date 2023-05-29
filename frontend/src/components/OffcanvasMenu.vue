<script setup lang="ts">
import { Offcanvas } from "bootstrap";
import { ref, onMounted } from "vue";
import { useSwipe, type UseSwipeDirection } from "@vueuse/core";

// initialize the offcanvas
let bsOffcanvas: Offcanvas;
const offcanvas = ref<Element | null>(null);
onMounted(() => {
  if (offcanvas.value === null) {
    throw new Error("Offcanvas element is null");
  }
  // create the offcanvas
  bsOffcanvas = new Offcanvas(offcanvas.value);
});

// close the offcanvas on swipe
useSwipe(offcanvas, {
  onSwipeEnd(_, direction: UseSwipeDirection) {
    if (direction === "left") {
      bsOffcanvas.hide();
    }
  },
});
</script>

<template>
  <button
    type="button"
    class="btn btn-sm btn-primary rounded-3 d-md-none position-fixed bottom-0 end-0 z-3 me-2 mb-2"
    @click="bsOffcanvas.show()"
  >
    <i class="bi bi-list"></i>
  </button>

  <div
    class="offcanvas-md offcanvas-start bg-body-tertiary border-end border-light-subtle position-fixed"
    style="width: inherit"
    tabindex="-1"
    ref="offcanvas"
  >
    <!-- Header -->
    <div class="offcanvas-header">
      <h5 class="offcanvas-title">
        <slot name="header" />
      </h5>
      <button
        type="button"
        class="btn-close"
        @click="bsOffcanvas.hide()"
      ></button>
    </div>
    <!-- Body -->
    <div class="offcanvas-body overflow-y-auto p-3">
      <slot name="body" />
    </div>
  </div>
</template>

<style scoped>
/* this is needed for the scroll behavior, I would really like to remove it... */
.offcanvas-body {
  height: calc(100vh - 56px);
}
</style>

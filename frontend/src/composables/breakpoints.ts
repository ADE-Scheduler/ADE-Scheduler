import { ref, watchEffect } from "vue";
import { useWindowSize } from "@vueuse/core";

// Window width
const { width } = useWindowSize();

// Setup breakpoints variable, watch for width change
const isSm = ref();
const isMd = ref();
const isLg = ref();
const isXl = ref();
const isXxl = ref();

watchEffect(() => {
  // Values are based on Bootstrap breakpoints (hardcoded)
  isSm.value = width.value < 576;
  isMd.value = width.value < 768;
  isLg.value = width.value < 992;
  isXl.value = width.value < 1200;
  isXxl.value = width.value < 1400;
});

export function useBreakpoints() {
  return { isSm, isMd, isLg, isXl, isXxl, width };
}

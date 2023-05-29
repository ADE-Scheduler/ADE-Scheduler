<script setup lang="ts">
import { Modal } from "bootstrap";
import { ref, onMounted, watch } from "vue";

// Props
const props = defineProps<{
  reveal: boolean;
}>();

// Emitted events
defineEmits(["cancel", "confirm"]);

// initialize the modal
let bsModal: Modal;
const modal = ref<Element | null>(null);
onMounted(() => {
  if (modal.value === null) {
    throw new Error("Modal element is null");
  }
  // create the modal
  bsModal = new Modal(modal.value);
  // show the modal
  if (props.reveal) {
    bsModal.show();
  }
});

// watch reveal
watch(
  () => props.reveal,
  (value) => {
    if (value) {
      bsModal.show();
    } else {
      bsModal.hide();
    }
  }
);
</script>

<template>
  <Teleport to="body">
    <div class="modal fade" data-bs-backdrop="static" ref="modal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header text-danger">
            <i class="bi bi-exclamation-triangle text-danger me-2"></i>
            <slot name="header" />
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              @click="$emit('cancel')"
            ></button>
          </div>
          <!-- Body -->
          <div class="modal-body">
            <slot name="body" />
          </div>
          <!-- Footer -->
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              data-bs-dismiss="modal"
              @click="$emit('cancel')"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-danger"
              data-bs-dismiss="modal"
              @click="$emit('confirm')"
            >
              <slot name="action" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<template>
  <div>
    <div ref="toast" class="toast" :class="[`bg-${type}`, textColor]">
      <div class="toast-header">
        <i class="bi bi-hand-thumbs-up me-2" v-if="type === 'success'"></i>
        <i class="bi bi-exclamation-triangle me-2" v-else></i>
        <strong class="me-auto">
          {{ header }}
        </strong>
        <button class="btn-close" data-bs-dismiss="toast"></button>
      </div>
      <div class="toast-body">
        <div v-html="message"></div>
        <!-- <small v-if="type === 'danger'">
          If this happens again, don't hesitate to contact us !
        </small> -->
      </div>
    </div>
  </div>
</template>

<script>
import { Toast } from 'bootstrap';

export default {
  name: 'AlertToast',
  props: ['type', 'message'],
  computed: {
    header() {
      switch (this.type) {
        case 'primary':
          return 'Info';
        case 'danger':
          return 'Error';
        case 'warning':
          return 'Warning';
        case 'success':
          return 'Success';
        default:
          return '';
      }
    },
    textColor() {
      return this.type === 'danger' ||
        this.type === 'success' ||
        this.type === 'primary'
        ? 'text-white'
        : '';
    },
  },
  watch: {
    message() {
      if (this.message !== '') this.toast.show();
    },
  },
  mounted() {
    const toastEl = this.$refs.toast;
    this.toast = new Toast(toastEl);
    toastEl.addEventListener('hidden.bs.toast', () => {
      this.$emit('toast-hidden');
    });
  },
};
</script>

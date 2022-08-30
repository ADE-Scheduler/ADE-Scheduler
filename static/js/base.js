/* global Flask */

import Vue from 'vue';
import AlertToast from '../../components/AlertToast.vue';
import store from './store.js';

import '../css/base.css';
import '../css/bootstrap.scss';

Vue.directive('focus', {
  inserted(el) {
    el.focus();
  },
});

export default document.addEventListener('DOMContentLoaded', () => {
  new Vue({
    el: '#app-base',
    delimiters: ['[[', ']]'],
    components: { alerttoast: AlertToast },
    directives: {
      // To render Flask flash messages
      flash: {
        bind(el, binding) {
          switch (binding.arg) {
          case 'success':
            store.success(binding.value);
            break;
          case 'warning':
            store.warning(binding.value);
            break;
          case 'error':
            store.error(binding.value);
            break;
          default:
            store.info(binding.value);
          }
        },
      },
    },
    data() {
      return {
        currentPath: window.location.pathname,
      };
    },
    computed: {
      infoMessage: {
        get() {
          return store.state.infoMessage;
        },
        set(value) {
          store.commit('setInfoMessage', value);
        },
      },
      errorMessage: {
        get() {
          return store.state.errorMessage;
        },
        set(value) {
          store.commit('setErrorMessage', value);
        },
      },
      warningMessage: {
        get() {
          return store.state.warningMessage;
        },
        set(value) {
          store.commit('setWarningMessage', value);
        },
      },
      successMessage: {
        get() {
          return store.state.successMessage;
        },
        set(value) {
          store.commit('setSuccessMessage', value);
        },
      },
    },
    methods: {
      localeSelector(e, locale) {
        window.location.href = `${Flask.url_for('set_locale', {
          locale,
        })}?next=${window.location.pathname}`;
      },
    },
  });

  document
    .querySelector('[data-bs-toggle="offcanvas"]')
    .addEventListener('click', () => {
      document.querySelector('.offcanvas-collapse').classList.toggle('open');
    });
});

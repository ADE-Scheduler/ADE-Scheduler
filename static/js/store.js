import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const store = new Vuex.Store({
  // For debugging purposes (ensures store state can only be mutated using
  // mutation handlers, should be off for production !)
  strict: process.env.NODE_ENV !== 'production', // eslint-disable-line no-undef
  state() {
    return {
      infoMessage: '',
      errorMessage: '',
      warningMessage: '',
      successMessage: '',
    };
  },
  mutations: {
    setInfoMessage(state, value) {
      state.infoMessage = value;
    },
    setErrorMessage(state, value) {
      state.errorMessage = value;
    },
    setWarningMessage(state, value) {
      state.warningMessage = value;
    },
    setSuccessMessage(state, value) {
      state.successMessage = value;
    },
  },
});

// Some helper functions
store.success = (msg) => store.commit('setSuccessMessage', msg);
store.warning = (msg) => store.commit('setWarningMessage', msg);
store.error = (msg) => store.commit('setErrorMessage', msg);
store.info = (msg) => store.commit('setInfoMessage', msg);

export default store;

import Vue from 'vue';
import store from './store.js';
import ScrollSpy from '../../components/ScrollSpy.vue';
import './base.js';
import '../css/contribute.css';

const axios = require('axios');

document.addEventListener('DOMContentLoaded', () => {
  new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    components: { scrollspy: ScrollSpy },
    data() {
      return {
        navBtn: false,
        content: [],
      };
    },
    mounted() {
      axios({
        method: 'GET',
        url: `/static/text/contribute/contribute-${document
          .getElementById('current-locale')
          .textContent.trim()
          .toLowerCase()}.json`,
      })
        .then((resp) => {
          this.content = resp.data;
        })
        .catch((err) => {
          store.error(err.response.data);
        })
        .then(() => {}); // TODO
    },
  });
});

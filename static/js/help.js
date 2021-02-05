import Vue from 'vue';
import ScrollSpy from '../../components/ScrollSpy.vue';
import './base.js';
import '../css/help.css';

const axios = require('axios');


document.addEventListener('DOMContentLoaded', function() {
  new Vue({
    el: '#app',
    delimiters: ['[[',']]'],
    components: { 'scrollspy': ScrollSpy },
    data: function() {
      return {
        navBtn: false,
        content: {},
      };
    },
    mounted() {
      axios({
        method: 'GET',
        url: `/static/text/help/help-${document.getElementById('current-locale').textContent.trim().toLowerCase()}.json`
      })
        .then(resp => {
          this.content = resp.data;
        })
        .catch(() => {})
        .then(() => {});  // TODO
    },
  });
});

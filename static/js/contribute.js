import Vue from 'vue';
import ScrollSpy from '../../components/ScrollSpy.vue';
import './base.js';
import '../css/contribute.css';


document.addEventListener('DOMContentLoaded', function() {
  new Vue({
    el: '#app',
    data: {
      navBtn: false,
    },
    delimiters: ['[[',']]'],
    components: { 'scrollspy': ScrollSpy },
  });
});

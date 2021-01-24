import Vue from 'vue';
import { Collapse, ScrollSpy } from 'bootstrap';
import './base.js';
import '../css/help.css';


document.addEventListener('DOMContentLoaded', function() {
  new Vue({
    el: '#app',
    data: {
      navBtn: false,
    },
    delimiters: ['[[',']]'],

    methods: {
      scroll: function(id, flag) {
        document.getElementById(id).scrollIntoView();
        if (window.innerWidth < 767.98 && !flag) {
          this.toggleNav(false);
        }
      },
      toggleNav: function(show) {
        this.navBtn = show;
        if (show)   { nav.show(); }
        else        { nav.hide(); }
      },
    },
  });

  new ScrollSpy(document.body, {
    target: '#faq-navigator',
    offset: 70
  });
  var nav = new Collapse(document.getElementById('faq-navigator'), {
    toggle: false,
  });
});

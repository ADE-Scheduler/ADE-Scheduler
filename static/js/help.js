import Vue from 'vue';
import { Collapse } from 'bootstrap';
import './base.js';
import '../css/help.css';

var nav = {};
var vm = new Vue({
    el: '#app',
    data: {
        navBtn: false,
    },
    delimiters: ['[[',']]'],

    methods: {
        scroll: function(e, dest) {
            window.location.hash = dest;
            window.scrollBy(0, -70);

            if (window.innerWidth < 767.98) {
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


document.addEventListener('DOMContentLoaded', function() {
    nav = new Collapse(document.getElementById('faq-navigator'), {
        toggle: false,
    });
});

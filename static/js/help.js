import Vue from 'vue';
import { Collapse, ScrollSpy } from 'bootstrap';
import './base.js';
import '../css/help.css';


document.addEventListener('DOMContentLoaded', function() {
    var vm = new Vue({
        el: '#app',
        data: {
            navBtn: false,
        },
        delimiters: ['[[',']]'],

        methods: {
            scroll: function(id) {
                document.getElementById(id).scrollIntoView();
                if (!((window.innerHeight + window.scrollY) >= document.body.offsetHeight)) {
                    window.scrollBy(0, -70);
                }
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

    var scrollSpy = new ScrollSpy(document.body, {
        target: '#faq-navigator',
        offset: 100
    });
    var nav = new Collapse(document.getElementById('faq-navigator'), {
        toggle: false,
    });
});

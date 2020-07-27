import Vue from 'vue';
import '../css/base.css'
// import 'bootstrap/dist/css/bootstrap.min.css';

export default {
    0: Vue.directive('focus', {
        inserted: function (el) {
            el.focus();
        }
    }),

    1: new Vue({
        el: '#app-base',
        delimiters: ['[[',']]'],
        data: {
            currentPath: window.location.pathname,
        },
        methods: {
            localeSelector: function(e, locale) {
                window.location.href = Flask.url_for('set_locale', {'locale': locale}) + '?next=' + window.location.pathname;
            },
        },
    }),

    2: document.addEventListener('DOMContentLoaded', function() {
        document.querySelector('[data-toggle="offcanvas"]').addEventListener('click', function () {
            document.querySelector('.offcanvas-collapse').classList.toggle('open')
        })
    }),
}

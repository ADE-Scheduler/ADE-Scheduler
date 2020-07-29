import Vue from 'vue';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../css/base.css'

Vue.directive('focus', {
    inserted: function (el) {
        el.focus();
    }
});

export default document.addEventListener('DOMContentLoaded', function() {
    new Vue({
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
    });

    document.querySelector('[data-toggle="offcanvas"]').addEventListener('click', function () {
        document.querySelector('.offcanvas-collapse').classList.toggle('open')
    });
});

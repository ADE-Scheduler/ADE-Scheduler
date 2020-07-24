Vue.directive('focus', {
    inserted: function (el) {
        el.focus()
    }
});

var vmBase = new Vue({
    el: '#app-base',
    delimiters: ['[[',']]'],
    data: {
        currentPath: window.location.pathname,
        language: 'English',
    },
    methods: {
        languageSelector: function(e) {

        },
    },
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('[data-toggle="offcanvas"]').addEventListener('click', function () {
        document.querySelector('.offcanvas-collapse').classList.toggle('open')
    })
});

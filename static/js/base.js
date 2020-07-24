Vue.directive('focus', {
    inserted: function (el) {
        el.focus()
    }
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('[data-toggle="offcanvas"]').addEventListener('click', function () {
        document.querySelector('.offcanvas-collapse').classList.toggle('open')
    })
});

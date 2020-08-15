import '../base.js';
import '../../css/security/change_password.css';


document.addEventListener('DOMContentLoaded', function() {
    const valid_pwd = document.getElementById('new_password_confirm');
    const       pwd = document.getElementById('new_password');
    const      form = document.getElementById('change_password_form');

    valid_pwd.addEventListener("input", validityCheck);
          pwd.addEventListener("input", validityCheck);

    function validityCheck() {
        if (valid_pwd.value === pwd.value ) {
            if (form.classList.contains('was-validated')) {
                valid_pwd.classList.add("is-valid");
                valid_pwd.classList.remove("is-invalid");
            }
            valid_pwd.setCustomValidity("");
        } else {
            if (form.classList.contains('was-validated')) {
                valid_pwd.classList.add("is-invalid");
                valid_pwd.classList.remove("is-valid");
            }
            valid_pwd.setCustomValidity("Invalid field.");
        }
    }

    (function () {
        'use strict'
        window.addEventListener('load', function () {
            form.addEventListener('submit', function (event) {
                if (form.checkValidity() === false) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        }, false)
    }());
});

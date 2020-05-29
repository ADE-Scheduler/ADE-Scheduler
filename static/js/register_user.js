const valid_pwd = document.getElementById('password_confirm');
const       pwd = document.getElementById('password');

function validityCheck() {
    if (valid_pwd.value === pwd.value ) {
        valid_pwd.classList.add("is-valid");
        valid_pwd.classList.remove("is-invalid");
        valid_pwd.setCustomValidity("");
    } else {
        valid_pwd.classList.add("is-invalid");
        valid_pwd.classList.remove("is-valid");
        valid_pwd.setCustomValidity("Invalid field.");
    }
}

(function () {
    'use strict'
    window.addEventListener('load', function () {
        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.getElementsByClassName('needs-validation')

        // Loop over them and prevent submission
        Array.prototype.filter.call(forms, function (form) {
            form.addEventListener('submit', function (event) {
                if (form.checkValidity() === false) {
                    event.preventDefault()
                    event.stopPropagation()
                }

                valid_pwd.addEventListener("input", validityCheck);
                      pwd.addEventListener("input", validityCheck);

                form.classList.add('was-validated')
            }, false)
        })
    }, false)
}());

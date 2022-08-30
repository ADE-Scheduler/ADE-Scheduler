import '../base.js';
import '../../css/security/register_user.css';

document.addEventListener('DOMContentLoaded', () => {
  const valid_pwd = document.getElementById('password_confirm');
  const pwd = document.getElementById('password');
  const email = document.getElementById('email');
  const form = document.getElementById('register-form');

  valid_pwd.addEventListener('input', validityCheck);
  pwd.addEventListener('input', validityCheck);
  email.addEventListener('input', () => {
    if (/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(email.value)) {
      // eslint-disable-line no-useless-escape
      if (form.classList.contains('was-validated')) {
        email.classList.add('is-valid');
        email.classList.remove('is-invalid');
      }
      email.setCustomValidity('');
    } else {
      if (form.classList.contains('was-validated')) {
        email.classList.add('is-invalid');
        email.classList.remove('is-valid');
      }
      email.setCustomValidity('Invalid field.');
    }
  });

  function validityCheck() {
    if (valid_pwd.value === pwd.value) {
      if (form.classList.contains('was-validated')) {
        valid_pwd.classList.add('is-valid');
        valid_pwd.classList.remove('is-invalid');
      }
      valid_pwd.setCustomValidity('');
    } else {
      if (form.classList.contains('was-validated')) {
        valid_pwd.classList.add('is-invalid');
        valid_pwd.classList.remove('is-valid');
      }
      valid_pwd.setCustomValidity('Invalid field.');
    }
  }

  (function () {
    window.addEventListener(
      'load',
      () => {
        form.addEventListener(
          'submit',
          (event) => {
            if (form.checkValidity() === false) {
              event.preventDefault();
              event.stopPropagation();
            }
            form.classList.add('was-validated');
          },
          false
        );
      },
      false
    );
  })();
});

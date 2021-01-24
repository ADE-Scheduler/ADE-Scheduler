import { Alert } from 'bootstrap';
import '../base.js';


document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.alert').forEach(function (alert) {
    new Alert(alert);
  });
});

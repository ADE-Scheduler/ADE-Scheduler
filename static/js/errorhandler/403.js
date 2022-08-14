import { Alert } from 'bootstrap';
import '../base.js';

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach((alert) => {
    new Alert(alert);
  });
});

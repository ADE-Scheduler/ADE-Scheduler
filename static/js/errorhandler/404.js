import { Alert } from 'bootstrap';
import '../base.js';


document.addEventListener('DOMContentLoaded', function() {
    var alertList = document.querySelectorAll('.alert').forEach(function (alert) {
        new Alert(alert);
    });
});

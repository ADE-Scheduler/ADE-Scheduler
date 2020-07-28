import Vue from 'vue';
import './base.js';
import '../css/classroom.css';


document.addEventListener('DOMContentLoaded', function() {
    var vm = new Vue({
        el: '#app',
        data: {
            message: 'Hello from the Classrooms page ! :-)'
        },
        delimiters: ['[[',']]'],
    });
});

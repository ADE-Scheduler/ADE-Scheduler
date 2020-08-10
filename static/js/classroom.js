import Vue from 'vue';
import * as VueGoogleMaps from 'vue2-google-maps';
import './base.js';
import '../css/classroom.css';


Vue.use(VueGoogleMaps, {
    load: {
        key: 'AIzaSyANRlyAxFvNqYEQ2CtwqTbJwClf9e37pGI',
        libraries: 'places',
    },
    installComponents: true,
});


document.addEventListener('DOMContentLoaded', function() {
    var vm = new Vue({
        el: '#app',
        data: {
            message: 'Hello from the Classrooms page ! :-)'
        },
        delimiters: ['[[',']]'],
    });
});

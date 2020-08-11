import Vue from 'vue';
import { Icon, latLng } from 'leaflet';
import { LMap, LTileLayer, LMarker, LTooltip } from 'vue2-leaflet';
import './base.js';
import '../css/classroom.css';
import 'leaflet/dist/leaflet.css';
const axios = require('axios');


delete Icon.Default.prototype._getIconUrl;
Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});


document.addEventListener('DOMContentLoaded', function() {
    var vm = new Vue({
        el: '#app',
        delimiters: ['[[',']]'],
        components: { LMap, LTileLayer, LMarker, LTooltip },
        data: {
            computing: false,
            error: false,
            url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            center: latLng(50.6681, 4.6118),
            zoom: 15,
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
            classrooms: [],
            nameSearch: '',
            codeSearch: '',
            addressSearch: '',
        },

        methods: {
            fetchData: function() {
                this.computing = true;
                axios({
                    method: 'GET',
                    url: Flask.url_for('classroom.get_data'),
                })
                .then(resp => {
                    this.classrooms = resp.data.classrooms;
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
        },
        computed: {
            opacity: function() {
                return {'opacity': this.computing ? '0.2':'1'}
            },
            classroomsFiltered: function () {
                let res = this.classrooms
                    .filter(c => !(c.name.toLowerCase().replace(/[^a-z0-9]/gi, '').indexOf(this.nameSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')) === -1))
                    .filter(c => !(c.code.toLowerCase().replace(/[^a-z0-9]/gi, '').indexOf(this.codeSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')) === -1))
                    .filter(c => !(c.address.toLowerCase().replace(/[^a-z0-9]/gi, '').indexOf(this.addressSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')) === -1));
                return res;
            }
        },
        created:  function () {
            this.fetchData();
        },
    });
});

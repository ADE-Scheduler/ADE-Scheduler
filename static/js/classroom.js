import Vue from 'vue';
import { Icon, latLng } from 'leaflet';
import { LMap, LTileLayer, LMarker, LTooltip } from 'vue2-leaflet';
import './base.js';
import '../css/classroom.css';
import 'leaflet/dist/leaflet.css';


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
            url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            center: latLng(50.6681, 4.6118),
            zoom: 15,
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
            classrooms: [
                {
                    'name': 'BARB 00 (GPLO-EPL)',
                    'code': 'BARB00',
                    'address': 'Place Sainte Barbe 1, 1348 Louvain-la-Neuve',
                    'coords': [50.6681, 4.6118]
                },
                {
                    'name': 'A.10 SCES',
                    'code': 'A10',
                    'address': 'Place des Sciences 2, 1348 Louvain-la-Neuve',
                    'coords': [50.6684, 4.6113]
                }
            ],
            nameSearch: '',
            codeSearch: '',
            addressSearch: '',
        },
    });
});

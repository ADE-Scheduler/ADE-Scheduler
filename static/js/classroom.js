/* global Flask */

import Vue from 'vue';
import L from 'leaflet';
import { LMap, LTileLayer } from 'vue2-leaflet';
import 'overlapping-marker-spiderfier-leaflet/dist/oms';
import { Modal, Tooltip } from 'bootstrap';
import Spinner from '../../components/Spinner.vue';
import FullCalendar from '@fullcalendar/vue';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import frLocale from '@fullcalendar/core/locales/fr';
import './base.js';
import '../css/classroom.css';
import 'leaflet/dist/leaflet.css';
const axios = require('axios');

const uclWeeksNo = {
  '2019': [0, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, -3, -3],
  '2020': [-3, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, -3, -3],
  '2021': [0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, -3, -3, 0],
};

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});


document.addEventListener('DOMContentLoaded', function() {
  var oms;
  var isTouchDevice = !!('ontouchstart' in window || navigator.maxTouchPoints);
  var vm = new Vue({
    el: '#app',
    delimiters: ['[[',']]'],
    components: { LMap, LTileLayer, FullCalendar, 'spinner': Spinner },
    data: function() {
      return {
        computing: false,
        error: false,
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        // url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png',
        center: L.latLng(50.6681, 4.6118),
        zoom: 15,
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
        classrooms: [],
        nameSearch: '',
        codeSearch: '',
        addressSearch: '',
        calendarOptions: {
          plugins: [ dayGridPlugin, timeGridPlugin ],
          locales: [ frLocale ],
          locale: document.getElementById('current-locale').innerText.trim(),

          height: 'auto',
          slotMinTime: '08:00:00',
          slotMaxTime: '21:00:00',
          editable: false,
          droppable: false,
          allDaySlot: false,
          navLinks: true,
          initialView: 'dayGridMonth',
          windowResize: function (arg) {
            if (document.body.clientWidth > 550) {
              vm.calendarOptions.headerToolbar.right = 'dayGridMonth,timeGridWeek';
              vm.calendarOptions.headerToolbar.center = 'title';
              if (arg.view.type === 'timeGridDay') { this.changeView('timeGridWeek'); }
            } else {
              vm.calendarOptions.headerToolbar.right = 'dayGridMonth,timeGridDay';
              vm.calendarOptions.headerToolbar.center = '';
              if (arg.view.type === 'timeGridWeek') { this.changeView('timeGridDay'); }
            }
          },

          // Week display
          firstDay: 1,
          weekNumbers: true,
          weekNumberContent: function (arg) {
          // Get week number & year
          // From: https://stackoverflow.com/a/6117889
            let d = new Date(Date.UTC(arg.date.getFullYear(), arg.date.getMonth(), arg.date.getDate()));
            d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
            let yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
            let weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7);
            let year = d.getUTCFullYear();
            let num;
            try {
              num = uclWeeksNo[year][weekNo-1];
            } catch(e) {
              num = 0;
            }

            let span = document.createElement('span');
            if (num > 0) {
              span.innerText = `S${num}`;
            } else {
              switch (num) {
              case -1:
                span.innerText = document.getElementById('current-locale').innerText.trim() === 'EN' ? 'Easter':'Pâques';
                break;
              case -2:
                span.innerText = document.getElementById('current-locale').innerText.trim() === 'EN' ? 'Break':'Congé';
                break;
              case -3:
                span.innerText = 'Blocus';
                break;
              default:
                span.innerText = '-';
              }
            }
            return {domNodes: [span]};
          },

          // Header bar
          headerToolbar: {
            left: 'prev,next today',
            center: document.body.clientWidth > 550 ? 'title':'',
            right: document.body.clientWidth > 550 ? 'dayGridMonth,timeGridWeek':'dayGridMonth,timeGridDay'
          },

          // Events
          events: [],
          eventTextColor: 'white',
          eventDisplay: 'block',
          eventDidMount: function (arg) {
            let description, location;
            if (!arg.event.extendedProps.description)   description = 'No description';
            else                                        description = arg.event.extendedProps.description;
            if (!arg.event.extendedProps.location)      location = 'No location';
            else                                        location = arg.event.extendedProps.location;
            new Tooltip(arg.el, {
              container: 'body',
              title: description + '\n' + location,
              sanitize: false,
              template: `
                            <div class="tooltip" role="tooltip">
                                <div class="tooltip-arrow"></div>
                                <div class="tooltip-inner" style="background-color:${arg.event.backgroundColor}"></div>
                            </div>`,
              placement: 'auto',
            });
          },
        },
        modalTitle: '',
        markers: [],
      };
    },
    computed: {
      classroomsFiltered: function () {
        return this.classrooms
          .filter(c => !(c.name.toLowerCase().replace(/[^a-z0-9]/gi, '').indexOf(this.nameSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')) === -1))
          .filter(c => !(c.code.toLowerCase().replace(/[^a-z0-9]/gi, '').indexOf(this.codeSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')) === -1))
          .filter(c => !(c.address.toLowerCase().replace(/[^a-z0-9]/gi, '').indexOf(this.addressSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')) === -1));
      },
    },
    watch: {
      classroomsFiltered: function () {
        let map = this.$refs.map.mapObject;

        // Remove current markers
        this.markers.forEach(marker => {
          map.removeLayer(marker);
          oms.removeMarker(marker);
        });

        // Add new markers
        this.classroomsFiltered
          .filter(item => item.latitude !== null && item.longitude !== null)
          .forEach(item => {
            let marker = L.marker(L.latLng(item.latitude, item.longitude)).addTo(map);
            if (isTouchDevice) {
              marker.bindTooltip(item.name);
            } else {
              marker.on('mouseover', function(e) {
                let count = oms.getMarkers().filter(item => {
                  let latlng = item.getLatLng();
                  return latlng.lat === e.latlng.lat && latlng.lng === e.latlng.lng;
                }).length;

                if (count > 1) {
                  let toolTip = document.getElementById('current-locale').innerText.trim() === 'EN' ? `${count} classrooms to show (click to expand)`:`${count} locaux à montrer (cliquer pour étendre)`;
                  marker.bindTooltip(toolTip).openTooltip();
                } else {
                  marker.bindTooltip(item.name).openTooltip();
                }
              });
            }
            oms.addMarker(marker);
            this.markers.push(marker);
          });
      }
    },
    created:  function () {
      this.fetchData();
    },
    mounted: function() {
      this.$nextTick(() => {
        this.$refs.map.mapObject.addControl(new L.Control.Fullscreen());
        oms = new window.OverlappingMarkerSpiderfier(this.$refs.map.mapObject, {
          keepSpiderfied: isTouchDevice,
        });
      });
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
          .catch(() => {
            this.error = true;
          })
          .then(() => {
            this.computing = false;
          });
      },
      getOccupation: function(classroom_id) {
        this.computing = true;
        axios({
          method: 'GET',
          url: Flask.url_for('classroom.get_occupation', {id: classroom_id}),
        })
          .then(resp => {
            this.calendarOptions.events = resp.data.events;
            this.modalTitle = name;
            calendarModal.show();
            document.getElementById('calendarModal').addEventListener('shown.bs.modal', () => {
              let api = this.$refs.calendar.getApi();
              api.next();
              api.prev();
            });
          })
          .catch(() => {
            this.error = true;
          })
          .then(() => {
            this.computing = false;
          });
      },
    }
  });

  var calendarModal = new Modal(document.getElementById('calendarModal'));
});

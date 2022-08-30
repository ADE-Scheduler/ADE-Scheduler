/* global Flask */

import Vue from 'vue';
import store from './store.js';
import L from 'leaflet';
import { LMap, LTileLayer } from 'vue2-leaflet';
import 'overlapping-marker-spiderfier-leaflet/dist/oms';
import { Modal, Tooltip } from 'bootstrap';
import FullCalendar from '@fullcalendar/vue';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import frLocale from '@fullcalendar/core/locales/fr';
import Spinner from '../../components/Spinner.vue';
import './base.js';
import '../css/classroom.css';
import 'leaflet/dist/leaflet.css';

const axios = require('axios');

const uclWeeksNo = {
  2019: [
    0, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, -3, -3,
  ],
  2020: [
    -3, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, -3, -3,
  ],
  2021: [
    0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
    12, 13, 14, -3, -3, 0,
  ],
  2022: [
    0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
    12, 13, 14, -3, -3, 0,
  ],
};

Date.prototype.getWeekNumber = function () {
  const d = new Date(
    Date.UTC(this.getFullYear(), this.getMonth(), this.getDate())
  );
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
};

Date.prototype.addDays = function (days) {
  const date = new Date(this.valueOf());
  date.setDate(date.getDate() + days);
  return date;
};

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

document.addEventListener('DOMContentLoaded', () => {
  let oms;
  const isTouchDevice = !!(
    'ontouchstart' in window || navigator.maxTouchPoints
  );
  var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    components: { LMap, LTileLayer, FullCalendar, spinner: Spinner },
    data() {
      return {
        computing: false,
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        // url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png',
        center: L.latLng(50.6681, 4.6118),
        zoom: 15,
        attribution:
          '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors',
        classrooms: [],
        nameSearch: '',
        codeSearch: '',
        addressSearch: '',
        calendarOptions: {
          plugins: [dayGridPlugin, timeGridPlugin],
          locales: [frLocale],
          locale: document.getElementById('current-locale').innerText.trim(),
          timeZone: 'Europe/Brussels', // Show schedule in the same TZ where classes are given
          height: 'auto',
          slotMinTime: '08:00:00',
          slotMaxTime: '21:00:00',
          editable: false,
          droppable: false,
          allDaySlot: false,
          navLinks: true,
          initialView: 'dayGridMonth',
          windowResize(arg) {
            if (document.body.clientWidth > 550) {
              vm.calendarOptions.headerToolbar.right =
                'dayGridMonth,timeGridWeek';
              vm.calendarOptions.headerToolbar.center = 'title';
              if (arg.view.type === 'timeGridDay') {
                this.changeView('timeGridWeek');
              }
            } else {
              vm.calendarOptions.headerToolbar.right =
                'dayGridMonth,timeGridDay';
              vm.calendarOptions.headerToolbar.center = '';
              if (arg.view.type === 'timeGridWeek') {
                this.changeView('timeGridDay');
              }
            }
          },

          // Week display
          firstDay: 1,
          weekNumbers: true,
          weekNumberContent(arg) {
            // Get week number & year
            // From: https://stackoverflow.com/a/6117889
            // Since FC set first day to be Sunday in some places, we shift the current day by one to be at least Monday, otherwise we get previous week number.
            const weekNo = arg.date.addDays(1).getWeekNumber();
            const year = arg.date.getUTCFullYear();
            let num;
            try {
              num = uclWeeksNo[year][weekNo - 1];
            } catch (e) {
              num = 0;
            }

            const span = document.createElement('span');
            if (num > 0) {
              span.innerText = `S${num}`;
            } else {
              switch (num) {
              case -1:
                span.innerText =
                    document
                      .getElementById('current-locale')
                      .innerText.trim() === 'EN'
                      ? 'Easter'
                      : 'Pâques';
                break;
              case -2:
                span.innerText =
                    document
                      .getElementById('current-locale')
                      .innerText.trim() === 'EN'
                      ? 'Break'
                      : 'Congé';
                break;
              case -3:
                span.innerText = 'Blocus';
                break;
              default:
                span.innerText = '-';
              }
            }
            return { domNodes: [span] };
          },

          // Header bar
          headerToolbar: {
            left: 'prev,next today',
            center: document.body.clientWidth > 550 ? 'title' : '',
            right:
              document.body.clientWidth > 550
                ? 'dayGridMonth,timeGridWeek'
                : 'dayGridMonth,timeGridDay',
          },

          // Events
          events: [],
          eventTextColor: 'white',
          eventDisplay: 'block',
          eventDidMount(arg) {
            let description;
            let location;
            if (!arg.event.extendedProps.description)
              description = 'No description';
            else description = arg.event.extendedProps.description;
            if (!arg.event.extendedProps.location) location = 'No location';
            else location = arg.event.extendedProps.location;
            new Tooltip(arg.el, {
              container: 'body',
              title: `${description}\n${location}`,
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
      classroomsFiltered() {
        return this.classrooms
          .filter(
            (c) =>
              !(
                c.name
                  .toLowerCase()
                  .replace(/[^a-z0-9]/gi, '')
                  .indexOf(
                    this.nameSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')
                  ) === -1
              )
          )
          .filter(
            (c) =>
              !(
                c.code
                  .toLowerCase()
                  .replace(/[^a-z0-9]/gi, '')
                  .indexOf(
                    this.codeSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')
                  ) === -1
              )
          )
          .filter(
            (c) =>
              !(
                c.address
                  .toLowerCase()
                  .replace(/[^a-z0-9]/gi, '')
                  .indexOf(
                    this.addressSearch.toLowerCase().replace(/[^a-z0-9]/gi, '')
                  ) === -1
              )
          );
      },
    },
    watch: {
      classroomsFiltered() {
        const map = this.$refs.map.mapObject;

        // Remove current markers
        this.markers.forEach((marker) => {
          map.removeLayer(marker);
          oms.removeMarker(marker);
        });

        // Add new markers
        this.classroomsFiltered
          .filter((item) => item.latitude !== null && item.longitude !== null)
          .forEach((item) => {
            const marker = L.marker(
              L.latLng(item.latitude, item.longitude)
            ).addTo(map);
            if (isTouchDevice) {
              marker.bindTooltip(item.name);
            } else {
              marker.on('mouseover', (e) => {
                const count = oms.getMarkers().filter((item) => {
                  const latlng = item.getLatLng();
                  return (
                    latlng.lat === e.latlng.lat && latlng.lng === e.latlng.lng
                  );
                }).length;

                if (count > 1) {
                  const toolTip =
                    document
                      .getElementById('current-locale')
                      .innerText.trim() === 'EN'
                      ? `${count} classrooms to show (click to expand)`
                      : `${count} locaux à montrer (cliquer pour étendre)`;
                  marker.bindTooltip(toolTip).openTooltip();
                } else {
                  marker.bindTooltip(item.name).openTooltip();
                }
              });
            }
            oms.addMarker(marker);
            this.markers.push(marker);
          });
      },
    },
    created() {
      this.fetchData();
    },
    mounted() {
      this.$nextTick(() => {
        this.$refs.map.mapObject.addControl(new L.Control.Fullscreen());
        oms = new window.OverlappingMarkerSpiderfier(this.$refs.map.mapObject, {
          keepSpiderfied: isTouchDevice,
        });
      });
    },

    methods: {
      fetchData() {
        this.computing = true;
        axios({
          method: 'GET',
          url: Flask.url_for('classroom.get_data'),
        })
          .then((resp) => {
            this.classrooms = resp.data.classrooms;
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      getOccupation(classroom_id) {
        this.computing = true;
        axios({
          method: 'GET',
          url: Flask.url_for('classroom.get_occupation', { id: classroom_id }),
        })
          .then((resp) => {
            this.calendarOptions.events = resp.data.events;
            this.modalTitle = name;
            calendarModal.show();
            document
              .getElementById('calendarModal')
              .addEventListener('shown.bs.modal', () => {
                const api = this.$refs.calendar.getApi();
                api.next();
                api.prev();
              });
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
    },
  });

  var calendarModal = new Modal(document.getElementById('calendarModal'));
});

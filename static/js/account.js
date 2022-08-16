/* global Flask */

import Vue from 'vue';
import VSwatches from 'vue-swatches';
import { Modal } from 'bootstrap';
import store from './store.js';
import Spinner from '../../components/Spinner.vue';
import AlertToast from '../../components/AlertToast.vue';
import './base.js';
import 'vue-swatches/dist/vue-swatches.css';
import '../css/account.css';

const axios = require('axios');

document.addEventListener('DOMContentLoaded', () => {
  new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    components: { VSwatches, spinner: Spinner, alerttoast: AlertToast },
    data() {
      return {
        projectId: [],
        schedules: [],
        externalCalendars: [],
        currentSchedule: {},
        labelBackup: '',
        computing: true,
        unsaved: true,
        autoSave: false,
        isEditing: false,
        externalCalendarForm: {
          code: '',
          name: '',
          url: '',
        },
      };
    },
    created() {
      this.fetchData();
    },
    methods: {
      fetchData() {
        this.computing = true;
        axios({
          method: 'GET',
          url: Flask.url_for('account.get_data'),
        })
          .then((resp) => {
            this.externalCalendars = resp.data.external_calendars;
            this.projectId = resp.data.project_id;
            this.unsaved = resp.data.unsaved;
            this.schedules = resp.data.schedules;
            this.currentSchedule = resp.data.current_schedule;
            this.labelBackup = this.currentSchedule.label;
            this.autoSave = resp.data.autosave;
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      changeAutoSave() {
        this.computing = true;
        axios({
          method: 'POST',
          url: Flask.url_for('account.autosave'),
          header: { 'Content-Type': 'application/json' },
          data: { autosave: this.autoSave },
        })
          .then(() => {})
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      loadSchedule(e, id) {
        this.request = function () {
          this.computing = true;
          axios({
            method: 'GET',
            url: Flask.url_for('account.load_schedule', { id }),
          })
            .then((resp) => {
              this.unsaved = resp.data.unsaved;
              this.currentSchedule = resp.data.current_schedule;
              this.labelBackup = this.currentSchedule.label;
            })
            .catch((err) => {
              store.error(err.response.data);
            })
            .then(() => {
              this.computing = false;
            });
        };

        if (this.unsaved && this.currentSchedule.id != id) {
          warningModal.show();
        } else {
          this.request();
        }
      },
      viewSchedule(e, id) {
        // ...
        this.request = function () {
          if (id == null) {
            id = -1;
          }
          this.computing = true;
          axios({
            method: 'GET',
            url: Flask.url_for('account.load_schedule', { id }),
          })
            .then(() => {
              window.location.href = Flask.url_for('calendar.index');
            })
            .catch((err) => {
              store.error(err.response.data);
            })
            .then(() => {
              this.computing = false;
            });
        };

        if (this.unsaved && this.currentSchedule.id != id) {
          warningModal.show();
        } else {
          this.request();
        }
      },
      deleteSchedule(e, id) {
        if (id == null) {
          id = -1;
        }
        this.computing = true;
        axios({
          method: 'DELETE',
          url: Flask.url_for('account.delete_schedule', { id }),
        })
          .then((resp) => {
            const index = this.schedules.findIndex((s) => s.id === id);
            if (index > -1) {
              this.schedules.splice(index, 1);
            }
            this.currentSchedule = resp.data.current_schedule;
            this.labelBackup = this.currentSchedule.label;
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      deleteExternalCalendar(e, id) {
        if (id == null) {
          id = -1;
        }
        this.computing = true;
        axios({
          method: 'DELETE',
          url: Flask.url_for('account.delete_external_calendar', { id }),
        })
          .then(() => {
            location.reload();
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      updateLabel(id) {
        // ...
        this.computing = true;
        if (id == null) {
          id = -1;
        }
        axios({
          method: 'PATCH',
          url: Flask.url_for('account.update_label', { id }),
          header: { 'Content-Type': 'applacation/json' },
          data: { label: this.currentSchedule.label },
        })
          .then(() => {
            this.isEditing = false;
            const schedule = this.schedules.find((s) => s.id === id);
            if (schedule) {
              schedule.label = this.currentSchedule.label;
              this.labelBackup = schedule.label;
            }
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      save() {
        this.computing = true;
        axios({
          method: 'POST',
          url: Flask.url_for('account.save'),
          header: { 'Content-Type': 'applacation/json' },
          data: this.currentSchedule,
        })
          .then((resp) => {
            if (
              this.schedules.findIndex(
                (s) => s.id === resp.data.saved_schedule.id
              ) < 0
            ) {
              this.schedules.push(resp.data.saved_schedule);
              this.currentSchedule.id = resp.data.saved_schedule.id;
            }
            this.unsaved = resp.data.unsaved;
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      addExternalCalendar() {
        const form = {
          code: this.externalCalendarForm.code,
          name: this.externalCalendarForm.name,
          url: this.externalCalendarForm.url,
          description: this.externalCalendarForm.description,
        };
        this.computing = true;
        axios({
          method: 'POST',
          url: Flask.url_for('account.add_external_calendar'),
          data: form,
          header: { 'Content-Type': 'application/json' },
        })
          .then((resp) => {
            store.success(resp.data);
            externalCalendarModal.hide();
            location.reload();
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      showExternalCalendarModal: () => {
        externalCalendarModal.show();
      },
      warningContinue() {
        this.request();
      },
      cancelSubmit: () => {},
      request: () => {},
    },
  });

  var warningModal = new Modal(document.getElementById('warningModal'));
  var externalCalendarModal = new Modal(document.getElementById('externalCalendarModal'));
});

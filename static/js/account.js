/* global Flask */

import Vue from 'vue';
import store from './store.js';
import Spinner from '../../components/Spinner.vue';
import VSwatches from 'vue-swatches';
import { Modal } from 'bootstrap';
import './base.js';
import 'vue-swatches/dist/vue-swatches.css';
import '../css/account.css';
const axios = require('axios');


document.addEventListener('DOMContentLoaded', function() {
  new Vue({
    el: '#app',
    delimiters: ['[[',']]'],
    components: { VSwatches, 'spinner': Spinner },
    data: function() {
      return {
        projectId: [],
        schedules: [],
        externalActivities: [],
        currentSchedule: {},
        labelBackup: '',
        computing: true,
        unsaved: true,
        autoSave: false,
        isEditing: false,
      };
    },
    created: function() {
      this.fetchData();
    },
    methods: {
      fetchData: function() {
        this.computing = true;
        axios({
          method: 'GET',
          url: Flask.url_for('account.get_data'),
        })
          .then(resp => {
            this.externalActivities = resp.data.external_activities; 
            this.projectId = resp.data.project_id;
            this.unsaved = resp.data.unsaved;
            this.schedules = resp.data.schedules;
            this.currentSchedule = resp.data.current_schedule;
            this.labelBackup = this.currentSchedule.label;
            this.autoSave = resp.data.autosave;
          })
          .catch(err => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      changeAutoSave: function () {
        this.computing = true;
        axios({
          method: 'POST',
          url: Flask.url_for('account.autosave'),
          header: {'Content-Type': 'application/json'},
          data: { autosave: this.autoSave },
        })
          .then(() => {})
          .catch(err => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      loadSchedule: function(e, id) {
        this.request = function() {
          this.computing = true;
          axios({
            method: 'GET',
            url: Flask.url_for('account.load_schedule', {'id': id}),
          })
            .then(resp => {
              this.unsaved = resp.data.unsaved;
              this.currentSchedule = resp.data.current_schedule;
              this.labelBackup = this.currentSchedule.label;
            })
            .catch(err => {
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
      viewSchedule: function(e, id) {
        // ...
        this.request = function() {
          if (id == null) { id = -1; }
          this.computing = true;
          axios({
            method: 'GET',
            url: Flask.url_for('account.load_schedule', {'id': id}),
          })
            .then(() => {
              window.location.href = Flask.url_for('calendar.index');
            })
            .catch(err => {
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
      deleteSchedule: function(e, id) {
        if (id == null) { id = -1; }
        this.computing = true;
        axios({
          method: 'DELETE',
          url: Flask.url_for('account.delete_schedule', {'id': id}),
        })
          .then(resp => {
            let index = this.schedules.findIndex(s => s.id === id);
            if (index > -1) {
              this.schedules.splice(index, 1);
            }
            this.currentSchedule = resp.data.current_schedule;
            this.labelBackup = this.currentSchedule.label;
          })
          .catch(err => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      deleteExternalActivity: function(e, id) {
        if (id == null) { id = -1; }
        this.computing = true;
        axios({
          method: 'DELETE',
          url: Flask.url_for('account.delete_external_activity', {'id': id}),
        })
          .then(resp => {
            //TODO : delete external activity
            let index = this.schedules.findIndex(s => s.id === id);
            if (index > -1) {
              this.schedules.splice(index, 1);
            }
            this.currentSchedule = resp.data.current_schedule;
            this.labelBackup = this.currentSchedule.label;
          })
          .catch(err => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      updateLabel: function(id) {
        // ...
        this.computing = true;
        if (id == null) { id = -1; }
        axios({
          method: 'PATCH',
          url: Flask.url_for('account.update_label', {'id': id}),
          header: {'Content-Type': 'applacation/json'},
          data: {'label': this.currentSchedule.label},
        })
          .then(() => {
            this.isEditing = false;
            let schedule = this.schedules.find(s => s.id === id);
            if (schedule) {
              schedule.label = this.currentSchedule.label;
              this.labelBackup = schedule.label;
            }
          })
          .catch(err => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      save: function() {
        this.computing = true;
        axios({
          method: 'POST',
          url: Flask.url_for('account.save'),
          header: {'Content-Type': 'applacation/json'},
          data: this.currentSchedule,
        })
          .then(resp => {
            if (this.schedules.findIndex(s => s.id === resp.data.saved_schedule.id) < 0) {
              this.schedules.push(resp.data.saved_schedule);
              this.currentSchedule.id = resp.data.saved_schedule.id;
            }
            this.unsaved = resp.data.unsaved;
          })
          .catch(err => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
      warningContinue: function() {this.request();},
      request: function() {},
    },
  });

  var warningModal = new Modal(document.getElementById('warningModal'));
});

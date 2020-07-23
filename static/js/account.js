
var warningModal = {};
var vm = new Vue({
    el: '#app',
    components: {
        VSwatches: window['vue-swatches']
    },
    data: {
        projectId: [],
        schedules: [],
        current_schedule: {},
        computing: true,
        unsaved: true,
        error: false,
        isEditing: false,
    },
    delimiters: ['[[',']]'],
    directives: {
        focus: {
            inserted: function(el) {
                el.focus();
            },
        },
    },
    methods: {
        fetchData: function(e) {
            this.computing = true;
            axios({
                method: 'GET',
                url: Flask.url_for('account.get_data'),
            })
            .then(resp => {
                this.projectId = resp.data.project_id;
                this.unsaved = resp.data.unsaved;
                this.schedules = resp.data.schedules;
                this.current_schedule = resp.data.current_schedule;
            })
            .catch(err => {
                this.error = true;
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
                    this.current_schedule = resp.data.current_schedule;
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            }

            if (this.unsaved && this.current_schedule.id != id) {
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
                .then(resp => {
                    window.location.href = Flask.url_for('calendar.schedule_viewer');
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            }

            if (this.unsaved && this.current_schedule.id != id) {
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
                this.current_schedule = resp.data.current_schedule
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                this.computing = false;
            });
        },
        updateLabel: function(e, id) {
            // ...
            if (this.isEditing) {
                this.computing = true;
                if (id == null) { id = -1; }
                axios({
                    method: 'PATCH',
                    url: Flask.url_for('account.update_label', {'id': id}),
                    header: {'Content-Type': 'applacation/json'},
                    data: {'label': this.current_schedule.label},
                })
                .then(resp => {
                    this.isEditing = false;
                    let schedule = this.schedules.find(s => s.id === id);
                    if (schedule) {
                        schedule.label = this.current_schedule.label;
                    }
                })
                .catch(err => {
                    this.error = true;
                    console.log(err);
                })
                .then(() => {
                    this.computing = false;
                });
            } else {
                this.isEditing = true;
            }
        },
        save: function(e) {
            this.computing = true;
            axios({
                method: 'POST',
                url: Flask.url_for('account.save'),
                header: {'Content-Type': 'applacation/json'},
                data: this.current_schedule,
            })
            .then(resp => {
                if (this.schedules.findIndex(s => s.id === resp.data.saved_schedule.id) < 0) {
                    this.schedules.push(resp.data.saved_schedule);
                    this.current_schedule.id = resp.data.saved_schedule.id;
                }
                this.unsaved = resp.data.unsaved;
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                this.computing = false;
            });
        },
        warningContinue: function() {this.request()},
        request: function() {},
    },
    computed: {
        opacity: function() {
            return {'opacity': this.computing ? '0.2':'1'}
        },
    },
    created: function() {
        this.fetchData();
    },
});


document.addEventListener('DOMContentLoaded', function() {
    warningModal = new bootstrap.Modal(document.getElementById('warningModal'));
});

var popoverList = [];
var eventModal = {};
var calendar = {};
var vm = new Vue({
    el: '#app',
    data: {
        codes: [],
        events: [],
        calendar: {},
        computing: true,
        error: false,
        saveSuccess: false,
        code: '',
        eventForm: {
            name: '',
            location: '',
            description: '',
            beginDay: '',
            endDay: '',
            beginHour: '',
            endHour: '',
            freq: [],
            beginRecurrDay: '',
            endRecurrDay: '',
            recurring: false,
        }
    },
    delimiters: ['[[',']]'],

    methods: {
        fetchData: function(e) {
            this.computing = true;
            axios({
                method: 'GET',
                url: Flask.url_for('calendar.get_data'),
            })
            .then(resp => {
                this.codes = resp.data.codes;
                this.events = resp.data.events;
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                this.computing = false;
            });
        },
        clear: function(e) {
            this.computing = true;
            axios({
                method: 'DELETE',
                url: Flask.url_for('calendar.clear'),
            })
            .then(resp => {
                this.events = [];
                this.codes = [];
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                this.computing = false;
            });
        },
        compute: function(e) {
            this.computing = true;
            axios({
                method: 'GET',
                url: Flask.url_for('calendar.compute'),
            })
            .then(resp => {
                console.log('Schedule computed successfuly !');
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                this.computing = false;
            });
        },
        save: function(e) {
            this.computing = true;
            axios({
                method: 'POST',
                url: Flask.url_for('calendar.save'),
            })
            .then(resp => {
                this.saveSuccess = true;
            })
            .catch(err => {
                if (err.response.status === 401) {
                    window.location.href = Flask.url_for('security.login');
                } else {
                    this.error = true;
                }
            })
            .then(() => {
                this.computing = false;
            });
        },
        addCode: function(e) {
            this.computing = true;
            axios({
                method: 'PATCH',
                url: Flask.url_for('calendar.add_code', {'code': this.code}),
            })
            .then(resp => {
                this.codes = this.codes.concat(resp.data.codes);
                this.events = resp.data.events;
                this.code = '';
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                this.computing = false;
            });
        },
        removeCode: function(e, code) {
            this.computing = true;
            axios({
                method: 'PATCH',
                url: Flask.url_for('calendar.remove_code', {'code': code}),
            })
            .then(resp => {
                this.codes.splice(this.codes.indexOf(code), 1);
                this.events = resp.data.events;
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                this.computing = false;
            });
        },
        addEvent: function(e) {
            let evt = {
                name: this.eventForm.name,
                location: this.eventForm.location,
                description: this.eventForm.description,
            }
            if (this.eventForm.recurring) {
                evt.begin = this.eventForm.beginRecurrDay + ' ' + this.eventForm.beginHour;
                evt.end = this.eventForm.beginRecurrDay + ' ' + this.eventForm.endHour;
                evt.end_recurr = this.eventForm.endRecurrDay + ' ' + this.eventForm.endHour;
                evt.freq = this.eventForm.freq;
            } else {
                evt.begin = this.eventForm.beginDay + ' ' + this.eventForm.beginHour;
                evt.end = this.eventForm.endDay + ' ' + this.eventForm.endHour;
            }

            computing = true;
            axios({
                method: 'POST',
                url: Flask.url_for('calendar.add_custom_event'),
                data: evt,
                header: {'Content-Type': 'application/json'},
            })
            .then(resp => {
                vm.events.push(resp.data.event);
                e.target.reset();
                eventModal.hide();
            })
            .catch(err => {
                this.error = true;
            })
            .then(() => {
                computing = false;
            });
        },
        checkMinDay: function(e) {
            if (this.eventForm.beginDay > this.eventForm.endDay || !this.eventForm.endDay) {
                this.eventForm.endDay = this.eventForm.beginDay;
            }
        },
        checkMaxDay: function(e) {
            if (this.eventForm.beginDay > this.eventForm.endDay || !this.eventForm.beginDay) {
                this.eventForm.beginDay = this.eventForm.endDay;
            }
        },
        checkMinRecurrDay: function(e) {
            if (this.eventForm.beginRecurrDay > this.eventForm.endRecurrDay || !this.eventForm.endRecurrDay) {
                this.eventForm.endRecurrDay = this.eventForm.beginRecurrDay;
            }
        },
        checkMaxRecurrDay: function(e) {
            if (this.eventForm.beginRecurrDay > this.eventForm.endRecurrDay || !this.eventForm.beginRecurrDay) {
                this.eventForm.beginRecurrDay = this.eventForm.endRecurrDay;
            }
        },
        checkMinHour: function(e) {
            if (this.eventForm.beginHour > this.eventForm.endHour || !this.eventForm.endHour) {
                this.eventForm.endHour = this.eventForm.beginHour;
            }
        },
        checkMaxHour: function(e) {
            if (this.eventForm.beginHour > this.eventForm.endHour || !this.eventForm.beginHour) {
                this.eventForm.beginHour = this.eventForm.endHour;
            }
        },
    },

    computed: {
        calendarOpacity: function() {
            return {'opacity': this.computing ? '0.2':'1'}
        },
    },

    watch: {
        events: function () {
            calendar.refetchEvents();
        },
    },

    created:  function () {
        this.fetchData();
    },
});


document.addEventListener('DOMContentLoaded', function() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="popover"]'));
    popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            container: 'body',
            trigger: 'focus',
        })
    });

    eventModal = new bootstrap.Modal(document.getElementById('eventModal'));

    calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
        height: 'auto',
        slotMinTime: '08:00:00',
        slotMaxTime: '21:00:00',
        navLinks: true, // can click day/week names to navigate views
        editable: true,
        droppable: true,
        dayMaxEventRows: false, // allow "more" link when too many events

        // Week display
        firstDay: 1,
        weekText: 'S',
        weekNumbers: true,
        weekNumberCalculation: (d) => {
            d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay()||7));
            // Get first day of year
            let yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
            // Calculate full weeks to nearest Thursday
            return weekNo = Math.ceil(( ( (d - yearStart) / 86400000) + 1)/7);
        },

        // Custom header Button
        customButtons: {
            addEvent: {
                text: '+',
                click: () => { eventModal.show(); }
            }
        },
        headerToolbar: {
            left: 'prev,next today addEvent',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },

        // Remember where the user left the calendar
        initialView: (localStorage.getItem("fcInitialView") !== null ? localStorage.getItem("fcInitialView") : 'timeGridWeek'),
        initialDate: (localStorage.getItem("fcInitialDate") !== null ? parseInt(localStorage.getItem("fcInitialDate")) : Date.now()),
        datesSet: function (arg) {
            localStorage.setItem("fcInitialView", arg.view.type);
            localStorage.setItem("fcInitialDate", arg.view.currentStart.getTime());
        },

        // Events refresher
        events: function (fetchInfo, successCallback, failureCallback) {
            successCallback(vm.events);
        },
        eventTextColor: 'white',
        eventDisplay: 'block',
    });
    calendar.render();
});

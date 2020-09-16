import Vue from 'vue';
import { Modal, Popover, Tooltip, Collapse, Dropdown } from 'bootstrap';
import FullCalendar from '@fullcalendar/vue'
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import frLocale from '@fullcalendar/core/locales/fr';
import './base.js';
import '../css/calendar.css';
const axios = require('axios');
const debounce = require('lodash/debounce');

const uclWeeksNo = {
    '2019': [0, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, -3, -3],
    '2020': [-3, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, -3, -3],
    '2021': [0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, -3, -3, 0],
};


document.addEventListener('DOMContentLoaded', function() {
    var isTouchDevice = !!('ontouchstart' in window || navigator.maxTouchPoints);
    var vm = new Vue({
        el: '#app',
        components: { FullCalendar },
        data: {
            projectId: [],
            schedules: [],
            currentProjectId: 0,
            codes: [],
            n_schedules: 0,
            selected_schedule: 0,
            computing: true,
            error: false,
            saveSuccess: !!document.getElementById('scheduleSaved'),
            code: '',
            codeSearch: [],
            unsaved: false,
            currentSchedule: {},
            codeSearchDisplay: false,
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
            },
            courseInfo: {
                code: '',
                title: '',
                summary: {},
                filtered: {},
            },
            eventInfo: {
                event: {},
                rrule: {},
            },
            navBtn: false,
            calendarOptions: {
                plugins: [ dayGridPlugin, timeGridPlugin ],
                locales: [ frLocale ],
                locale: document.getElementById('current-locale').innerText.trim(),

                height: 'auto',
                slotMinTime: '08:00:00',
                slotMaxTime: '21:00:00',
                navLinks: true, // can click day/week names to navigate views
                editable: false,
                droppable: false,
                dayMaxEventRows: false, // allow "more" link when too many events
                allDaySlot: false,

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
                customButtons: {
                    addEvent: {
                        text: '+',
                        click: () => { addEventModal.show(); }
                    }
                },
                headerToolbar: {
                    left: 'prev,next today addEvent',
                    center: document.body.clientWidth > 550 ? 'title':'',
                    right: document.body.clientWidth > 550 ? 'dayGridMonth,timeGridWeek':'dayGridMonth,timeGridDay'
                },

                // Remember where the user left the calendar
                initialView: (localStorage.getItem("fcInitialView") !== null ? localStorage.getItem("fcInitialView") : 'timeGridWeek'),
                initialDate: (localStorage.getItem("fcInitialDate") !== null ? parseInt(localStorage.getItem("fcInitialDate")) : Date.now()),
                datesSet: function (arg) {
                    localStorage.setItem("fcInitialView", arg.view.type);
                    localStorage.setItem("fcInitialDate", arg.view.currentStart.getTime());
                },
                windowResize: function (arg) {
                    if (document.body.clientWidth > 550) {
                        vm.calendarOptions.headerToolbar.right = 'dayGridMonth,timeGridWeek';
                        vm.calendarOptions.headerToolbar.center = 'title';
                        if (arg.view.type === 'timeGridDay') { this.changeView('timeGridWeek') }
                    } else {
                        vm.calendarOptions.headerToolbar.right = 'dayGridMonth,timeGridDay';
                        vm.calendarOptions.headerToolbar.center = '';
                        if (arg.view.type === 'timeGridWeek') { this.changeView('timeGridDay') }
                    }
                },

                // Events
                events: [],
                eventTextColor: 'white',
                eventDisplay: 'block',
                eventDidMount: function(arg) {
                    let evt = arg.event.toPlainObject({collapseExtendedProps: true});
                    if (!!evt.code || !isTouchDevice) {
                        let description, location;
                        if (!evt.description)   description = 'No description';
                        else                    description = evt.description;
                        if (!evt.location)      location = 'No location';
                        else                    location = evt.location;
                        arg.el.tooltip = new Tooltip(arg.el, {
                            container: 'body',
                            trigger: 'manual',
                            title: description + '\n' + location,
                            sanitize: false,
                            template: `
                                <div class="tooltip" role="tooltip">
                                    <div class="tooltip-arrow"></div>
                                    <div class="tooltip-inner" style="background-color:${evt.backgroundColor}"></div>
                                </div>`,
                            placement: 'auto',
                        });
                    }
                },
                eventMouseEnter: function(arg) {
                    if (!vm.computing && !!arg.el.tooltip) {
                        arg.el.tooltip.show();
                    }
                },
                eventMouseLeave: function(arg) {
                    if (!!arg.el.tooltip) {
                        arg.el.tooltip.hide();
                    }
                },
                eventClick: function(arg) {
                    let evt = arg.event.toPlainObject({collapseExtendedProps: true});
                    if (!evt.code) {
                        vm.eventInfo = evt;
                        vm.eventInfo.event = arg.event;
                        eventModal.show();
                    } else if (!isTouchDevice) {
                        vm.getDetails(evt.code);
                    }
                }
            },
            exportInfo: {
                url: null,
                subscriptionType: 0,
            },
            shareLink: '',
        },
        delimiters: ['[[',']]'],

        methods: {
            fetchData: function() {
                this.computing = true;
                axios({
                    method: 'GET',
                    url: Flask.url_for('calendar.get_data'),
                })
                .then(resp => {
                    this.codes = resp.data.codes;
                    this.projectId = resp.data.project_id;
                    this.currentProjectId = resp.data.current_project_id;
                    this.n_schedules = resp.data.n_schedules;
                    this.schedules = resp.data.schedules;
                    this.calendarOptions.events = resp.data.events;
                    this.unsaved = resp.data.unsaved;
                    this.currentSchedule = resp.data.current_schedule;
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
                        url: Flask.url_for('calendar.load_schedule', {'id': id}),
                    })
                    .then(resp => {
                        this.codes = resp.data.codes;
                        this.projectId = resp.data.project_id;
                        this.currentProjectId = resp.data.current_project_id;
                        this.n_schedules = resp.data.n_schedules;
                        this.schedules = resp.data.schedules;
                        this.calendarOptions.events = resp.data.events;
                        this.unsaved = resp.data.unsaved;
                        this.currentSchedule = resp.data.current_schedule;
                    })
                    .catch(err => {
                        this.error = true;
                    })
                    .then(() => {
                        this.computing = false;
                    });
                }

                if (this.unsaved && this.currentSchedule.id != id) {
                    warningModal.show();
                } else {
                    this.request();
                }
            },
            clear: function() {
                this.request = function() {
                    this.computing = true;
                    axios({
                        method: 'DELETE',
                        url: Flask.url_for('calendar.clear'),
                    })
                    .then(resp => {
                        this.calendarOptions.events = [];
                        this.n_schedules = 0;
                        this.selected_schedule = 0;
                        this.codes = [];
                        this.currentProjectId = resp.data.current_project_id;
                        this.unsaved = resp.data.unsaved;
                        this.currentSchedule = resp.data.current_schedule
                    })
                    .catch(err => {
                        this.error = true;
                    })
                    .then(() => {
                        this.computing = false;
                    });
                }
                if (this.unsaved) {
                    warningModal.show();
                } else {
                    this.request();
                }
            },
            compute: function() {
                this.computing = true;
                axios({
                    method: 'PUT',
                    url: Flask.url_for('calendar.compute'),
                })
                .then(resp => {
                    this.unsaved = resp.data.unsaved;
                    this.n_schedules = resp.data.n_schedules;
                    this.selected_schedule = resp.data.selected_schedule;
                    this.calendarOptions.events = resp.data.events;
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
            getLink: function() {
                this.computing = true;
                axios({
                    method: 'GET',
                    url: Flask.url_for('calendar.export'),
                })
                .then(resp => {
                    this.exportInfo.url = `${window.location.origin}${Flask.url_for('calendar.download')}?link=${resp.data.link}`;
                    this.shareLink = `${window.location.origin}${Flask.url_for('calendar.share')}?link=${resp.data.link}`;
                    exportModal.show();
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
            save: function() {
                this.computing = true;
                axios({
                    method: 'POST',
                    url: Flask.url_for('calendar.save'),
                })
                .then(resp => {
                    this.saveSuccess = true;
                    this.unsaved = resp.data.unsaved;
                    this.schedules = resp.data.schedules;
                })
                .catch(err => {
                    if (err.response.status === 401) {
                        window.location.href = `${Flask.url_for('security.login')}?next=${Flask.url_for('calendar.index')}%3Fsave%3DTrue`;
                    } else {
                        this.error = true;
                    }
                })
                .then(() => {
                    this.computing = false;
                });
            },
            addCode: function(e, code) {
                if (code !== undefined) {
                    this.code = code;
                }
                if (this.code !== '') {
                    this.computing = true;
                    axios({
                        method: 'PATCH',
                        url: Flask.url_for('calendar.add_code', {'code': encodeURIComponent(this.code)}),
                    })
                    .then(resp => {
                        this.codes = this.codes.concat(resp.data.codes);
                        this.calendarOptions.events = resp.data.events;
                        this.code = '';
                        this.unsaved = resp.data.unsaved;
                    })
                    .catch(err => {
                        if (err.response.status === 404) {
                            warningModal.show();
                        } else {
                            this.error = true;
                        }
                    })
                    .then(() => {
                        this.computing = false;
                    });
                }
            },
            removeCode: function(code) {
                this.computing = true;
                axios({
                    method: 'DELETE',
                    url: Flask.url_for('calendar.remove_code', {'code': encodeURIComponent(code)}),
                })
                .then(resp => {
                    this.codes.splice(this.codes.indexOf(code), 1);
                    this.calendarOptions.events = resp.data.events;
                    this.unsaved = resp.data.unsaved;
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
                    evt.end_recurrence = this.eventForm.endRecurrDay + ' ' + this.eventForm.endHour;
                    evt.freq = this.eventForm.freq;
                } else {
                    evt.begin = this.eventForm.beginDay + ' ' + this.eventForm.beginHour;
                    evt.end = this.eventForm.endDay + ' ' + this.eventForm.endHour;
                }

                this.computing = true;
                axios({
                    method: 'POST',
                    url: Flask.url_for('calendar.add_custom_event'),
                    data: evt,
                    header: {'Content-Type': 'application/json'},
                })
                .then(resp => {
                    this.calendarOptions.events.push(resp.data.event);
                    this.unsaved = resp.data.unsaved;
                    e.target.reset();
                    this.eventForm = {
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
                    };
                    addEventModal.hide();
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
            checkMinDay: function() {
                if (this.eventForm.beginDay > this.eventForm.endDay || !this.eventForm.endDay) {
                    this.eventForm.endDay = this.eventForm.beginDay;
                }
            },
            checkMaxDay: function() {
                if (this.eventForm.beginDay > this.eventForm.endDay || !this.eventForm.beginDay) {
                    this.eventForm.beginDay = this.eventForm.endDay;
                }
            },
            checkMinRecurrDay: function() {
                if (this.eventForm.beginRecurrDay > this.eventForm.endRecurrDay || !this.eventForm.endRecurrDay) {
                    this.eventForm.endRecurrDay = this.eventForm.beginRecurrDay;
                }
            },
            checkMaxRecurrDay: function() {
                if (this.eventForm.beginRecurrDay > this.eventForm.endRecurrDay || !this.eventForm.beginRecurrDay) {
                    this.eventForm.beginRecurrDay = this.eventForm.endRecurrDay;
                }
            },
            checkMinHour: function() {
                if (this.eventForm.beginHour > this.eventForm.endHour || !this.eventForm.endHour) {
                    this.eventForm.endHour = this.eventForm.beginHour;
                }
            },
            checkMaxHour: function() {
                if (this.eventForm.beginHour > this.eventForm.endHour || !this.eventForm.beginHour) {
                    this.eventForm.beginHour = this.eventForm.endHour;
                }
            },
            getDetails: function(code) {
                if (this.courseInfo.code === code) {
                    courseModal.show();
                } else {
                    this.computing = true;
                    axios({
                        method: 'GET',
                        url: Flask.url_for('calendar.get_info', {'code': encodeURIComponent(code)}),
                    })
                    .then(resp => {
                        this.courseInfo.code = code;
                        this.courseInfo.title = resp.data.title;
                        this.courseInfo.summary = resp.data.summary;

                        Object.entries(this.courseInfo.summary).forEach(([key, val]) => {
                            Vue.set(this.courseInfo.filtered, key, {});
                            Object.entries(val).forEach(([k, v]) => {
                                Vue.set(this.courseInfo.filtered[key], k, {});
                                v.forEach(item => {
                                    Vue.set(this.courseInfo.filtered[key][k], item, !resp.data.filtered[key].includes(k + ': ' + item));
                                });
                            });
                        });

                        courseModal.show();
                    })
                    .catch(err => {
                        this.error = true;
                    })
                    .then(() => {
                        this.computing = false;
                    });
                }
            },
            applyFilter: function() {
                this.computing = true;
                axios({
                    method: 'PUT',
                    url: Flask.url_for('calendar.apply_filter'),
                    data: this.courseInfo.filtered,
                    header: {'Content-Type': 'application/json'},
                })
                .then(resp => {
                    this.unsaved = resp.data.unsaved;
                    this.calendarOptions.events = resp.data.events;
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
            toggleNav: function() {
                this.navBtn = !this.navBtn;
                if (this.navBtn)    { codeMenu.show(); }
                else                { codeMenu.hide(); }
            },
            removeEvent: function(event) {
                this.computing = true;
                axios({
                    method: 'DELETE',
                    url: Flask.url_for('calendar.delete_custom_event', {'id': event.id}),
                })
                .then(resp => {
                    this.calendarOptions.events = this.calendarOptions.events.filter(item => item.id !== event.id);
                    this.unsaved = resp.data.unsaved;
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
            getEvents: function(schedule_number) {
                this.computing = true;
                axios({
                    method: 'GET',
                    url: Flask.url_for('calendar.get_events'),
                    params: { schedule_number: schedule_number },
                })
                .then(resp => {
                    this.calendarOptions.events = resp.data.events;
                    this.selected_schedule = schedule_number;
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
            updateYear: function() {
                this.computing = true;
                axios({
                    method: 'PUT',
                    url: Flask.url_for('calendar.update_poject_id', {id: this.currentProjectId}),
                })
                .then(resp => {
                    this.calendarOptions.events = resp.data.events;
                })
                .catch(err => {
                    this.error = true;
                })
                .then(() => {
                    this.computing = false;
                });
            },
            copyToClipboard: function(id) {
                let copyText = document.getElementById(id);
                copyText.select();
                copyText.setSelectionRange(0, 99999);   // for mobile
                copyText.classList.add('is-valid');
                document.execCommand('copy');
            },
            getCodeSearchResults: function() {
                if (this.code !== '') {
                    axios({
                        method: 'GET',
                        url: Flask.url_for('calendar.search_code', {'search_key': encodeURIComponent(this.code)}),
                    })
                    .then(resp => {
                        this.codeSearch = resp.data.codes;
                    })
                    .catch(err => {})
                    .then(  () => {});
                }
            },
            warningConfirmed: function() {
                this.request();
            },
            request: function() {},
        },
        computed: {
            calendarOpacity: function() {
                return {'opacity': this.computing ? '0.2':'1'}
            },
            subscriptionLink: function() {
                return this.exportInfo.url + '&choice=' + this.exportInfo.subscriptionType;
            },
        },
        watch: {
            codeSearchDisplay: function () {
                if (this.codeSearchDisplay) {
                    codeDropdown.show();
                } else {
                    codeDropdown.hide();
                }
            },
            code: function(newCode) {
                if (newCode === '') {
                    this.codeSearch = [];
                }
                this.debouncedCodeSearchResults();
            },
        },
        created:  function () {
            this.fetchData();
            this.debouncedCodeSearchResults = debounce(this.getCodeSearchResults, 200);
        },
    });

    var popoverList = [].slice.call(document.querySelectorAll('[data-toggle="popover"]')).map(function (popoverTriggerEl) {
        return new Popover(popoverTriggerEl, {
            container: 'body',
            trigger: 'focus',
        })
    });
    var codeDropdown = new Dropdown(document.getElementById('input-enter-code'));
    var addEventModal = new Modal(document.getElementById('addEventModal'));
    var eventModal = new Modal(document.getElementById('eventModal'));
    var exportModal = new Modal(document.getElementById('exportModal'));
    var courseModal = new Modal(document.getElementById('courseModal'));
    var warningModal = new Modal(document.getElementById('warningModal'));
    var codeMenu = new Collapse(document.getElementById('sidebarMenu'), {
        toggle: false,
    });
    var warningModal = new Modal(document.getElementById('warningModal'));
});

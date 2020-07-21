var calendar = new Object();
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
    },
    delimiters: ['[[',']]'],

    methods: {
        fetch: function(e) {
            this.computing = false;
            axios({
                method: 'GET',
                url: Flask.url_for('calendar.get_data'),
            })
            .then(resp => {
                this.codes = resp.data.codes;
                this.events = resp.data.events;
            })
            .catch(err => {
                console.log('An error has occurred');
                console.log(data);
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
                spinner.run = false;
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
                $('#save-success-alert').show();
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
        this.fetch();
    },
});

window.onload = () => {
    $(function () {
        $('[data-toggle="popover"]').popover({
            container: 'body',
            trigger: 'focus'
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
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
                click: () => { $('#eventModal').modal('show'); }
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

function addEventButton(e) {
    // Prevent form submission
    e.preventDefault();

    // Assemble the event
    let evt = {
        name: $('#event-name').val(),
        location: $('#event-location').val(),
        description: $('#event-description').val(),
    }
    if ($('#switch-repetition').is(':checked')) {
        evt.begin = $('#recurring-start').val() + ' ' + $('#time-start').val();
        evt.end = $('#recurring-start').val() + ' ' + $('#time-end').val();
        evt.end_recurr = $('#recurring-end').val() + ' ' + $('#time-end').val();
        evt.freq = $('#recurring-days').val();
    } else {
        evt.begin = $('#date-start').val() + ' ' +$('#time-start').val();
        evt.end = $('#date-end').val() + ' ' +$('#time-end').val();
    }

    // Send the request to the server
    spinner.run = true;
    $.ajax({
        url: Flask.url_for('calendar.add_custom_event'),
        type: 'POST',
        data: JSON.stringify(evt),
        contentType: 'application/json;charset=UTF-8',
        success: (data) => {
            vm.events.push(data.event);
            calendar.refetchEvents();

            // Clear the form
            e.target.reset();
            $('#eventModal').modal('hide');
        },
        error: (data) => {
            $('#error-alert').show()
        },
        complete: () => {
            spinner.run = false;
        },
    });
 };

$('#switch-repetition').on('change', (e) => {
    if (e.target.checked) {
        $('#recurring-start').attr('required', true);
        $('#recurring-end').attr('required', true);
        $('#recurring-days').attr('required', true);
        $('#date-start').attr('required', false);
        $('#date-end').attr('required', false);

        $('#recurring-start').attr('disabled', false);
        $('#recurring-end').attr('disabled', false);
        $('#recurring-days').attr('disabled', false);
        $('#date-start').attr('disabled', true);
        $('#date-end').attr('disabled', true);
    } else {
        $('#recurring-start').attr('required',false);
        $('#recurring-end').attr('required', false);
        $('#recurring-days').attr('required', false);
        $('#date-start').attr('required', true);
        $('#date-end').attr('required', true);

        $('#recurring-start').attr('disabled', true);
        $('#recurring-end').attr('disabled', true);
        $('#recurring-days').attr('disabled', true);
        $('#date-start').attr('disabled', false);
        $('#date-end').attr('disabled', false);
    }
});
$('#date-start').change((e) => {
    if ($('#date-end').val() === '') {
        $('#date-end').val(e.target.value);
    }
    $('#date-end').attr('min', e.target.value);
});
$('#date-end').change((e) => {
    if ($('#date-start').val() === '') {
        $('#date-start').val(e.target.value);
    }
    $('#date-start').attr('max', e.target.value);
});
$('#recurring-start').change((e) => {
    if ($('#recurring-end').val() === '') {
        $('#recurring-end').val(e.target.value);
    }
    $('#recurring-end').attr('min', e.target.value);
});
$('#recurring-end').change((e) => {
    if ($('#recurring-start').val() === '') {
        $('#recurring-start').val(e.target.value);
    }
    $('#recurring-start').attr('max', e.target.value);
});

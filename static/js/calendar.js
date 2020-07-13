var spinner = {
    run: false,
    set run(val) {
        let cal = $('#calendar');
        let spin = $('#spinner-compute');
        if (val) {
            $('#sidebarMenu').collapse('hide');
            cal.css('opacity', '0.2');
            spin.css('display', 'initial');
        } else {
            cal.css('opacity', '1');
            spin.css('display', 'none');
        }
    },
};

var eventArray = [];
var calendar = {};

document.addEventListener('DOMContentLoaded', function() {
    let calendarDiv = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarDiv, {
        plugins: ['interaction', 'dayGrid', 'list', 'timeGrid', 'bootstrap'],
        themeSystem: 'bootstrap',
        height: 'auto',
        width: 'parent',
        minTime: '08:00:00',
        maxTime: '21:00:00',
        navLinks: true, // can click day/week names to navigate views
        editable: true,
        droppable: true,
        eventLimit: false, // allow "more" link when too many events

        // Week display
        firstDay: 1,
        weekLabel: 'S',
        weekNumbers: true,
        weekNumbersWithinDays: true,
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
        header: {
            left: 'prev,next today addEvent',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },

        // Remember where the user left the calendar
        defaultView: (localStorage.getItem("fcDefaultView") !== null ? localStorage.getItem("fcDefaultView") : 'timeGridWeek'),
        defaultDate: (localStorage.getItem("fcDefaultDate") !== null ? parseInt(localStorage.getItem("fcDefaultDate")) : Date.now()),
        datesRender: function (arg) {
            localStorage.setItem("fcDefaultView", arg.view.type);
            localStorage.setItem("fcDefaultDate", arg.view.currentStart.getTime());
        },

        // Events refresher
        events: function (fetchInfo, successCallback, failureCallback) {
            successCallback(eventArray);
        },
    });

    calendar.render();
});

$(function () {
    $('[data-toggle="popover"]').popover({
        container: 'body',
        trigger: 'focus'
    });
});


/*
 *  Button callbacks
 */
function computeButton() {
    spinner.run = true;

    // Done (to be replaced by an AJAX request...)
    setTimeout(() => {
        spinner.run = false;
    }, 2e3);
}

function clearButton() {
    console.log("Calendar cleared !");
}

function addCodeButton() {
    spinner.run = true;
    let code = $('#codeInput').val();
    if (code) {
        $.ajax({
            url: Flask.url_for('calendar.add_code', {'code': code}),
            type: 'PUT',
            success: (data) => {
                data.codes.forEach((code) => {
                    $('.list-code-input').before(
                        `<li class="list-group-item code-item d-flex justify-content-between align-items-center">
                        <span class="code-tag" data-toggle="modal" data-target="#detailsModal">`
                        + code +
                        `</span>
                        <a href="#" class="badge badge-danger" onclick="removeCodeButton(this, '`+ code +`')">
                        <i class="fas fa-trash"></i>
                        </a>
                        </li>`);
                })
                $('#codeInput').val('');
            },
            error: (data) => {
                console.log('Request failed.');
            },
            complete: () => {
                spinner.run = false;
            },
        });
    }
}

function removeCodeButton(div, code) {
    spinnerrun = true;
    $.ajax({
        url: Flask.url_for('calendar.remove_code', {'code': code}),
        type: 'PUT',
        success: (data) => {
            $(div).parent().remove();
        },
        error: (data) => {
            console.log('Request failed.');
        },
        complete: () => {
            spinner.run = false;
        },
    });
}


/*
 *  Add an event form
 */
$('#form-add-event').submit((e) => {
    // Prevent form submission
    e.preventDefault();

    // Assemble the event
    let evt = {
        editable: true,
        title: $('#event-title').val(),
        location: $('#event-location').val(),
        notes: $('#event-notes').val(),
    }
    if ($('#switch-repetition').is(':checked')) {
        evt.startTime = $('#time-start').val();
        evt.startRecur = $('#recurring-start').val();
        evt.endTime = $('#time-end').val();
        evt.endRecur = $('#recurring-end').val();
        evt.daysOfWeek = $('#recurring-days').val();
    } else {
        evt.start = $('#date-start').val() + ' ' +$('#time-start').val();
        evt.end = $('#date-end').val() + ' ' +$('#time-end').val();
    }
    eventArray.push(evt);
    calendar.refetchEvents(evt);

    // Clear the form
    e.target.reset();
 });

$('#switch-repetition').change((e) => {
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

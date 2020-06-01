document.addEventListener('DOMContentLoaded', function() {
    let calendarDiv = document.getElementById('calendar');
    let calendar = new FullCalendar.Calendar(calendarDiv, {
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
    let cal = $('#calendar');
    let spinner = $('#spinner-compute');

    // Computing data...
    $('#sidebarMenu').collapse('hide');
    cal.css('opacity', '0.2');
    spinner.css('display', 'initial');

    // Done (to be replaced by an AJAX request...)
    setTimeout(() => {
        cal.css('opacity', '1');
        spinner.css('display', 'none');
    }, 2e3);
}

document.addEventListener('DOMContentLoaded', function() {
    let calendarDiv = document.getElementById('calendar');
    let calendar = new FullCalendar.Calendar(calendarDiv, {
        plugins: ['interaction', 'dayGrid', 'list', 'timeGrid', 'bootstrap'],
        themeSystem: 'bootstrap',
        height: 'auto',
        width: 'parent',
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridDay,listWeek'
        },
        minTime: '08:00:00',
        maxTime: '21:00:00',
        navLinks: true, // can click day/week names to navigate views
        editable: true,
        droppable: true,
        eventLimit: false, // allow "more" link when too many events
        weekNumberCalculation: 'ISO',

        // Remember where the user left the calendar
        defaultView: (localStorage.getItem("fcDefaultView") !== null ? localStorage.getItem("fcDefaultView") : 'dayGridWeek'),
        defaultDate: (localStorage.getItem("fcDefaultDate") !== null ? parseInt(localStorage.getItem("fcDefaultDate")) : Date.now()),
        datesRender: function (arg) {
            localStorage.setItem("fcDefaultView", arg.view.type);
            localStorage.setItem("fcDefaultDate", arg.view.currentStart.getTime());
        },
    });

    calendar.render();
});



function loadScheduleButton(id) {
    $.ajax({
        url: Flask.url_for('account.load_schedule', {'id': id}),
        type: 'GET',
        success: (data) => {
            window.location.href = Flask.url_for('calendar.schedule_viewer')
        },
        error: (data) => {
            console.log("An error has occurred")
        },
        complete: () => {}
    });
}

function deleteScheduleButton(div, id) {
    $.ajax({
        url: Flask.url_for('account.delete_schedule', {'id': id}),
        type: 'DELETE',
        success: (data) => {
            $(div).parent().parent().parent().remove();
        },
        error: (data) => {
            console.log("An error has occurred")
        },
        complete: () => {}
    });
}

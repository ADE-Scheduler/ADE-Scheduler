

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
            $(div).parent().parent().remove();
        },
        error: (data) => {
            console.log("An error has occurred")
        },
        complete: () => {}
    });
}


function updateLabelButton(e, id) {
    // Prevent form submission
    e.preventDefault();

    let form = $('#form-update-label');
    let input = $('#input-label');
    let div = $('#schedule-label');

    if (!input.length) {
        div.remove();
        form.prepend(`<input class="form-control mr-4" type="text" id="input-label" value="`+ div.text() +`"/>`);
    } else {
        if (id == null) {id = -1;}
        $.ajax({
            url: Flask.url_for('account.update_label', {'id': id}),
            type: 'PATCH',
            data: JSON.stringify({'label': input.val()}),
            contentType: 'application/json;charset=UTF-8',
            success: (data) => {
                input.remove();
                form.prepend(`<div id="schedule-label">`+ input.val() +`</div>`);
                $('.current-schedule').find('h6').text(input.val());
            },
            error: (data) => {
                console.log("An error has occurred")
            },
            complete: () => {}
        });
    }
}

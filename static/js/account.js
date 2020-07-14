var unsaved = true;

window.onload = () => {
    $.ajax({
        url: Flask.url_for('account.get_data'),
        type: 'GET',
        success: (data) => {
            unsaved = data.unsaved;
        },
        error: (data) => {
            console.log("An error has occurred")
        },
    })
}


function updateCurrentScheduleData(data, selected_div) {
    unsaved = data.unsaved;
    if (data.no_current_schedule) {
        $('#schedule-label').text(data.label);
        $('#form-update-label').attr('onsubmit', 'updateLabelButton(event, -1)');
    } else {
        $('.current-schedule').removeClass('current-schedule')
        $(selected_div).parent().addClass('current-schedule');
        $('#schedule-label').text(data.label);
        $('#form-update-label').attr('onsubmit', 'updateLabelButton(event,'+data.id+')');
    }
}

function loadScheduleButton(div, id) {
    let req = (div, id) => {
        $.ajax({
            url: Flask.url_for('account.load_schedule', {'id': id}),
            type: 'GET',
            success: (data) => {
                updateCurrentScheduleData(data, div);
            },
            error: (data) => {
                console.log("An error has occurred")
            },
        });
    }

    if (unsaved) {
        $('#warningModal').modal('show');
        $('#warningModal').on('hide.bs.modal', (e) => {
            if (document.activeElement.id === 'warning-continue') {
                req(div, id);
            }
            $('#warningModal').off('hide.bs.modal');
        });
    } else {
        req(div, id);
    }
}

function viewScheduleButton(id) {
    let req = (id) => {
        $.ajax({
            url: Flask.url_for('account.load_schedule', {'id': id}),
            type: 'GET',
            success: (data) => {
                window.location.href = Flask.url_for('calendar.schedule_viewer');
            },
            error: (data) => {
                console.log("An error has occurred")
            },
        });
    }

    if (unsaved) {
        $('#warningModal').modal('show');
        $('#warningModal').on('hide.bs.modal', (e) => {
            if (document.activeElement.id === 'warning-continue') {
                req(id);
            }
            $('#warningModal').off('hide.bs.modal');
        });
    } else {
        req(id);
    }
}

function deleteScheduleButton(div, id) {
    $.ajax({
        url: Flask.url_for('account.delete_schedule', {'id': id}),
        type: 'DELETE',
        success: (data) => {
            $(div).parent().parent().remove();
            if (data.no_current_schedule) {
                updateCurrentScheduleData(data);
            }
        },
        error: (data) => {
            console.log("An error has occurred")
        },
    });
}


function updateLabelButton(e, id) {
    // Prevent form submission
    e.preventDefault();

    let form = $('#form-update-label');
    let input = $('#input-label');
    let div = $('#schedule-label');

    if (div.length) {
        div.remove();
        form.prepend(`<input class="form-control mr-4" type="text" id="input-label" value="`+ div.text() +`"/>`);
        $('#input-label').focus();
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
        });
    }
}

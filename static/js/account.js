var unsaved = true;
var spinner = {
    run: false,
    set run(val) {
        let div1 = $('#form-update-label');
        let div2 = $('#info-schedule');
        let spin = $('#spinner-compute');
        if (val) {
            $('#sidebarMenu').collapse('hide');
            div1.css('opacity', '0.2');
            div2.css('opacity', '0.2');
            spin.css('display', 'initial');
        } else {
            div1.css('opacity', '1');
            div2.css('opacity', '1');
            spin.css('display', 'none');
        }
    },
};

window.onload = () => {
    // Fetch data
    spinner.run = true;
    $.ajax({
        url: Flask.url_for('account.get_data'),
        type: 'GET',
        success: (data) => {
            unsaved = data.unsaved;
        },
        error: (data) => {
            console.log("An error has occurred")
        },
        complete: () => {
            spinner.run = false;
        },
    });

    // Some stuff for the warning modal
    $('#warningModal').on('hidden.bs.modal', () => $('#warning-continue').off('click'));
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
        spinner.run = true;
        $.ajax({
            url: Flask.url_for('account.load_schedule', {'id': id}),
            type: 'GET',
            success: (data) => {
                updateCurrentScheduleData(data, div);
            },
            error: (data) => {
                console.log("An error has occurred")
            },
            complete: () => {
                spinner.run = false;
            }
        });
    }

    if (unsaved) {
        $('#warningModal').modal('show');
        $('#warning-continue').on('click', () => req(div, id));
    } else {
        req(div, id);
    }
}

function viewScheduleButton(id) {
    let req = (id) => {
        spinner.run = true;
        $.ajax({
            url: Flask.url_for('account.load_schedule', {'id': id}),
            type: 'GET',
            success: (data) => {
                window.location.href = Flask.url_for('calendar.schedule_viewer');
            },
            error: (data) => {
                console.log("An error has occurred")
            },
            complete: () => {
                spinner.run = false;
            },
        });
    }

    if (unsaved) {
        $('#warningModal').modal('show');
        $('#warning-continue').on('click', () => req(id));
    } else {
        req(id);
    }
}

function deleteScheduleButton(div, id) {
    spinner.run = true;
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
        complete: () => {
            spinner.run = false;
        }
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
        spinner.run = true;
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
            complete: () => {
                spinner.run = false;
            }
        });
    }
}

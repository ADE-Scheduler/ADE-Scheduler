from flask import current_app as app
from flask import Blueprint, render_template, session, request, jsonify
from flask_security import login_required, current_user

import backend.schedules as schd
from backend.ade_api import DEFAULT_PROJECT_ID

account = Blueprint('account', __name__, static_folder='../static')


@account.before_request
def before_account_request():
    if not session.get('current_schedule'):
        session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
        session['current_schedule_modified'] = True


@account.route('/')
@login_required
def dashboard():
    return render_template('account.html')


@account.route('/get/data', methods=['GET'])
@login_required
def get_data():
    return jsonify({
        'unsaved': session['current_schedule_modified'],
        'schedules': list(map(lambda s: {
            'id': s.id,
            'label': s.data.label,
        }, current_user.get_schedule())),
        'current_schedule': {
            'id': session['current_schedule'].id,
            'label': session['current_schedule'].label,
        },
    }), 200


@account.route('/load/schedule/<id>', methods=['GET'])
@login_required
def load_schedule(id):
    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        session['current_schedule'] = schedule.data
        session['current_schedule_modified'] = False
        return jsonify({
            'current_schedule': {
                'id': schedule.data.id,
                'label': schedule.data.label,
            },
            'unsaved': session['current_schedule_modified'],
        }), 200
    else:
        return '', 403      # Requested id is not in this user's schedule list.


@account.route('/delete/schedule/<id>', methods=['DELETE'])
@login_required
def delete_schedule(id):
    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        current_user.remove_schedule(schedule)
        if session['current_schedule'].id == schedule.id:
            session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
            session['current_schedule_modified'] = True
            return jsonify({
                'no_current_schedule': True,
                'current_schedule': {
                    'id': schedule.data.id,
                    'label': schedule.data.label,
                },
                'unsaved': session['current_schedule_modified'],
            }), 200
        return 'OK', 200
    else:
        return '', 403      # Requested id is not in this user's schedule list.


@account.route('/update/label/<id>', methods=['PATCH'])
@login_required
def update_label(id):
    label = request.json.get('label')

    if int(id) == -1:
        session['current_schedule'].label = label
        return 'OK', 200

    schedule = current_user.get_schedule(id=int(id))
    if schedule and session['current_schedule'].id == int(id):
        session['current_schedule'].label = label
        schedule.update_label(label)
        return '', 200
    else:
        return '', 403      # Requested id is not in this user's schedule list.

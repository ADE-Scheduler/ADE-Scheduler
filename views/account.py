from flask import current_app as app
from flask import Blueprint, render_template, session, request
from flask_security import login_required, current_user

import backend.schedules as schd
from backend.ade_api import DEFAULT_PROJECT_ID

account = Blueprint('account', __name__, static_folder='../static')


@account.before_request
def before_account_request():
    if not session.get('current_schedule'):
        session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)


@account.route('/')
@login_required
def dashboard():
    return render_template('account.html', schedules=current_user.get_schedule(), current_schedule=session['current_schedule'])


@account.route('/load/schedule/<id>', methods=['GET'])
@login_required
def load_schedule(id):
    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        session['current_schedule'] = schedule.data
        return 'OK', 200
    else:
        return '', 403      # Requested id is not in this user's schedule list.


@account.route('/delete/schedule/<id>', methods=['DELETE'])
@login_required
def delete_schedule(id):
    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        if session['current_schedule'].id == schedule.id:
            session['current_schedule'] = None
        current_user.remove_schedule(schedule)
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
        mng = app.config['MANAGER']
        session['current_schedule'].label = label
        session['current_schedule'] = mng.save_schedule(current_user, session['current_schedule'])
        return '', 200
    else:
        return '', 403      # Requested id is not in this user's schedule list.

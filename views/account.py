from flask import Blueprint, render_template, session
from flask_security import login_required, current_user


account = Blueprint('account', __name__, static_folder='../static')

@account.route('/')
@login_required
def dashboard():
    schedules = map(lambda s: {'id': s.id, 'label': s.label}, current_user.get_schedule())
    if session.get('current_schedule'):
        id = session['current_schedule'].id
    else:
        id = None
    return render_template('account.html', schedules=schedules, id=id)


@account.route('/load/schedule/<id>', methods=['GET'])
@login_required
def load_schedule(id):
    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        session['current_schedule'] = schedule.data
        return 'Success', 200
    else:
        return '', 403      # Requested id is not in this user's schedule list.


@account.route('/delete/schedule/<id>', methods=['DELETE'])
@login_required
def delete_schedule(id):
    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        if session.get('current_schedule'):
            if session['current_schedule'].id == schedule.id:
                session['current_schedule'] = None
        current_user.remove_schedule(schedule)
        return 'Success', 200
    else:
        return '', 403      # Requested id is not in this user's schedule list.

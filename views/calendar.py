import re
import time

from flask import current_app as app
from flask import Blueprint, render_template, session, jsonify, redirect, url_for, request
from flask_security import current_user, login_required

import backend.schedules as schd
from backend.ade_api import DEFAULT_PROJECT_ID


calendar = Blueprint('calendar', __name__, static_folder='../static')


@calendar.before_request
def before_calendar_request():
    if not session.get('current_schedule'):
        session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
        session['current_schedule_modified'] = True


@calendar.route('/')
def schedule_viewer():
    current_schedule = session['current_schedule']
    return render_template('calendar.html', codes=current_schedule.codes)


@calendar.route('/add/<code>', methods=['PATCH'])
def add_code(code):
    pattern = re.compile('^\s+|\s*,\s*|\s+$')
    codes = [x.upper() for x in pattern.split(code) if x]
    codes = session['current_schedule'].add_course(codes)
    session['current_schedule_modified'] = True
    return jsonify({
        'codes': codes,
        'events': [],
    }), 200


@calendar.route('/remove/<code>', methods=['PATCH'])
def remove_code(code):
    session['current_schedule'].remove_course(code)
    session['current_schedule_modified'] = True
    return 'OK', 200


@calendar.route('/clear', methods=['DELETE'])
def clear():
    session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
    session['current_schedule_modified'] = True
    return 'OK', 200


@calendar.route('/compute', methods=['GET'])
def compute():
    # TODO: plug in the current_schedule.compute() function and return relevant data
    time.sleep(2)
    session['current_schedule_modified'] = True
    return jsonify({}), 200


@calendar.route('/save', methods=['POST'])
def save():
    if not current_user.is_authenticated:
        return 'Login is required', 401

    # TODO: save the schedule in the current user's schedule list. Either create a new one,
    #       or update existing, according to the situation.
    mng = app.config['MANAGER']
    session['current_schedule'] = mng.save_schedule(current_user, session['current_schedule'])
    session['current_schedule_modified'] = False
    return 'OK', 200


@calendar.route('/add/custom_event', methods=['POST'])
def add_custom_event():
    event = request.json
    print(event)
    session['current_schedule_modified'] = True
    return 'OK', 200

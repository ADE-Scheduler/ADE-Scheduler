import re

from flask import Blueprint, render_template, session, jsonify
from flask_security import current_user

import backend.schedules as schd
from backend.ade_api import DEFAULT_PROJECT_ID


calendar = Blueprint('calendar', __name__, static_folder='../static')


@calendar.before_request
def before_first_calendar_request():
    if 'current_schedule' not in session:
        session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)


@calendar.route('/')
def schedule_viewer():
    current_schedule = session['current_schedule']
    return render_template('calendar.html', codes=current_schedule.codes)


@calendar.route('/add/<code>', methods=['PUT'])
def add_code(code):
    pattern = re.compile('^\s+|\s*,\s*|\s+$')
    codes = [x.upper() for x in pattern.split(code) if x]
    session['current_schedule'].add_course(codes)
    return jsonify({
        'codes': codes,
        'events': [],
    }), 200


@calendar.route('/remove/<code>', methods=['PUT'])
def remove_code(code):
    session['current_schedule'].remove_course(code)
    return "Success", 200

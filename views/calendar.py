import re
from datetime import datetime

from flask import current_app as app
from flask import Blueprint, render_template, session, jsonify, redirect, url_for, request, make_response
from flask_security import current_user, login_required
from flask_babelex import _

import backend.schedules as schd
import backend.events as evt
from backend.ade_api import DEFAULT_PROJECT_ID


calendar = Blueprint('calendar', __name__, static_folder='../static')


@calendar.before_request
def before_calendar_request():
    if not session.get('current_schedule'):
        session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
        session['current_schedule_modified'] = False


@calendar.route('/')
def index():
    return render_template('calendar.html')


@calendar.route('/get/data', methods=['GET'])
def get_data():
    return jsonify({
        'events': session['current_schedule'].get_events(json=True),
        'codes': session['current_schedule'].codes,
    }), 200


@calendar.route('/get/<code>/info', methods=['GET'])
def get_info(code):
    mng = app.config['MANAGER']
    courses = mng.get_courses(code, project_id=session['current_schedule'].project_id)

    summary = dict()
    for course in courses:
        summary[course.code] = course.get_summary()

    if len(courses) is 1:   title = courses[-1].name.upper()
    else:                   title = 'Course program'

    return jsonify({
        'title': title,
        'summary': summary,
        'filtered': session['current_schedule'].filtered_subcodes,
    }), 200


@calendar.route('/add/<code>', methods=['PATCH'])
def add_code(code):
    pattern = re.compile('^\s+|\s*,\s*|\s+$')
    codes = [x.upper() for x in pattern.split(code) if x]
    codes = session['current_schedule'].add_course(codes)
    session['current_schedule_modified'] = True
    return jsonify({
        'codes': codes,
        'events': session['current_schedule'].get_events(json=True),
    }), 200


@calendar.route('/remove/<code>', methods=['PATCH'])
def remove_code(code):
    session['current_schedule'].remove_course(code)
    session['current_schedule_modified'] = True
    return jsonify({
        'events': session['current_schedule'].get_events(json=True),
    }), 200


@calendar.route('/clear', methods=['DELETE'])
def clear():
    session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
    session['current_schedule_modified'] = False
    return 'OK', 200


@calendar.route('/compute', methods=['GET'])
def compute():
    # TODO: plug in the current_schedule.compute() function and return relevant data
    import time
    time.sleep(2)
    session['current_schedule_modified'] = True
    return jsonify({}), 200


@calendar.route('/filter', methods=["PUT"])
def apply_filter():
    schedule = session['current_schedule']
    for code, filters in request.json.items():
        session['current_schedule'].filtered_subcodes[code] = list()
        for type, filters in filters.items():
            for filter, value in filters.items():
                if not value:
                    session['current_schedule'].filtered_subcodes[code].append(type + ': ' + filter)
    return jsonify({
        'events': session['current_schedule'].get_events(json=True),
    }), 200


@calendar.route('/save', methods=['POST'])
def save():
    if not current_user.is_authenticated:
        return 'Login is required', 401

    mng = app.config['MANAGER']
    session['current_schedule'] = mng.save_schedule(current_user, session['current_schedule'])
    session['current_schedule_modified'] = False
    return 'OK', 200


@calendar.route('/add/custom_event', methods=['POST'])
def add_custom_event():
    event = request.json
    event['begin'] = datetime.strptime(event['begin'], '%Y-%m-%d %H:%M').astimezone(evt.TZ)
    event['end'] = datetime.strptime(event['end'], '%Y-%m-%d %H:%M').astimezone(evt.TZ)
    if event.get('end_recurr'):
        event['end_recurr'] = datetime.strptime(event['end_recurr'], '%Y-%m-%d %H:%M').astimezone(evt.TZ)
        event = evt.RecurringCustomEvent(*event.values())
    else:
        event = evt.CustomEvent(*event.values())
    session['current_schedule'].add_custom_event(event)
    session['current_schedule_modified'] = True
    return jsonify({
        'event': event.json(),
    }), 200


@calendar.route('/delete/custom_event/<id>', methods=['DELETE'])
def delete_custom_event(id):
    session['current_schedule'].remove_custom_event(id=id)
    return 'OK', 200


@calendar.route('/download', methods=['GET'])
def download():
    link = request.args.get('link')
    if link:
        mng = app.config['MANAGER']
        schedule, choice = mng.get_schedule(link)
    else:
        schedule = session['current_schedule']
        choice = int(request.args.get('choice')) if request.args.get('choice') else 0

    if schedule is None:
        return _('The schedule you requested does not exist in our database !'), 400
    else:
        resp = make_response(schedule.get_ics_file(choice=choice))
        resp.mimetype = 'text/calendar'
        resp.headers['Content-Disposition'] = 'attachment; filename=' + schedule.label.replace(' ', '_') + '.ics'
        return resp

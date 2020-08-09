import re
import json
from datetime import datetime
from typing import Any

from flask import current_app as app
from flask import Blueprint, render_template, session, jsonify, request, make_response
from flask_security import current_user

import backend.schedules as schd
import backend.events as evt
from backend.ade_api import DEFAULT_PROJECT_ID


class CalendarEncoder(json.JSONEncoder):
    """
    Subclass of json decoder made for the calendar-specific JSON encodings.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class CalendarDecoder(json.JSONDecoder):
    """
    Subclass of json decoder made for the calendar-specific JSON decodings.
    """

    def decode(self, obj: Any, w: Any = None) -> str:
        decoded = json.JSONDecoder().decode(obj)
        for key in decoded:
            obj = decoded[key]
            if isinstance(obj, list) and isinstance(obj[0], str):
                decoded[key] = set(obj)
        return decoded


calendar = Blueprint('calendar', __name__, static_folder='../static')
calendar.json_decoder = CalendarDecoder
calendar.json_encoder = CalendarEncoder


@calendar.before_request
def before_calendar_request():
    if not session.get('current_schedule'):
        session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
        session['current_schedule_modified'] = False


@calendar.route('/')
def index():
    return render_template('calendar.html')


@calendar.route('/', methods=['DELETE'])
def clear():
    session['current_schedule'] = schd.Schedule(DEFAULT_PROJECT_ID)
    session['current_schedule_modified'] = False
    return 'OK', 200


@calendar.route('/data', methods=['GET'])
def get_data():
    return jsonify({
        'events': session['current_schedule'].get_events(json=True),
        'codes': session['current_schedule'].codes,
    }), 200


@calendar.route('/<code>', methods=['PATCH'])
def add_code(code):
    pattern = re.compile('^\s+|\s*,\s*|\s+$')
    codes = [x.upper() for x in pattern.split(code) if x]
    codes = session['current_schedule'].add_course(codes)
    session['current_schedule_modified'] = True
    return jsonify({
        'codes': codes,
        'events': session['current_schedule'].get_events(json=True),
    }), 200


@calendar.route('/<code>', methods=['DELETE'])
def remove_code(code):
    session['current_schedule'].remove_course(code)
    session['current_schedule_modified'] = True
    return jsonify({
        'events': session['current_schedule'].get_events(json=True),
    }), 200


@calendar.route('/<code>/info', methods=['GET'])
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


@calendar.route('/custom_event', methods=['POST'])
def add_custom_event():
    event = request.json
    event['begin'] = datetime.strptime(event['begin'], '%Y-%m-%d %H:%M').astimezone(evt.TZ)
    event['end'] = datetime.strptime(event['end'], '%Y-%m-%d %H:%M').astimezone(evt.TZ)
    if event.get('end_recurrence'):
        event['end_recurrence'] = datetime.strptime(event['end_recurrence'], '%Y-%m-%d %H:%M').astimezone(evt.TZ)
        event = evt.RecurringCustomEvent(**event)
    else:
        event = evt.CustomEvent(**event)
    session['current_schedule'].add_custom_event(event)
    session['current_schedule_modified'] = True
    return jsonify({
        'event': event.json(),
    }), 200


@calendar.route('/custom_event/<id>', methods=['DELETE'])
def delete_custom_event(id):
    session['current_schedule'].remove_custom_event(id=id)
    session['current_schedule_modified'] = True
    return 'OK', 200


@calendar.route('/schedule', methods=['POST'])
def save():
    if not current_user.is_authenticated:
        return 'Login is required', 401

    mng = app.config['MANAGER']
    session['current_schedule'] = mng.save_schedule(current_user, session['current_schedule'])
    session['current_schedule_modified'] = False
    return 'OK', 200


@calendar.route('/schedule', methods=['GET'])
def download():
    link = request.args.get('link')
    choice = int(request.args.get('choice')) if request.args.get('choice') else 0
    if link:
        mng = app.config['MANAGER']
        schedule, _ = mng.get_schedule(link)
    else:
        schedule = session['current_schedule']

    if schedule is None:
        return _('The schedule you requested does not exist in our database !'), 400
    else:
        resp = make_response(schedule.get_ics_file(schedule_number=choice))
        resp.mimetype = 'text/calendar'
        resp.headers['Content-Disposition'] = 'attachment; filename=' + schedule.label.replace(' ', '_') + '.ics'
        return resp


@calendar.route('/schedule', methods=['PUT'])
def apply_filter():
    schedule = session['current_schedule']
    for code, filters in request.json.items():

        for type, filters in filters.items():
            for filter, value in filters.items():
                if not value:
                    schedule.add_filter(code, type + ': ' + filter)
                else:
                    schedule.remove_filter(code, type + ': ' + filter)
    return jsonify({
        'events': session['current_schedule'].get_events(json=True),
    }), 200


@calendar.route('/schedule/link', methods=['GET'])
def export():
    mng = app.config['MANAGER']
    if session['current_schedule'].id is None:
        session['current_schedule'] = mng.save_schedule(current_user if current_user.is_authenticated else None, session['current_schedule'])

    link = mng.get_link(session['current_schedule'].id)
    if link is None:
        return 'KO', 401
    else:
        return jsonify({
            'link': link,
        })


@calendar.route('/schedule/best', methods=['GET'])
def get_best():
    pass


@calendar.route('/schedule/best', methods=['PUT'])
def compute():
    session['current_schedule'].compute_best()
    session['current_schedule_modified'] = True
    return jsonify({}), 200

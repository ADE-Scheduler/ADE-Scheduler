import json
from datetime import datetime
from typing import Any

from flask import current_app as app
from flask import Blueprint, render_template, session, jsonify, request, make_response, redirect, url_for, g
from flask_security import current_user, login_required
from flask_babelex import _

import backend.schedules as schd
import backend.events as evt
import backend.models as md


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
        mng = app.config['MANAGER']
        session['current_schedule'] = schd.Schedule(mng.get_default_project_id())
        session['current_schedule_modified'] = False


@calendar.route('/')
def index():
    if bool(request.args.get('save')) and current_user.is_authenticated:
        mng = app.config['MANAGER']
        session['current_schedule'] = mng.save_schedule(current_user, session['current_schedule'])
        session['current_schedule_modified'] = False
        return render_template('calendar.html', saved=True)
    return render_template('calendar.html')


@calendar.route('/', methods=['DELETE'])
def clear():
    mng = app.config['MANAGER']
    session['current_schedule'] = schd.Schedule(mng.get_default_project_id())
    session['current_schedule_modified'] = False
    return jsonify({
        'label': _(session['current_schedule'].label),
        'current_project_id': session['current_schedule'].project_id,
    }), 200


@calendar.route('/data', methods=['GET'])
def get_data():
    mng = app.config['MANAGER']
    return jsonify({
        'project_id': mng.get_project_ids(),
        'current_project_id': session['current_schedule'].project_id,
        'label': _(session['current_schedule'].label),
        'n_schedules': len(session['current_schedule'].best_schedules),
        'events': session['current_schedule'].get_events(json=True),
        'codes': session['current_schedule'].codes,
    }), 200


@calendar.route('/<search_key>', methods=['GET'])
def search_code(search_key):

    codes = [
        'LELEC2885',
        'LMECA2660',
        'LMECA2170',
        'LEPL1104',
        'A VERY VERY VERY LONG CODE !'
    ]

    codes = [code for code in codes if search_key.upper() in code.upper()]

    return jsonify({
        'codes': codes
    }), 200


@calendar.route('/<code>', methods=['PATCH'])
def add_code(code):
    mng = app.config['MANAGER']
    code = code.upper()
    if not mng.code_exists(code, project_id=session['current_schedule'].project_id):
        return _('The code you added does not exist in our database.'), 404

    codes = session['current_schedule'].add_course(code)
    if codes:
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
    title = dict()
    for course in courses:
        summary[course.code] = course.get_summary()
        title[course.code] = course.name

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
        resp.headers['Content-Disposition'] = 'attachment; filename=' + \
            ''.join(c for c in schedule.label if c.isalnum() or c in ('_')) \
            .rstrip() + '.ics'
        g.track_var['schedule download'] = schedule.id
        return resp


@calendar.route('/share', methods=['GET'])
@login_required
def share():
    link = request.args.get('link')
    if link:
        mng = app.config['MANAGER']
        schedule, _ = mng.get_schedule(link)
    else:
        schedule = None

    if schedule is None:
        return _('The schedule you requested does not exist in our database !'), 400
    else:
        session['current_schedule'] = md.Schedule(schedule, user=current_user).data
        g.track_var['schedule share'] = schedule.id
        return redirect(url_for('calendar.index'))


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


@calendar.route('/schedule/year/<id>', methods=['PUT'])
def update_poject_id(id):
    session['current_schedule'].project_id = id
    session['current_schedule_modified'] = True
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


@calendar.route('/schedule/events', methods=['GET'])
def get_events():
    schedule_number = int(request.args.get('schedule_number'))
    return jsonify({
        'events': session['current_schedule'].get_events(json=True, schedule_number=schedule_number),
    }), 200


@calendar.route('/schedule/best', methods=['PUT'])
def compute():
    bests = session['current_schedule'].compute_best()
    session['current_schedule_modified'] = True
    return jsonify({
        'n_schedules': len(session['current_schedule'].best_schedules) if bests is not None else 0,
        'events': session['current_schedule'].get_events(json=True, schedule_number=1) if bests is not None else list(),
        'selected_schedule': 1 if bests is not None else 0
    }), 200

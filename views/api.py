import json
from typing import Any
from distutils.util import strtobool

from flask import current_app as app
from flask import Blueprint, jsonify, request, session, redirect, url_for

import backend.schedules as schd


class ApiEncoder(json.JSONEncoder):
    """
    Subclass of json decoder made for the calendar-specific JSON encodings.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class ApiDecoder(json.JSONDecoder):
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


api = Blueprint('api', __name__, static_folder='../static')
api.json_decoder = ApiDecoder
api.json_encoder = ApiEncoder


@api.before_request
def before_api_request():
    mng = app.config['MANAGER']

    if not session.get('current_schedule'):
        session['current_schedule'] = schd.Schedule(mng.get_default_project_id())
        session['current_schedule_modified'] = False

    project_ids = [int(year['id']) for year in mng.get_project_ids()]
    if int(session['current_schedule'].project_id) not in project_ids:
        session['current_schedule'].project_id = mng.get_default_project_id()


@api.route('/events', methods=['GET'])
def get_events():
    """
    API endpoint to fetch the schedule matching the various arguments.

    The request accepts 3 arguments:
     - view: if set to True, shows the schedule in ADE-Scheduler's schedule viewer.
             By default, view = False the data is returned in JSON format.
     - year: defines the academical year. Accepted format is YYYY-YYYY where the second year is the first + 1.
             e.g.: 2020-20201
     - code: the various code of the courses to be added to the schedule.
             e.g.: LELEC2885, LMECA2170, LEPL1104,...
             To specify a list of codes, use the following format:
             /schedule?code=CODE_1&code=CODE_2&code=CODE_3 and so on.
     - filtered events: the IDs of the events you want to filter.
            Say the course which code is "CODE" has two TPs with IDs "TP: CODE-Q1A" and "TP: CODE-Q1B"
            and you want to filter out the events of "TP: CODE-Q1A", you can specify such a filter by specifying:
            /schedule?code=CODE&CODE=TP: CODE-Q1A&...

    /!\\ To make sure to avoid any problems, respect the case-sensitiveness of the codes and event IDs.
    Generally, those are uppercase. /!\\

    Example:
        https://ade-scheduler.info.ucl.ac.be/api/events?year=2020-2021&code=LMECA2170&code=LEPL1104&view=true
    or, with filtered events:
        https://ade-scheduler.info.ucl.ac.be/api/events?year=2020-2021&code=LEPL1104&LEPL1104=TP: LEPL1104_Q2B-APE&view=true
    """
    mng = app.config['MANAGER']

    year = request.args.get('year')
    codes = request.args.getlist('code')
    view = request.args.get('view')
    if view is None:
        view = False
    else:
        view = bool(strtobool(request.args.get('view')))

    project_id = mng.get_project_ids(year=year)
    if project_id is None:
        project_id = mng.get_default_project_id()

    schedule = schd.Schedule(project_id=project_id)
    schedule.add_course([code.upper() for code in codes])
    for code in codes:
        schedule.add_filter(code.upper(), request.args.getlist(code))

    if view:
        session['current_schedule'] = schedule
        return redirect(url_for('calendar.index'))

    return jsonify({
        'events': schedule.get_events(json=True),
    }), 200

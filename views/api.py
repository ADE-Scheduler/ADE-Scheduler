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

    Example:
        https://ade-scheduler.info.ucl.ac.be/api/events?year=2020-2021&code=LMECA2170&code=LEPL1104&view=true
    """
    mng = app.config['MANAGER']

    year = request.args.get('year')
    codes = request.args.getlist('code')
    view = bool(strtobool(request.args.get('view')))

    project_id = mng.get_project_ids(year=year)
    if project_id is None:
        project_id = mng.get_default_project_id()

    schedule = schd.Schedule(project_id=project_id)
    schedule.add_course([code.upper() for code in codes])

    if view:
        session['current_schedule'] = schedule
        return redirect(url_for('calendar.index'))

    return jsonify({
        'events': schedule.get_events(json=True),
    }), 200

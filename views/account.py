import json
from typing import Any

from flask import current_app as app
from flask import Blueprint, render_template, session, request, jsonify
from flask_security import login_required, current_user
from flask_babelex import _

import backend.schedules as schd


class AccountEncoder(json.JSONEncoder):
    """
    Subclass of json decoder made for the account-specific JSON encodings.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class AccountDecoder(json.JSONDecoder):
    """
    Subclass of json decoder made for the account-specific JSON decodings.
    """

    def decode(self, obj: Any, w: Any = None) -> str:
        decoded = json.JSONDecoder().decode(obj)
        for key in decoded:
            obj = decoded[key]
            if isinstance(obj, list) and isinstance(obj[0], str):
                if len(obj[0]) > 0 and obj[0][0] == '#':  # Then its color palette and we don't convert back
                    continue
                else:
                    decoded[key] = set(obj)
        return decoded


account = Blueprint('account', __name__, static_folder='../static')
account.json_decoder = AccountDecoder
account.json_encoder = AccountEncoder


@account.before_request
def before_account_request():
    mng = app.config['MANAGER']

    if not session.get('current_schedule'):
        session['current_schedule'] = schd.Schedule(mng.get_default_project_id())
        session['current_schedule_modified'] = False

    project_ids = [int(year['id']) for year in mng.get_project_ids()]
    if int(session['current_schedule'].project_id) not in project_ids:
        session['current_schedule'].project_id = mng.get_default_project_id()


@account.route('/')
@login_required
def index():
    return render_template('account.html')


@account.route('/data', methods=['GET'])
@login_required
def get_data():
    mng = app.config['MANAGER']
    label = session['current_schedule'].label

    if label == schd.DEFAULT_SCHEDULE_NAME:  # Translates the default schedule name
        session['current_schedule'].label = _(label)
        # Might exist a better way ...

    return jsonify({
        'project_id': mng.get_project_ids(),
        'unsaved': session['current_schedule_modified'],
        'schedules': list(map(lambda s: {
            'id': s.id,
            'label': s.data.label,
        }, current_user.get_schedule())),
        'current_schedule': {
            'id': session['current_schedule'].id,
            'project_id': session['current_schedule'].project_id,
            'label': session['current_schedule'].label,
            'color_palette': session['current_schedule'].color_palette,
        },
    }), 200


@account.route('/schedule/<id>', methods=['GET'])
@login_required
def load_schedule(id):
    if int(id) == -1:
        return 'OK', 200

    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        session['current_schedule'] = schedule.data
        session['current_schedule_modified'] = False
        return jsonify({
            'current_schedule': {
                'id': schedule.data.id,
                'project_id': schedule.data.project_id,
                'label': schedule.data.label,
                'color_palette': schedule.data.color_palette,
            },
            'unsaved': session['current_schedule_modified'],
        }), 200
    return '', 403      # Requested id is not in this user's schedule list.


@account.route('/schedule/<id>', methods=['DELETE'])
@login_required
def delete_schedule(id):
    id = int(id)
    schedule = current_user.get_schedule(id=id)
    if schedule is None and id is not -1:
        return '', 403      # Requested id is not in this user's schedule list.

    if schedule is not None:
        current_user.remove_schedule(schedule)

    if id is session['current_schedule'].id or id is -1:
        mng = app.config['MANAGER']
        session['current_schedule'] = schd.Schedule(mng.get_default_project_id())
        session['current_schedule_modified'] = True

    return jsonify({
        'current_schedule': {
            'id': session['current_schedule'].id,
            'project_id': session['current_schedule'].project_id,
            'label': session['current_schedule'].label,
            'color_palette': session['current_schedule'].color_palette,
        },
        'unsaved': session['current_schedule_modified'],
    }), 200


@account.route('/label/<id>', methods=['PATCH'])
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
        return 'OK', 200
    return '', 403      # Requested id is not in this user's schedule list.


@account.route('/schedule', methods=['POST'])
@login_required
def save():
    s = session['current_schedule']
    s.project_id = request.json['project_id']
    s.color_palette = request.json['color_palette']
    mng = app.config['MANAGER']
    session['current_schedule'] = mng.save_schedule(current_user, s)
    session['current_schedule_modified'] = False
    return jsonify({
        'saved_schedule': {
            'id': session['current_schedule'].id,
            'label': session['current_schedule'].label,
        },
        'unsaved': session['current_schedule_modified'],
    }), 200

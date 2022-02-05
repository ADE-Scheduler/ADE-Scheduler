import json
import uuid

from flask import current_app as app
from flask import session
from flask_login import current_user

import backend.schedules as schd


def init_session():
    mng = app.config["MANAGER"]

    if not session.get("uuid"):
        session["uuid"] = uuid.uuid4()

    if not session.get("current_schedule"):
        session["current_schedule"] = schd.Schedule(mng.get_default_project_id())

    if session.get("current_schedule_modified", None) is None:
        session["current_schedule_modified"] = False

    project_ids = [int(year["id"]) for year in mng.get_project_ids()]
    if int(session["current_schedule"].project_id) not in project_ids:
        session["current_schedule"].project_id = mng.get_default_project_id()


def autosave_schedule(response):
    if response.is_json and session["current_schedule_modified"]:
        if current_user.is_authenticated and current_user.autosave:
            mng = app.config["MANAGER"]
            session["current_schedule"] = mng.save_schedule(
                current_user, session["current_schedule"], session["uuid"]
            )
            session["current_schedule_modified"] = False

        data = json.loads(response.get_data())
        data["unsaved"] = session["current_schedule_modified"]
        response.set_data(json.dumps(data))

    return response


def autoload_schedule():
    if current_user.is_authenticated and session["current_schedule"].id is not None:
        schedule = current_user.get_schedule(id=session["current_schedule"].id)

        if schedule is None:
            mng = app.config["MANAGER"]
            session["current_schedule"] = schd.Schedule(mng.get_default_project_id())
            session["current_schedule_modified"] = False
            return

        if (
            schedule.last_modified_by != session["uuid"]
            and schedule.last_modified_by is not None
        ):
            session["current_schedule"] = schedule.data
            schedule.update_last_modified_by(session["uuid"])

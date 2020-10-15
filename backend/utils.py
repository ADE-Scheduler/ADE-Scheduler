from flask import current_app as app
from flask import session
from flask_security import current_user

import backend.schedules as schd


def init_schedule():
    mng = app.config["MANAGER"]

    if not session.get("current_schedule"):
        session["current_schedule"] = schd.Schedule(mng.get_default_project_id())
        session["current_schedule_modified"] = False

    project_ids = [int(year["id"]) for year in mng.get_project_ids()]
    if int(session["current_schedule"].project_id) not in project_ids:
        session["current_schedule"].project_id = mng.get_default_project_id()


def autosave_schedule():
    mng = app.config["MANAGER"]

    if session["current_schedule_modified"]:
        if current_user.is_authenticated and current_user.autosave:
            mng = app.config["MANAGER"]
            session["current_schedule"] = mng.save_schedule(
                current_user, session["current_schedule"]
            )

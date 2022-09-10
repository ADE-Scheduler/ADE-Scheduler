import json
from typing import Any
from urllib.parse import urlparse

import requests
from flask import Blueprint
from flask import current_app as app
from flask import jsonify, render_template, request, session
from flask_babel import LazyString, gettext
from flask_login import current_user, login_required
from ics import Calendar

import backend.schedules as schd
import views.utils as utl
from backend.manager import ExternalCalendarAlreadyExistsError


class AccountEncoder(json.JSONEncoder):
    """
    Subclass of json decoder made for the account-specific JSON encodings.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, LazyString):
            return str(obj)
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
                if (
                    len(obj[0]) > 0 and obj[0][0] == "#"
                ):  # Then its color palette and we don't convert back
                    continue
                else:
                    decoded[key] = set(obj)
        return decoded


account = Blueprint("account", __name__, static_folder="../static")
account.json_decoder = AccountDecoder
account.json_encoder = AccountEncoder


@account.before_request
def before_account_request():
    utl.init_session()
    utl.autoload_schedule()


@account.route("/")
@login_required
def index():
    return render_template("account.html")


@account.route("/data", methods=["GET"])
@login_required
def get_data():
    mng = app.config["MANAGER"]

    return (
        jsonify(
            {
                "external_calendars": list(
                    map(
                        lambda ec: {
                            "id": ec.id,
                            "code": ec.code,
                            "approved": ec.approved,
                            "url": ec.url,
                        },
                        mng.get_external_calendars(current_user),
                    )
                ),
                "project_id": mng.get_project_ids(),
                "unsaved": session["current_schedule_modified"],
                "autosave": current_user.autosave,
                "schedules": list(
                    map(
                        lambda s: {"id": s.id, "label": s.data.label},
                        current_user.get_schedules(),
                    )
                ),
                "current_schedule": {
                    "id": session["current_schedule"].id,
                    "project_id": session["current_schedule"].project_id,
                    "label": session["current_schedule"].label,
                    "color_palette": session["current_schedule"].color_palette,
                },
            }
        ),
        200,
    )


@account.route("/schedule/<id>", methods=["GET"])
@login_required
def load_schedule(id):
    if int(id) == -1:
        return "OK", 200

    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        session["current_schedule"] = schedule.data
        session["current_schedule_modified"] = False
        return (
            jsonify(
                {
                    "current_schedule": {
                        "id": schedule.data.id,
                        "project_id": schedule.data.project_id,
                        "label": schedule.data.label,
                        "color_palette": schedule.data.color_palette,
                    },
                    "unsaved": session["current_schedule_modified"],
                }
            ),
            200,
        )
    return gettext("Schedule n°%d is not in your schedule list.") % int(id), 403


@account.route("/schedule/<id>", methods=["DELETE"])
@login_required
def delete_schedule(id):
    id = int(id)
    schedule = current_user.get_schedule(id=id)
    if schedule is None and id != -1:
        return gettext("Schedule n°%d is not in your schedule list.") % int(id), 403

    if schedule is not None:
        current_user.remove_schedule(schedule)

    if id == session["current_schedule"].id or id == -1:
        mng = app.config["MANAGER"]
        session["current_schedule"] = schd.Schedule(mng.get_default_project_id())
        session["current_schedule_modified"] = True

    return (
        jsonify(
            {
                "current_schedule": {
                    "id": session["current_schedule"].id,
                    "project_id": session["current_schedule"].project_id,
                    "label": session["current_schedule"].label,
                    "color_palette": session["current_schedule"].color_palette,
                },
                "unsaved": session["current_schedule_modified"],
            }
        ),
        200,
    )


@account.route("/external_calendar/<id>", methods=["DELETE"])
@login_required
def delete_external_calendar(id):
    id = int(id)
    mng = app.config["MANAGER"]
    mng.delete_external_calendar(id)

    return gettext("External Activity Deleted"), 200


@account.route("/label/<id>", methods=["PATCH"])
@login_required
def update_label(id):
    label = request.json.get("label")

    if int(id) == -1:
        session["current_schedule"].label = label
        return "OK", 200

    schedule = current_user.get_schedule(id=int(id))
    if schedule and session["current_schedule"].id == int(id):
        session["current_schedule"].label = label
        schedule.update_label(label)
        return "OK", 200
    return gettext("Schedule n°%d is not in your schedule list.") % int(id), 403


@account.route("/schedule", methods=["POST"])
@login_required
def save():
    s = session["current_schedule"]
    s.project_id = request.json["project_id"]
    s.color_palette = request.json["color_palette"]
    mng = app.config["MANAGER"]
    session["current_schedule"] = mng.save_schedule(
        current_user, s, session.get("uuid")
    )
    session["current_schedule_modified"] = False
    return (
        jsonify(
            {
                "saved_schedule": {
                    "id": session["current_schedule"].id,
                    "label": session["current_schedule"].label,
                },
                "unsaved": session["current_schedule_modified"],
            }
        ),
        200,
    )


@account.route("/autosave", methods=["POST"])
@login_required
def autosave():
    current_user.set_autosave(request.json["autosave"])
    return jsonify({}), 200


@account.route("/external_calendar", methods=["POST"])
def add_external_calendar():
    course = request.json

    hostname = urlparse(request.base_url).hostname
    url = course["url"]

    if url.startswith(
        "webcal://"
    ):  # Many websites provide ical link with this prefix instead
        url = "https" + url[6:]

    if urlparse(url).hostname == hostname:
        return (
            gettext(
                "Sorry, but we currently do not accept calendars emitted by ADE Scheduler to avoid circular dependencies."
            ),
            400,
        )

    try:  # Check if URL correctly returns some iCal
        # TODO: how to prevent attacks? See https://lgtm.com/rules/1514759767119/
        _ = Calendar(requests.get(url).text)  # lgtm [py/full-ssrf]
    except Exception:
        return gettext("The url you entered does not return a valid .ics file."), 400

    if not current_user.is_authenticated:
        return gettext("To save your schedule, you need to be logged in."), 401

    try:
        mng = app.config["MANAGER"]
        mng.save_ics_url(
            course["code"].upper(),
            course["name"],
            url,
            course.get("description", None),
            current_user,
            False,
        )  # False: waiting to be approved
    except ExternalCalendarAlreadyExistsError as e:
        return str(e), 400

    return (
        gettext("Your calendar has been created and is now awaiting for approval."),
        200,
    )

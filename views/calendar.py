import json
from datetime import datetime
from typing import Any

from flask import Blueprint
from flask import current_app as app
from flask import (
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_babel import LazyString, gettext
from flask_login import current_user, login_required

import backend.events as evt
import backend.schedules as schd
import views.utils as utl


class CalendarEncoder(json.JSONEncoder):
    """
    Subclass of json decoder made for the calendar-specific JSON encodings.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, LazyString):
            return str(obj)
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
            if (
                isinstance(obj, list)
                and isinstance(obj[0], str)
                and key != "color_palette"
            ):
                decoded[key] = set(obj)
        return decoded


calendar = Blueprint("calendar", __name__, static_folder="../static")
calendar.json_decoder = CalendarDecoder
calendar.json_encoder = CalendarEncoder


@calendar.before_request
def before_calendar_request():
    utl.init_session()
    utl.autoload_schedule()


@calendar.after_request
def after_calendar_request(response):
    response = utl.autosave_schedule(response)
    return response


@calendar.route("/")
def index():
    return render_template("calendar.html")


@calendar.route("/", methods=["DELETE"])
def clear():
    mng = app.config["MANAGER"]
    session["current_schedule"] = schd.Schedule(mng.get_default_project_id())
    session["current_schedule_modified"] = False
    return (
        jsonify(
            {
                "current_schedule": {
                    "id": session["current_schedule"].id,
                    "label": gettext(session["current_schedule"].label),
                    "color_palette": session["current_schedule"].color_palette,
                },
                "current_project_id": session["current_schedule"].project_id,
            }
        ),
        200,
    )


@calendar.route("/data", methods=["GET"])
def get_data():
    mng = app.config["MANAGER"]
    min_time_slot, max_time_slot = session["current_schedule"].get_min_max_time_slots()
    return (
        jsonify(
            {
                "project_id": mng.get_project_ids(),
                "current_project_id": session["current_schedule"].project_id,
                "current_schedule": {
                    "id": session["current_schedule"].id,
                    "label": gettext(session["current_schedule"].label),
                    "color_palette": session["current_schedule"].color_palette,
                },
                "n_schedules": len(session["current_schedule"].best_schedules),
                "events": session["current_schedule"].get_events(json=True),
                "codes": session["current_schedule"].codes,
                "schedules": (
                    list()
                    if not current_user.is_authenticated
                    else list(
                        map(
                            lambda s: {"id": s.id, "label": gettext(s.data.label)},
                            current_user.get_schedules(),
                        )
                    )
                ),
                "autosave": getattr(current_user, "autosave", False),
                "min_time_slot": min_time_slot,
                "max_time_slot": max_time_slot,
            }
        ),
        200,
    )


@calendar.route("/schedule/<id>", methods=["GET"])
@login_required
def load_schedule(id):
    mng = app.config["MANAGER"]
    schedule = current_user.get_schedule(id=int(id))
    if schedule:
        session["current_schedule"] = schedule.data
        session["current_schedule_modified"] = False
        min_time_slot, max_time_slot = session[
            "current_schedule"
        ].get_min_max_time_slots()
        return (
            jsonify(
                {
                    "current_schedule": {
                        "id": schedule.data.id,
                        "label": gettext(schedule.data.label),
                        "color_palette": schedule.data.color_palette,
                    },
                    "project_id": mng.get_project_ids(),
                    "current_project_id": session["current_schedule"].project_id,
                    "n_schedules": len(session["current_schedule"].best_schedules),
                    "events": session["current_schedule"].get_events(json=True),
                    "codes": session["current_schedule"].codes,
                    "schedules": list(
                        map(
                            lambda s: {"id": s.id, "label": gettext(s.data.label)},
                            current_user.get_schedules(),
                        )
                    ),
                    "min_time_slot": min_time_slot,
                    "max_time_slot": max_time_slot,
                }
            ),
            200,
        )
    return gettext("Schedule n°%d is not in your schedule list.") % int(id), 403


@calendar.route("/<path:search_key>", methods=["GET"])
def search_code(search_key):
    search_key = search_key.replace("*", "")  # * does not work in Python
    # see: https://stackoverflow.com/questions/3675144/regex-error-nothing-to-repeat/44657703
    mng = app.config["MANAGER"]
    codes = mng.get_codes_matching(search_key, session["current_schedule"].project_id)
    return jsonify({"codes": codes}), 200


@calendar.route("/<path:code>", methods=["PATCH"])
def add_code(code):
    mng = app.config["MANAGER"]
    code = code.upper()
    if not mng.code_exists(code, project_id=session["current_schedule"].project_id):
        return gettext("The code you added does not exist in our database."), 404

    codes = session["current_schedule"].add_course(code)

    min_time_slot, max_time_slot = session["current_schedule"].get_min_max_time_slots()
    if codes:
        session["current_schedule_modified"] = True
    return (
        jsonify(
            {
                "codes": codes,
                "events": session["current_schedule"].get_events(json=True),
                "min_time_slot": min_time_slot,
                "max_time_slot": max_time_slot,
            }
        ),
        200,
    )


@calendar.route("/<path:code>", methods=["DELETE"])
def remove_code(code):
    session["current_schedule"].remove_course(code)
    session["current_schedule_modified"] = True

    min_time_slot, max_time_slot = session["current_schedule"].get_min_max_time_slots()
    return (
        jsonify(
            {
                "events": session["current_schedule"].get_events(json=True),
                "min_time_slot": min_time_slot,
                "max_time_slot": max_time_slot,
            }
        ),
        200,
    )


@calendar.route("/<path:code>/info", methods=["GET"])
def get_info(code):
    mng = app.config["MANAGER"]
    courses = mng.get_courses(code, project_id=session["current_schedule"].project_id)

    summary = dict()
    title = dict()
    for course in courses:
        summary[course.code] = course.get_summary()
        title[course.code] = course.name

    return (
        jsonify(
            {
                "title": title,
                "summary": summary,
                "filtered": session["current_schedule"].filtered_subcodes,
            }
        ),
        200,
    )


@calendar.route("/custom_event", methods=["POST"])
def add_custom_event():
    event = request.json
    event["begin"] = datetime.strptime(event["begin"], "%Y-%m-%d %H:%M").astimezone(
        evt.TZ
    )
    event["end"] = datetime.strptime(event["end"], "%Y-%m-%d %H:%M").astimezone(evt.TZ)
    if event.get("end_recurrence"):
        event["end_recurrence"] = datetime.strptime(
            event["end_recurrence"], "%Y-%m-%d %H:%M"
        ).astimezone(evt.TZ)
        event = evt.RecurringCustomEvent(**event)
    else:
        event = evt.CustomEvent(**event)
    session["current_schedule"].add_custom_event(event)
    session["current_schedule_modified"] = True
    return (jsonify({"event": event.json()}), 200)


@calendar.route("/custom_event/<id>", methods=["DELETE"])
def delete_custom_event(id):
    session["current_schedule"].remove_custom_event(id=id)
    session["current_schedule_modified"] = True
    return jsonify({}), 200


@calendar.route("/custom_event/<id>", methods=["POST"])
def update_custom_event(id):
    title = request.json.get("title")
    color = request.json.get("color")
    location = request.json.get("location")
    description = request.json.get("description")

    session["current_schedule"].set_custom_event_attributes(
        id, name=title, color=color, location=location, description=description
    )

    session["current_schedule_modified"] = True
    schedule_number = int(request.json.get("schedule_number"))
    return (
        jsonify(
            {
                "events": session["current_schedule"].get_events(
                    json=True, schedule_number=schedule_number
                )
            }
        ),
        200,
    )


@calendar.route("/schedule", methods=["POST"])
def save():
    if not current_user.is_authenticated:
        return gettext("To save your schedule, you need to be logged in."), 401
    mng = app.config["MANAGER"]
    session["current_schedule"] = mng.save_schedule(
        current_user, session["current_schedule"], session.get("uuid")
    )
    session["current_schedule_modified"] = False
    return (
        jsonify(
            {
                "schedules": list(
                    map(
                        lambda s: {"id": s.id, "label": gettext(s.data.label)},
                        current_user.get_schedules(),
                    )
                )
            }
        ),
        200,
    )


@calendar.route("/schedule", methods=["GET"])
def download():
    mng = app.config["MANAGER"]
    link = request.args.get("link")

    try:
        choice = int(request.args.get("choice")) if request.args.get("choice") else 0
    except ValueError:
        choice = 0

    if link:
        schedule = mng.get_schedule(link)[0]
    else:
        schedule = session["current_schedule"]

    project_ids = [int(year["id"]) for year in mng.get_project_ids()]
    if int(schedule.project_id) not in project_ids:
        schedule.project_id = mng.get_default_project_id()

    if schedule is None:
        return (
            gettext("The schedule you requested does not exist in our database !"),
            400,
        )
    else:
        resp = make_response(schedule.get_ics_file(schedule_number=choice))
        resp.mimetype = "text/calendar"
        resp.headers["Content-Disposition"] = (
            "attachment; filename="
            + "".join(c for c in schedule.label if c.isalnum() or c in ("_")).rstrip()
            + ".ics"
        )
        g.track_var["schedule download"] = schedule.id
        return resp


@calendar.route("/share", methods=["GET"])
def share():
    link = request.args.get("link")
    if link:
        mng = app.config["MANAGER"]
        schedule = mng.get_schedule(link)[0]
    else:
        schedule = None

    if schedule is None:
        return (
            gettext("The schedule you requested does not exist in our database !"),
            400,
        )
    else:
        g.track_var["schedule share"] = schedule.id
        session["current_schedule"] = schedule
        session["current_schedule"].id = None  # "unsave" this schedule
        return redirect(url_for("calendar.index"))


@calendar.route("/schedule", methods=["PUT"])
def apply_filter():
    schedule = session["current_schedule"]
    for code, filters in request.json.items():
        for type, filters in filters.items():
            for filter, value in filters.items():
                if not value:
                    schedule.add_filter(code, type + ": " + filter)
                else:
                    schedule.remove_filter(code, type + ": " + filter)
    session["current_schedule_modified"] = True
    return (jsonify({"events": session["current_schedule"].get_events(json=True)}), 200)


@calendar.route("/schedule/year/<id>", methods=["PUT"])
def update_poject_id(id):
    session["current_schedule"].project_id = id
    session["current_schedule_modified"] = True
    return (jsonify({"events": session["current_schedule"].get_events(json=True)}), 200)


@calendar.route("/schedule/link", methods=["GET"])
def export():
    mng = app.config["MANAGER"]
    if session["current_schedule"].id is None:
        session["current_schedule"] = mng.save_schedule(
            current_user if current_user.is_authenticated else None,
            session["current_schedule"],
            session.get("uuid"),
        )

    link = mng.get_link(session["current_schedule"].id)
    if link is None:
        return gettext("Hum... this schedule does not have an associated link."), 401
    else:
        return jsonify({"link": link})


@calendar.route("/schedule/events", methods=["GET"])
def get_events():
    schedule_number = int(request.args.get("schedule_number"))
    return (
        jsonify(
            {
                "events": session["current_schedule"].get_events(
                    json=True, schedule_number=schedule_number
                )
            }
        ),
        200,
    )


@calendar.route("/schedule/best", methods=["PUT"])
def compute():
    bests = session["current_schedule"].compute_best()
    session["current_schedule_modified"] = True
    return (
        jsonify(
            {
                "n_schedules": (
                    len(session["current_schedule"].best_schedules)
                    if bests is not None
                    else 0
                ),
                "events": (
                    session["current_schedule"].get_events(json=True, schedule_number=1)
                    if bests is not None
                    else list()
                ),
                "selected_schedule": 1 if bests is not None else 0,
            }
        ),
        200,
    )


@calendar.route("/schedule/best", methods=["DELETE"])
def reset_best_schedules():
    session["current_schedule"].reset_best_schedules()

    session["current_schedule_modified"] = True
    return (
        jsonify(
            {
                "events": session["current_schedule"].get_events(
                    json=True, schedule_number=0
                )
            }
        ),
        200,
    )


@calendar.route("/schedule/color", methods=["POST"])
def update_color():
    color_palette = request.json.get("color_palette")
    if color_palette:
        session["current_schedule"].color_palette = color_palette

    schedule_number = int(request.json.get("schedule_number"))
    session["current_schedule_modified"] = True
    return (
        jsonify(
            {
                "events": session["current_schedule"].get_events(
                    json=True, schedule_number=schedule_number
                )
            }
        ),
        200,
    )


@calendar.route("/schedule/color", methods=["DELETE"])
def reset_color():
    session["current_schedule"].reset_color_palette()

    schedule_number = int(request.json.get("schedule_number"))
    session["current_schedule_modified"] = True
    return (
        jsonify(
            {
                "color_palette": session["current_schedule"].color_palette,
                "events": session["current_schedule"].get_events(
                    json=True, schedule_number=schedule_number
                ),
            }
        ),
        200,
    )

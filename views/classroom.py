from flask import Blueprint
from flask import current_app as app
from flask import jsonify, render_template

import views.utils as utl

classroom = Blueprint("classroom", __name__, static_folder="../static")


@classroom.before_request
def before_classroom_request():
    utl.init_session()


@classroom.route("/")
def index():
    return render_template("classroom.html")


@classroom.route("/data", methods=["GET"])
def get_data():
    mng = app.config["MANAGER"]
    classrooms = mng.get_classrooms(return_json=True)

    return jsonify({"classrooms": classrooms}), 200


@classroom.route("/<id>/occupation", methods=["GET"])
def get_occupation(id):
    events = list()
    mng = app.config["MANAGER"]

    project_ids = mng.get_project_ids()
    for project_id in project_ids:
        events_in_classroom = mng.get_events_in_classroom(
            id, project_id=project_id["id"]
        )
        events.extend(map(lambda e: e.json("#2C3E50"), events_in_classroom))

    return (jsonify({"events": events}), 200)

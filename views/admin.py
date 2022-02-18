from flask import Blueprint
from flask import current_app as app
from flask import jsonify, render_template

from backend.security import roles_required

admin = Blueprint("admin", __name__, static_folder="../static")


@admin.route("/")
@roles_required("admin")
def index():
    return render_template("admin.html")


@admin.route("/data", methods=["GET"])
@roles_required("admin")
def get_data():
    mng = app.config["MANAGER"]
    plots = mng.get_plots()

    return jsonify(plots)

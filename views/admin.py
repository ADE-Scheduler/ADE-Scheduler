from flask import Blueprint, render_template
from flask import current_app as app
from flask_security import roles_required


admin = Blueprint("admin", __name__, static_folder="../static")


@admin.route("/")
@roles_required("admin")
def index():
    return render_template("admin.html")

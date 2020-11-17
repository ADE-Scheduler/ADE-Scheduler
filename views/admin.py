from flask import Blueprint, render_template
from flask_security import roles_required

admin = Blueprint("admin", __name__, static_folder="../static")


@roles_required("admin")
@admin.route("/")
def index():
    return render_template("admin.html")

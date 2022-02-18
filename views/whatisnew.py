from flask import Blueprint, render_template

whatisnew = Blueprint("whatisnew", __name__, static_folder="../static")


@whatisnew.route("/")
def index():
    return render_template("whatisnew.html")

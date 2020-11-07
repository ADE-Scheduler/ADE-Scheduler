from flask import Blueprint, render_template


whatisnew = Blueprint("whatisnew", __name__, static_folder="../static")


@whatisnew.before_request
def before_whatisnew_request():
    utl.init_session()


@whatisnew.route("/")
def index():
    return render_template("whatisnew.html")

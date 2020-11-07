from flask import Blueprint, render_template


help = Blueprint("help", __name__, static_folder="../static")


@help.before_request
def before_help_request():
    utl.init_session()


@help.route("/")
def index():
    return render_template("help.html")

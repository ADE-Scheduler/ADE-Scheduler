from flask import Blueprint, render_template

help = Blueprint("help", __name__, static_folder="../static")


@help.route("/")
def index():
    return render_template("help.html")

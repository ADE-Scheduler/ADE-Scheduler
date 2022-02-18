from flask import Blueprint, render_template

contribute = Blueprint("contribute", __name__, static_folder="../static")


@contribute.route("/")
def index():
    return render_template("contribute.html")

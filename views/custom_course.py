from flask import Blueprint, render_template

custom_course = Blueprint("custom_course", __name__, static_folder="../static")


@custom_course.route("/")
def index():
    return render_template("custom_course.html")

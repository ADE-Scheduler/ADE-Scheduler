from flask import current_app as app
from flask_babel import gettext
from flask_login import current_user
from flask import Blueprint, render_template, request
import requests
import csv
from ics import Calendar

custom_course = Blueprint("custom_course", __name__, static_folder="../static")


@custom_course.route("/")
def index():
    return render_template("custom_course.html")


@custom_course.route("/", methods=["POST"])
def add_custom_course():
    course = request.json

    try:
        cal = Calendar(requests.get(course["url"]).text)
    except Exception as e:
        print(e)
        return "Verify your url.", 400

    if not current_user.is_authenticated:
        return gettext("To save your schedule, you need to be logged in."), 401
    mng = app.config["MANAGER"]
    mng.save_ics_url(
        course["name"].upper(), course["url"], current_user, True
    )  # Automatically approved

    return "Your course has been created."

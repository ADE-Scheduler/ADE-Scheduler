from flask import Blueprint, render_template, flash, url_for, request, redirect
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
    print(course)
    # TODO: Instead of saving to a csv, call some other backend function.
    with open('custom_courses.csv', 'a') as f:
        write = csv.writer(f)
        write.writerow([course["name"], course["url"]])

    try:
        cal = Calendar(requests.get(course["url"]).text)
    except Exception as e:
        print(e)
        return "Verify your url.", 400

    return "Your course has been created."

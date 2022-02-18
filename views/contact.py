from flask import Blueprint, render_template

contact = Blueprint("contact", __name__, static_folder="../static")


@contact.route("/")
def index():
    return render_template("contact.html")

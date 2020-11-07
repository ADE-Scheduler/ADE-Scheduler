from flask import Blueprint, render_template


contact = Blueprint("contact", __name__, static_folder="../static")


@contact.before_request
def before_contact_request():
    utl.init_session()


@contact.route("/")
def index():
    return render_template("contact.html")

from flask import Blueprint, render_template, session
from flask_security import current_user


calendar = Blueprint('calendar', __name__, static_folder='../static')

@calendar.route('/')
def schedule_viewer():
    return render_template('calendar.html', **session)

from flask import Blueprint, render_template, session


calendar = Blueprint('calendar', __name__, static_folder='../static')

@calendar.route('/')
def schedule_viewer():
    return render_template('calendar.html', **session)

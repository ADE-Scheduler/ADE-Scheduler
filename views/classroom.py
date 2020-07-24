from flask import Blueprint, render_template


classroom = Blueprint('classroom', __name__, static_folder='../static')


@classroom.before_request
def before_classroom_request():
    pass


@classroom.route('/')
def index():
    return render_template('classroom.html')

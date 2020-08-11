from flask import Blueprint, render_template
from flask import current_app as app
from backend.classrooms import prettify_classrooms


classroom = Blueprint('classroom', __name__, static_folder='../static')


@classroom.route('/')
def index():
    mng = app.config['MANAGER']
    classrooms = mng.get_classrooms(search_dict={'code': 'BA'})

    # TODO: pour toi gillou
    print(prettify_classrooms(classrooms))

    return render_template('classroom.html')

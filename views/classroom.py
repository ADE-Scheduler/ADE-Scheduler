import math

from flask import current_app as app
from flask import Blueprint, render_template, jsonify


classroom = Blueprint('classroom', __name__, static_folder='../static')


@classroom.route('/')
def index():
    return render_template('classroom.html')


@classroom.route('/data', methods=['GET'])
def get_data():
    mng = app.config['MANAGER']
    classrooms = mng.get_classrooms(return_json=True)

    # TODO: Temporary fix !!
    for classroom in classrooms:
        if math.isnan(classroom['latitude']):
            classroom['latitude'] = None
            classroom['longitude'] = None

    return jsonify({
        'classrooms': classrooms
    }), 200


@classroom.route('/<code>/occupation', methods=['GET'])
def get_occupation(code):
    events = list()
    mng = app.config['MANAGER']
    project_ids = mng.get_project_ids()
    for project_id in project_ids:
        print(project_id['id'])
        classrooms = mng.get_courses(code, project_id=project_id['id'])
        for classroom in classrooms:
            events.extend([e.json('#2C3E50') for e in classroom.get_events()])

    # TODO faire un truc propre comme pour ade v1 @Jérome
    # ce truc marche mais il prend certains event qui sont pas au local per se
    return jsonify({
        'events': events,
    }), 200

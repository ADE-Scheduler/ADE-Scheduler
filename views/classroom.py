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

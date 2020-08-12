from flask import current_app as app
from flask import Blueprint, render_template, jsonify
from backend.classrooms import prettify_classrooms


classroom = Blueprint('classroom', __name__, static_folder='../static')


@classroom.route('/')
def index():
    return render_template('classroom.html')


@classroom.route('/data', methods=['GET'])
def get_data():
    mng = app.config['MANAGER']
    classrooms = mng.get_classrooms(return_json=True)
    print(classrooms)
    # TODO: wtf ça marche pas sur la page, pourtant le format est le même non ?
    return jsonify({
        'classrooms': classrooms
    }), 200

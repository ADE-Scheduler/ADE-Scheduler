from flask import Flask, render_template, request
import json
import sys

# BACK-END FILES
sys.path.insert(1, '../python')
from ade import getCoursesFromCodes
from static_data import Q1, Q2, Q3
from computation import parallel_compute

app = Flask(__name__)

codes_master = ['LELEC2660', 'LELEC2811', 'LMECA2755', 'LELEC2313', 'LELEC2531', 'LMECA2801', 'LELME2002']
codes = list()
data = list()
blocked = list()
basic_context = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # CODE ADDED BY USER
        if request.form['submit'] == 'Add':
            course_code = request.form.get("course_code", None)
            if course_code:
                # TODO: check le regex de course_code pour prevenir les erreurs user
                if course_code not in codes:
                    codes.append(course_code)
                    # TODO: fonction dans Course pour générer objet JSON pour directement afficher le cours
                    # TODO: afficher l'horaire "brut" du cours après addition du code

        # COMPUTATION REQUESTED BY USER
        if request.form['submit'] == 'Compute':
            # No course code was specified
            if len(codes) == 0:
                print('At least a course !')
                return render_template('calendar.html', data=json.dumps(data))

            # At least one course code was specified, time to compute !
            data.clear()
            c = getCoursesFromCodes(codes, Q1 + Q2, 9)
            year = parallel_compute(c)
            for week, score in year:
                for event in week[0]:
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name, 'editable': False,
                            'description': event.name+'\n'+event.location+' - '+str(event.duration)+'\n'+str(event.description)}
                    data.append(temp)
                    print(temp['description'])

        # CLEAR ALL
        if request.form['submit'] == 'Clear':
            data.clear()
            codes.clear()

    context = basic_context
    context['codes'] = codes
    return render_template('calendar.html', **context, data=json.dumps(data))


# To be chosed
@app.route('/tobecontinued')
def continued():
    return render_template('continued.html')


if __name__ == '__main__':
    app.run(debug=True, host='90.41.153.93')

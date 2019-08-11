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

basic_context = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['submit'] == 'Add':
            course_code = request.form.get("course_code", None)
            if course_code:
                # TODO: check le regex de course_code pour prevenir les erreurs user ?
                if course_code not in codes:
                    codes.append(course_code)
                print(codes)

        if request.form['submit'] == 'Compute':
            if len(codes) == 0:
                print('At least a course !')
                return render_template('calendar.html', data=json.dumps(data))
            print('Computing the calendar ! Please wait.')
            c = getCoursesFromCodes(codes, Q1 + Q2, 9)
            year = parallel_compute(c)
            for week, score in year:
                for event in week[0]:
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name}
                    data.append(temp)

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
    app.run(debug=True, host='0.0.0.0')

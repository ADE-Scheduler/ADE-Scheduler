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
                # TODO: afficher direct les cours après fetching ?
                if course_code not in codes:
                    codes.append(course_code)
                    # c = getCoursesFromCodes(codes, Q1+Q2, 9)
                    # for course in c:
                    #     data += course.getEventsJSON()

        # COMPUTATION REQUESTED BY USER
        if request.form['submit'] == 'Compute':
            # No course code was specified
            if len(codes) == 0:
                data.clear()
                print('At least a course !')
                return render_template('calendar.html', data=json.dumps(data), fts=json.dumps(blocked))

            # At least one course code was specified, time to compute !
            data.clear()
            c = getCoursesFromCodes(codes, Q1 + Q2, 9)
            year = parallel_compute(c)
            for week, score in year:
                for event in week[0]:
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name, 'editable': False,
                            'description': event.name+'\n'+event.location+' - '+str(event.duration)+'\n'+str(event.description)}
                    data.append(temp)

        # CLEAR ALL
        if request.form['submit'] == 'Clear':
            data.clear()
            codes.clear()

    context = basic_context
    context['codes'] = codes
    return render_template('calendar.html', **context, data=json.dumps(data), fts=json.dumps(blocked))

# To fetch the FTS
@app.route('/getFTS', methods=['POST'])
def getFTS():
    fts = json.loads(request.values.get('fts', None))
    blocked.clear()
    for el in fts:
        blocked.append(el)
    return render_template('calendar.html', **basic_context, data=json.dumps(data), fts=json.dumps(blocked))


# To remove the code
@app.route('/remove/code/<the_code>', methods=['POST'])
def remove_code(the_code):
    codes.remove(the_code)
    print(codes)
    return render_template('calendar.html', **basic_context, data=json.dumps(data), fts=json.dumps(blocked))


# To be chosed
@app.route('/tobecontinued')
def continued():
    return render_template('continued.html')


# Page for user's help guide
@app.route('/help')
def help_guide():
    return render_template('help.html')


# ERROR HANDLER

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

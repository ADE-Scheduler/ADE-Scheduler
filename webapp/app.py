from flask import Flask, render_template, request
import json
import sys, os, inspect
from pytz import timezone
from dateutil.parser import parse

# BACK-END FILES
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir+'/python')
from ade import getCoursesFromCodes
from static_data import Q1, Q2, Q3
from computation import parallel_compute
from event import CustomEvent


app = Flask(__name__)

codes_master = ['LELEC2660', 'LELEC2811', 'LMECA2755', 'LELEC2313', 'LELEC2531', 'LMECA2801', 'LELME2002']
codes = list()
data = list()
fts_json = list()
fts = list()
basic_context = {'up_to_date': True}

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
                    basic_context['up_to_date'] = False
                    codes.append(course_code)
                    # c = getCoursesFromCodes(codes, Q1+Q2, 9)
                    # for course in c:
                    #     data += course.getEventsJSON()

        # COMPUTATION REQUESTED BY USER
        if request.form['submit'] == 'Compute':
            basic_context['up_to_date'] = True
            # No course code was specified
            if len(codes) == 0:
                data.clear()
                print('At least a course !')
                return render_template('calendar.html', **basic_context, data=json.dumps(data), fts=json.dumps(fts_json))

            # At least one course code was specified, time to compute !
            data.clear()
            # TODO: Gérer les projectID sur le site et sur le back-end ! (proposer l'année scolaire en sélection ?)
            c = getCoursesFromCodes(codes, Q1+Q2+Q3, 9)
            year = parallel_compute(c, forbiddenTimeSlots=fts)
            for week, score in year:
                for event in week[0]:
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name, 'editable': False,
                            'description': event.name + '\n' + event.location + ' - ' + str(
                                event.duration) + '\n' + str(event.description)}
                    data.append(temp)

        # CLEAR ALL
        if request.form['submit'] == 'Clear':
            basic_context['up_to_date'] = True
            data.clear()
            codes.clear()
            fts_json.clear()
            fts.clear()

    context = basic_context
    context['codes'] = codes
    return render_template('calendar.html', **context, data=json.dumps(data), fts=json.dumps(fts_json))


# To fetch the FTS
@app.route('/getFTS', methods=['POST'])
def getFTS():
    msg = json.loads(request.values.get('fts', None))
    fts_json.clear()
    tz = timezone('Europe/Brussels')
    for el in msg:
        fts_json.append(el)
        t0 = parse(el['start']).astimezone(tz)
        t1 = parse(el['end']).astimezone(tz)
        dt = t1 - t0
        if el['title'] == 'High':
            fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=5))
        elif el['title'] == 'Medium':
            fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=3))
        elif el['title'] == 'Low':
            fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=1))
        else:
            print('This FTS was not recognized by the engine')
    return render_template('calendar.html', **basic_context, data=json.dumps(data), fts=json.dumps(fts_json))


# To remove the code
@app.route('/remove/code/<the_code>', methods=['GET'])
def remove_code(the_code):
    if the_code in codes:
        codes.remove(the_code)
        basic_context['up_to_date'] = False
    return render_template('calendar.html', **basic_context, data=json.dumps(data), fts=json.dumps(fts_json))


# Page for user preferences
@app.route('/preferences')
def preferences():
    return render_template('preferences.html')


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

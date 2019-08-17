from flask import Flask, render_template, request, redirect, url_for, make_response
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
from event import CustomEvent, EventCM

app = Flask(__name__)

codes_master = ['LELEC2660', 'LELEC2811', 'LMECA2755', 'LELEC2313', 'LELEC2531', 'LMECA2801', 'LELME2002']
codes = list()
data_base = list()
data_sched = list()
fts_json = list()
fts = list()
basic_context = {'up_to_date': True, 'safe_compute':None}

@app.route('/', methods=['GET', 'POST'])
def index():
    global data_base
    global codes

    if basic_context['safe_compute'] is None: # Also meaning that it is the first connection
        # Getting the cookies
        # Safe compute
        resp = make_response(render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json)))
        try:
            pref_safe_compute = request.cookies.get('safe-compute')
            if pref_safe_compute is None or pref_safe_compute == 'False':
                # Put some cookies
                basic_context['safe_compute'] = False
            elif pref_safe_compute == 'True':
                basic_context['safe_compute'] = True
        except:
            # Put some cookies
            basic_context['safe_compute'] = False

        # Last computed codes
        if request.method == 'GET' and len(codes) == 0:
            try:
                last_computed = request.cookies.get('last_computed')
                codes = last_computed.split()
                c = getCoursesFromCodes(codes, Q1+Q2+Q3, 9)
                for course in c:
                    data_base += course.getEventsJSON()
                year = parallel_compute(c, forbiddenTimeSlots=fts, nbest=5)
                for week, score in year:
                    for event in week[0]:
                        temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name, 'editable': False,
                                'description': event.name + '\n' + event.location + ' - ' + str(
                                    event.duration) + '\n' + str(event.description)}
                        data_sched.append(temp)
            except:
                pass
        
    if request.method == 'POST':
        # CODE ADDED BY USER
        if request.form['submit'] == 'Add':
            course_code = request.form.get("course_code", None)
            if course_code:
                if course_code not in codes:
                    basic_context['up_to_date'] = False
                    codes.append(course_code)
                    c = getCoursesFromCodes([course_code], Q1+Q2+Q3, 9)
                    for course in c:
                        data_base += course.getEventsJSON()
                    basic_context['codes'] = codes # Useless I think
            return render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json))

        # COMPUTATION REQUESTED BY USER
        if request.form['submit'] == 'Compute':
            basic_context['up_to_date'] = True

            # No course code was specified
            if len(codes) == 0:
                data_sched.clear()
                return render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json))

            # At least one course code was specified, time to compute !
            data_sched.clear()
            # TODO: Gérer les projectID sur le site et sur le back-end ! (proposer l'année scolaire en sélection ?)
            c = getCoursesFromCodes(codes, Q1+Q2+Q3, 9)
            year = parallel_compute(c, forbiddenTimeSlots=fts, nbest=5)
            #print(year)
            for week, score in year:
                for event in week[0]:
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name, 'editable': False,
                            'description': event.name + '\n' + event.location + ' - ' + str(
                                event.duration) + '\n' + str(event.description)}
                    data_sched.append(temp)
            resp = make_response(render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json)))
            # Update the last computed codes
            str_last_computed = " ".join(codes)
            resp.set_cookie('last_computed', str_last_computed)
            return resp

        # CLEAR ALL
        if request.form['submit'] == 'Clear':
            basic_context['up_to_date'] = True
            data_base.clear()
            data_sched.clear()
            codes.clear()
            fts_json.clear()
            fts.clear()
            basic_context['codes'] = codes
            return render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json))


    basic_context['codes'] = codes
    print(codes)
    return render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json))


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
        basic_context['up_to_date'] = False
    return render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json))


# To remove the code
@app.route('/remove/code/<the_code>', methods=['POST'])
def remove_code(the_code):
    global data_base
    if the_code in codes:
        codes.remove(the_code)
        basic_context['up_to_date'] = False
        data_base.clear()
        if len(codes) > 0:
            c = getCoursesFromCodes(codes, Q1 + Q2 + Q3, 9)
            for course in c:
                data_base += course.getEventsJSON()
    return render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=json.dumps(data_sched), fts=json.dumps(fts_json))


# Page for user preferences
@app.route('/preferences')
def preferences():
    try:
        pref_safe_compute = request.cookies.get('safe-compute')
        if pref_safe_compute is None or pref_safe_compute == 'False':
            # Put some cookies
            basic_context['safe_compute'] = False
        elif pref_safe_compute == 'True':
            basic_context['safe_compute'] = True
    except:
        # Put some cookies
        basic_context['safe_compute'] = False
    return render_template('preferences.html', **basic_context)


# Page for user's help guide
@app.route('/help')
def help_guide():
    return render_template('help.html')


# To handle the preferences form
# The method post garantees that we cannot go by url
@app.route('/change/preferences', methods=['POST'])
def preferences_changes():
    # Some work
    if request.method == 'POST':
        resp = make_response(redirect('/'))
        safe_compute_user = request.form.get('safe-compute')
        if safe_compute_user is None: # Not checked
            resp.set_cookie('safe-compute', 'False')
        else:
            resp.set_cookie('safe-compute', 'True')
    return resp

# ERROR HANDLER
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)

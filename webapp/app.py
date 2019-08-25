# BACK-END FILES
from app_calendar import *
from flask import Flask, request, url_for, render_template, redirect, make_response, send_file
from flask_babel import Babel
from flask_session import Session
from redis import Redis
import personnal_data


app = Flask(__name__)

# BABEL
app.config['LANGUAGES'] = ['en', 'fr']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'app/translations'

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host=personnal_data.my_ip, port=6379)     # '192.168.1.13' ou '127.0.0.1'

babel = Babel(app)
Session(app)


@babel.localeselector
def get_locale():
    if session.get('basic_context').get('locale') is None:
        session['basic_context']['locale'] = request.accept_languages.best_match(app.config['LANGUAGES'])
    locale = session['basic_context']['locale']
    return locale


@app.route('/locale/<locale>', methods=['GET'])
def locale_selector(locale):
    if request.method == 'GET':
        session['basic_context']['locale'] = locale
    return redirect(url_for('calendar'))


@app.route('/', methods=['GET', 'POST'])
def calendar():
    if not session.get('init'):
        init()

    if request.method == 'POST':
        # ADD CODE
        if request.form['submit'] == 'Add':
            code = request.form['course_code'].upper()
            add_course(code)
        # COMPUTE
        if request.form['submit'] == 'Compute':
            compute()
        # CLEAR
        if request.form['submit'] == 'Clear':
            clear()
    else:
        fetch_id()

    session['basic_context']['codes'] = session['codes']
    session.modified = True
    return render_template('calendar.html', **(session['basic_context']), data_base=json.dumps(session['data_base']),
                           data_sched=session['data_sched'], fts=json.dumps(session['fts']), id=session['id_tab'])


# To fetch the FTS
@app.route('/get/fts', methods=['POST'])
def getFTS():
    get_fts()
    return redirect(url_for('calendar'))


# To remove the code
@app.route('/remove/code/<code>', methods=['POST'])
def remove_code(code):
    delete_course(code)
    return redirect(url_for('calendar'))


# To fetch the IDs
@app.route('/get/id', methods=['POST'])
def getIDs():
    session['id_list'] = json.loads(request.form['IDs'])
    print(session['id_list'])
    return redirect(url_for('calendar'))


@app.route('/getCalendar')
def getCalendar():
    n = request.args.get('number', default=0, type=int)
    return send_file(library.getCalendar(n), as_attachment=True)


# Page for user preferences
@app.route('/preferences')
def preferences():
    # try:
    #     pref_safe_compute = request.cookies.get('safe-compute')
    #     if pref_safe_compute is None or pref_safe_compute == 'False':
    #         # Put some cookies
    #         basic_context['safe_compute'] = False
    #     elif pref_safe_compute == 'True':
    #         basic_context['safe_compute'] = True
    # except:
    #     # Put some cookies
    #     basic_context['safe_compute'] = False
    #
    # basic_context['codes'] = codes
    return render_template('preferences.html', **session['basic_context'])


# Page for user's help guide
@app.route('/help')
def help_guide():
    return render_template('help.html', **session['basic_context'])


# To handle the preferences form
# The method post garantees that we cannot go by url
@app.route('/change/preferences', methods=['POST'])
def preferences_changes():
    # Some work
    if request.method == 'POST':
        resp = make_response(redirect('/'))
        safe_compute_user = request.form.get('safe-compute')
        print(safe_compute_user)
        if safe_compute_user is None:  # Not checked
            resp.set_cookie('safe-compute', 'False')
        else:
            resp.set_cookie('safe-compute', 'True')
    return resp


# ERROR HANDLER
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# COOKIES HANDLER
def cookies_handler():
    global codes
    global data_base

    # Getting the cookies
    # Safe compute
    resp = make_response(
        render_template('calendar.html', **basic_context, data_base=json.dumps(data_base), data_sched=data_sched,
                        fts=json.dumps(fts_json), id=id_tab))
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
            c = getCoursesFromCodes(codes, Q1 + Q2 + Q3, 9)
            for course in c:
                data_base += course.getEventsJSON()
            scheds, score = parallel_compute(c, forbiddenTimeSlots=fts, nbest=3)
            i = 1
            for year in scheds:
                temp_sched = list()
                for week in year:
                    for event in week:
                        temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name,
                                'editable': False,
                                'description': event.name + '\n' + event.location + ' - ' + str(
                                    event.duration) + '\n' + str(event.description)}
                        temp_sched.append(temp)
                data_sched['sched_' + str(i)] = json.dumps(temp_sched)
                i += 1
        except:
            pass


if __name__ == '__main__':
    host = '0.0.0.0'
    host = '192.168.1.46'
    app.run(debug=True, host=host, port='5000')

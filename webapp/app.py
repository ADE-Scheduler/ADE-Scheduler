# BACK-END FILES
from app_calendar import *
from flask import Flask, request, url_for, render_template, redirect, make_response, send_file
from flask_babel import Babel
from flask_session import Session
***REMOVED***
import personnal_data


app = Flask(__name__)

# BABEL
app.config['LANGUAGES'] = ['en', 'fr']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'app/translations'
babel = Babel(app)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host=personnal_data.redis_ip, port=6379)
app.config['PERMANENT_SESSION_LIFETIME'] = 60*60*24
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
    get_id()
    return redirect(url_for('calendar'))


# To download the calendar's .ics file
@app.route('/download/schedule/<choice>', methods=['POST'])
def download(choice):
    print(int(choice))
    _cal = download_calendar(int(choice)-1)
    resp = make_response(_cal)
    resp.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
    return resp


@app.route('/getCalendar')
def getCalendar():
    n = request.args.get('number', default=0, type=int)
    return send_file(library.getCalendar(n), as_attachment=True)


# Page for user preferences
@app.route('/preferences')
def preferences():
    return render_template('preferences.html', **session['basic_context'])


# Page for user's help guide
@app.route('/help')
def help_guide():
    return render_template('help.html', **session['basic_context'])


# ERROR HANDLER
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', **session['basic_context']), 404


if __name__ == '__main__':
    host = personnal_data.local_ip
    app.run(debug=True, host=host)

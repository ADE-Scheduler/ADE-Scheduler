# Python imports
import os
import traceback
from datetime import timedelta
from jsmin import jsmin
from ics import Calendar

# Flask imports
from werkzeug.exceptions import InternalServerError
from flask import Flask, session, request, redirect, url_for, render_template, make_response
from flask_session import Session
from flask_security import Security, SQLAlchemyUserDatastore
from flask_login import user_logged_out
from flask_mail import Mail, Message
from flask_jsglue import JSGlue
from flask_babelex import Babel, _
from flask_migrate import Migrate
from flask_compress import Compress

# API imports
import backend.models as md
import backend.credentials as cd
import backend.servers as srv
import backend.ade_api as ade
import backend.manager as mng
import backend.schedules as schd
import backend.events as evt

# Views imports
from views.calendar import calendar
from views.account import account
from views.classroom import classroom
from views.help import help

# Setup app
app = Flask(__name__)
app.register_blueprint(calendar, url_prefix='/calendar')
app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(classroom, url_prefix='/classroom')
app.register_blueprint(help, url_prefix='/help')
app.config['SECRET_KEY'] = 'super-secret'   # TODO: change !
jsglue = JSGlue(app)

# Setup the API Manager
ade_api_credentials = cd.get_credentials(cd.ADE_API_CREDENTIALS)
manager = mng.Manager(ade.Client(ade_api_credentials), srv.Server(host='localhost', port=6379), md.db)
app.config['MANAGER'] = manager

# Setup Flask-Mail
mail_credentials = cd.get_credentials(cd.GMAIL_CREDENTIALS)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = mail_credentials['username']
app.config['MAIL_PASSWORD'] = mail_credentials['password']
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@' + app.config['MAIL_SERVER']
app.config['ADMINS'] = ['gillesponcelet98@gmail.com']   # TODO: mettez vos mails les boys
app.config['MAIL_MANAGER'] = Mail(app)

# Setup Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['ADE_DB_PATH']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
manager.database.init_app(app)
migrate = Migrate(app, manager.database)

# Setup Flask-Security
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'a_very_complex_and_indeciphrable_salt'  # TODO: change !
app.config['SECURITY_MANAGER'] = Security(app, SQLAlchemyUserDatastore(manager.database, md.User, md.Role))

# Setup Flask-Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = manager.server
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_MANAGER'] = Session(app)

# Allows compression of text assets
# If the server has automatic compression, comment this line.
compress = Compress(app)

# Setup Flask-Babel
app.config['LANGUAGES'] = ['en', 'fr']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel = Babel(app)


@babel.localeselector
def get_locale():
    if session.get('locale') is None:
        session['locale'] = request.accept_languages.best_match(app.config['LANGUAGES'])
    return session['locale']


app.jinja_env.globals['get_locale'] = get_locale


@app.route('/locale/<locale>')
def set_locale(locale):
    if locale in app.config['LANGUAGES']:
        session['locale'] = locale
    return redirect(request.args.get('next'))


@app.before_first_request
def before_first_request():
    if not os.path.exists('static/dist'):
        os.makedirs('static/dist')
    with open('static/dist/jsglue.min.js', 'w') as f:
        f.write(jsmin(jsglue.generate_js()))


# Reset current schedule on user logout
@user_logged_out.connect_via(app)
def when_user_logged_out(sender, user):
    session['current_schedule'] = schd.Schedule(manager.get_default_project_id())
    session['current_schedule_modified'] = False


# Main page
@app.route('/')
def welcome():
    if session.get('previous_user'):
        return redirect(url_for('calendar.index'))
    else:
        session['previous_user'] = True
        return render_template('welcome.html')


# Alert v1 users they need to update their schedule
@app.route('/getcalendar/<link>', methods=['GET'])
def update_notification(link):
    event = evt.RecurringCustomEvent(**{
        'name': 'There is a new ADE Scheduler version -- go check it now !',
        'location': 'https://ade-scheduler.info.ucl.ac.be',
        'description': 'The new version is GREAT !',
        'begin': '2020-01-01 08:00',
        'end': '2020-01-01 18:00',
        'freq': [0, 1, 2, 3, 4, 5, 6],
        'end_recurrence': '2021-12-31 18:00',
    })
    calendar = Calendar(events=[event])
    resp = make_response(str(calendar))
    resp.mimetype = 'text/calendar'
    resp.headers['Content-Disposition'] = 'attachment; filename=calendar.ics'
    return resp


# Error handlers
@app.errorhandler(InternalServerError)
def handle_exception(e):
    if not app.debug:
        error_details = str(traceback.format_exc())
        req_info = f'Exception on {request.path} [{request.method}]:'
        msg = Message(
            subject='ADE Scheduler Failure: ' + str(e.original_exception),
            body=req_info + '\n\n' + error_details,
            recipients=app.config['ADMINS'])
        app.config['MAIL_MANAGER'].send(msg)
    return 'Oops', 500


@app.errorhandler(404)
def page_not_found(e):
    return _('This URL does NOT exist... C\'mon !'), 404  # TODO: translation not detected ?


@app.shell_context_processor
def make_shell_context():
    return {
        'db': md.db,
        'Property': md.Property,
        'Schedule': md.Schedule,
        'Link': md.Link,
        'User': md.User,
        'mng': app.config['MANAGER'],
    }


if __name__ == '__main__':
    app.run(host=os.environ['ADE_FLASK_HOSTNAME'], debug=True)

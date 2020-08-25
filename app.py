# Python imports
import os
import traceback
from datetime import timedelta
from jsmin import jsmin
from ics import Calendar

# Flask imports
from werkzeug.exceptions import InternalServerError
from flask import Flask, session, request, redirect, url_for, render_template, make_response, g
from flask_session import Session
from flask_security import Security, SQLAlchemyUserDatastore
from flask_login import user_logged_out
from flask_mail import Mail, Message
from flask_jsglue import JSGlue
from flask_babelex import Babel, _
from flask_migrate import Migrate
from flask_compress import Compress
from flask_track_usage import TrackUsage
from flask_track_usage.storage.sql import SQLStorage

# API imports
import backend.models as md
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
from views.contact import contact
from views.api import api

# CLI commands
import cli

# Change current working directory to main directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Setup app
app = Flask(__name__, template_folder='static/dist/html')
app.register_blueprint(calendar, url_prefix='/calendar')
app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(classroom, url_prefix='/classroom')
app.register_blueprint(help, url_prefix='/help')
app.register_blueprint(contact, url_prefix='/contact')
app.register_blueprint(api, url_prefix='/api')
app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
jsglue = JSGlue(app)

# Register new commands
app.cli.add_command(cli.redis)
app.cli.add_command(cli.client)

# Setup the API Manager
app.config['ADE_API_CREDENTIALS'] = {
    'user': os.environ['ADE_USER'],
    'password': os.environ['ADE_PASSWORD'],
    'secret_key': os.environ['ADE_SECRET_KEY'],
    'url': os.environ['ADE_URL'],
    'data': os.environ['ADE_DATA'],
    'Authorization': os.environ['ADE_AUTHORIZATION'],
}
manager = mng.Manager(ade.Client(app.config['ADE_API_CREDENTIALS']), srv.Server(host='localhost', port=6379), md.db)
app.config['MANAGER'] = manager

# Setup Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@' + app.config['MAIL_SERVER']
app.config['ADMINS'] = [os.environ['MAIL_USERNAME']]
app.config['MAIL_MANAGER'] = Mail(app)

# Setup Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['ADE_DB_PATH']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
manager.database.init_app(app)
migrate = Migrate(app, manager.database)

# Setup Flask-Security
app.config['SECURITY_CONFIRMABLE'] = True
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = os.environ['FLASK_SALT']
app.config['SECURITY_CONFIRM_URL'] = '/confirm'
app.config['SECURITY_POST_REGISTER_VIEW'] = app.config['SECURITY_CONFIRM_URL']
app.config['SECURITY_MANAGER'] = Security(app, SQLAlchemyUserDatastore(manager.database, md.User, md.Role))

# Setup Flask-Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = manager.server
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=100)
app.config['SESSION_MANAGER'] = Session(app)

# Setup Flask-TrackUsage
app.config['TRACK_USAGE_COOKIE'] = True
app.config['TRACK_USAGE_USE_FREEGEOIP'] = False
app.config['TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS'] = 'exclude'
with app.app_context():
    storage = SQLStorage(db=manager.database)
t = TrackUsage(app, storage)

# Allows compression of text assets
# If the production server has automatic compression, comment this line,
# which is the case for the server on which ADE-Scheduler runs.
# compress = Compress(app)

# Setup Flask-Babel
app.config['LANGUAGES'] = ['en', 'fr']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel = Babel(app)


# Jinja filter for autoversionning
@app.template_filter('autoversion')
def autoversion_filter(filename):
    fullpath = os.path.join('', filename[1:])
    try:
        timestamp = str(os.path.getmtime(fullpath))
    except OSError:
        return filename
    newfilename = "{0}?{1}".format(filename, timestamp)
    return newfilename


# Babel's locale "getter/setter"
@babel.localeselector
def get_locale():
    if session.get('locale') is None:
        session['locale'] = 'fr'
    return session['locale']


app.jinja_env.globals.update(get_locale=get_locale)


@app.route('/locale/<locale>')
def set_locale(locale):
    if locale in app.config['LANGUAGES']:
        session['locale'] = locale
    return redirect(request.args.get('next'))


# Write jsglue.min.js
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
        g.track_var['new user'] = '+1'
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
    g.track_var['old user link'] = link
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
    return _('An error has occurred. Please contact the admins if it keeps happening.'), 500


@app.errorhandler(404)  # URL NOT FOUND
@app.errorhandler(405)  # METHOD NOT ALLOWED
def page_not_found(e):
    message = _('404 Page not found :(')
    return render_template('errorhandler/404.html', message=message)


# Shell context default exports
@app.shell_context_processor
def make_shell_context():
    return {
        'db': md.db,
        'Property': md.Property,
        'Schedule': md.Schedule,
        'Link': md.Link,
        'User': md.User,
        'mng': app.config['MANAGER'],
        't': storage,
    }

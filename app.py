# Python imports
import os
from datetime import timedelta

# Flask imports
from flask import Flask, session, request, redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_mail import Mail
from flask_assets import Environment
from flask_jsglue import JSGlue
from flask_babelex import Babel
from flask_migrate import Migrate

# API imports
import backend.models as md
import backend.credentials as cd
import backend.servers as srv
import backend.ade_api as ade
import backend.manager as mng

# Views imports
from views.calendar import calendar
from views.account import account
from views.classroom import classroom
from views.help import help

# Setup app
app = Flask(__name__)
app.register_blueprint(calendar, url_prefix='')
app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(classroom, url_prefix='/classroom')
app.register_blueprint(help, url_prefix='/help')
app.config['SECRET_KEY'] = 'super-secret'   # TODO: change !
jsglue = JSGlue(app)

# Setup the API Manager
ade_api_credentials = cd.get_credentials(cd.ADE_API_CREDENTIALS)
manager = mng.Manager(ade.Client(ade_api_credentials), srv.Server(host='localhost', port=6379), md.db)
app.config['MANAGER'] = manager

# Setup Flask-Assets
from util.assets import bundles
assets = Environment(app)
assets.register(bundles)

# Setup Flask-Mail
mail_credentials = cd.get_credentials(cd.GMAIL_CREDENTIALS)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = mail_credentials['username']
app.config['MAIL_PASSWORD'] = mail_credentials['password']
app.config['MAIL_DEFAULT_SENDER'] = mail_credentials['username']
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
    if not os.path.exists('static/gen'):
        os.makedirs('static/gen')
    with open('static/gen/jsglue.js', 'w') as f:
        f.write(jsglue.generate_js())


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

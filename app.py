# Python imports
import os
from datetime import timedelta

# Flask imports
from flask import Flask, render_template, url_for, redirect, request, session
from flask_session import Session
from flask_security import Security, SQLAlchemySessionUserDatastore
from flask_mail import Mail
from flask_assets import Environment

# API imports
import backend.database as db
import backend.models as md
import backend.credentials as cd
import backend.servers as srv
import backend.ade_api as ade
import backend.manager as mng

# Views imports
from views.calendar import calendar
from views.account import account


# Setup app
app = Flask(__name__)
app.register_blueprint(calendar, url_prefix='')
app.register_blueprint(account, url_prefix='/account')
app.config['SECRET_KEY'] = 'super-secret'   # TODO: change !

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

# Setup Flask-Security
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'a_very_complex_and_indeciphrable_salt'  # TODO: change !
app.config['SECURITY_MANAGER'] = Security(app, SQLAlchemySessionUserDatastore(db.session, md.User, md.Role))

# Setup Flask-Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = srv.Server(host='localhost', port=6379)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_MANAGER'] = Session(app)

# Setup the API Manager
ade_api_credentials = cd.get_credentials(cd.ADE_API_CREDENTIALS)
app.config['MANAGER'] = mng.Manager(ade.Client(ade_api_credentials), app.config['SESSION_REDIS'])


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == '__main__':
    app.run(host=os.environ['ADE_FLASK_HOSTNAME'], debug=True)

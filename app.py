# Python imports
import os
from datetime import timedelta

# Flask imports
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_mail import Mail
from flask_assets import Environment

# API imports
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

# Setup Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['ADE_DB_PATH']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
}
md.db.init_app(app)

# Setup Flask-Security
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'a_very_complex_and_indeciphrable_salt'  # TODO: change !
app.config['SECURITY_MANAGER'] = Security(app, SQLAlchemyUserDatastore(md.db, md.User, md.Role))

# Setup Flask-Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = srv.Server(host='localhost', port=6379)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SESSION_MANAGER'] = Session(app)

# Setup the API Manager
ade_api_credentials = cd.get_credentials(cd.ADE_API_CREDENTIALS)
app.config['MANAGER'] = mng.Manager(ade.Client(ade_api_credentials), app.config['SESSION_REDIS'])


if __name__ == '__main__':
    app.run(host=os.environ['ADE_FLASK_HOSTNAME'], debug=True)

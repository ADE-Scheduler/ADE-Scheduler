from flask import Flask, render_template, url_for, redirect, request, session
from flask_session import Session
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from flask_mail import Mail
from redis import Redis
from datetime import timedelta
from backend.database import db_session, init_db
from backend.models import Role, User  #, Link, Schedule
from backend.credentials import Credentials

# Setup app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'   # TODO: change !

# Setup Flask-Mail
mail_credentials = Credentials.get_credentials(Credentials.GMAIL_CREDENTIALS)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = mail_credentials['username']
app.config['MAIL_PASSWORD'] = mail_credentials['password']
app.config['MAIL_DEFAULT_SENDER'] = mail_credentials['username']
Mail(app)

# Setup Flask-Security
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'a_very_complex_and_indeciphrable_salt'  # TODO: change !
Security(app, SQLAlchemySessionUserDatastore(db_session, User, Role))

# Setup Flask-Session
app.config['SECRET_KEY'] = 'super-secret'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
Session(app)


@app.route('/')
def main():
    return render_template('calendar.html', **session)


@app.route('/account')
@login_required
def account():
    return render_template('account.html')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="10.42.0.1", debug=True)

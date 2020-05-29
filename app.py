from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_session import Session
from redis import Redis
from datetime import timedelta
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from flask_login import LoginManager, UserMixin, current_user, login_user
from backend.database import db_session, init_db
from backend.models import Role, User  #, Link, Schedule

# Setup app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'   # TODO: change !
app.config['SECURITY_SEND_REGISTER_MAIL'] = False

# Setup Flask-Security
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CHANGEABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'a_very_complex_and_indeciphrable_salt'  # TODO: change !
security = Security(app, SQLAlchemySessionUserDatastore(db_session, User, Role))

# Session
# secret_key = 'JYL_FRONT_END'  # TODO: change asbolutely
# app.secret_key = secret_key
app.config['SECRET_KEY'] = 'super-secret'
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_REDIS'] = Redis(host='localhost', port=6379)
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
# Session(app)


@app.route('/')
def main():
    return render_template('calendar.html', **session)


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="10.42.0.1", debug=True)
    # app.run(host="192.168.1.4", debug=True)

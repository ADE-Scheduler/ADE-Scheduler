# Python imports
import os
from datetime import timedelta

# Flask imports
from flask import Flask, render_template, url_for, redirect, request, session
from flask_session import Session
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from flask_mail import Mail

# API imports
import backend.database as db
import backend.models as md
import backend.credentials as cd
import backend.redis as rd

# Setup app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'   # TODO: change !

# Setup Flask-Mail
mail_credentials = cd.get_credentials(cd.GMAIL_CREDENTIALS)
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
Security(app, SQLAlchemySessionUserDatastore(db.session, md.User, md.Role))

# Setup Flask-Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = rd.conn
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
Session(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.route('/')
def main():
    return render_template('calendar.html', **session)


@app.route('/account')
@login_required
def account():
    return render_template('account.html')


if __name__ == '__main__':
    import diagnostics as diags

    # TODO: there is a class Credentials still somewhere in diagnostics :-)
    # print('Is everything ready to initialize ?')
    # ready, diagnostics = diags.ready_to_initialize()
    # if ready:
    #     print('\tEverything is clear!')
    # else:
    #     print('\tSome error(s) occured:', diagnostics)

    app.run(host=os.environ['ADE_FLASK_HOSTNAME'], debug=True)

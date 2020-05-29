from flask import Flask, render_template, url_for, redirect, request, flash
from flask_session import Session
from redis import Redis
from datetime import timedelta
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from flask_login import LoginManager, UserMixin, current_user, login_user
from backend.database import Database
from backend.models import Role, User  #, Link, Schedule

app = Flask(__name__)

# Redis for Session
redis = Redis(host='localhost', port=6379)

# Database
db = Database('test')
db_session = db.session

# Session
# secret_key = 'JYL_FRONT_END'  # TODO: change asbolutely
# app.secret_key = secret_key
app.config['SECRET_KEY'] = 'super-secret'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
app.config['SECURITY_REGISTERABLE'] = True

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)

security = Security(app, user_datastore)

login_manager = LoginManager()
login_manager.init_app(app)


# Create a user to test with
# @app.before_first_request
def create_user():
    # init_db()
    user_datastore.create_user(email='test@ade-scheduler.com', password_hash='42')
    db_session.commit()


# TODO: change but where ?
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def main():
    return render_template('calendar.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Already authenticated but goes to /login
        return redirect(url_for('main'))

    if request.method == 'GET':
        return render_template('login.html')

    # Assume POST
    email = request.form['email']
    password = request.form['password']
    remember_me = request.form.get('remember') is not None
    user = User.query.filter_by(username=email).first()
    if user is None or not user.check_password(password):
        print('passage')
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user, remember=remember_me)
    return redirect(url_for('main'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        print(request.form['email'])
        print(request.form['password'])
        return redirect(url_for('main'))

    # return render_template('security/register_user.html')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="10.42.0.1", debug=True)

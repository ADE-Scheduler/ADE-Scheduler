from flask import Flask, render_template, url_for, redirect, request, flash
from flask_session import Session
from redis import Redis
from datetime import timedelta
from flask_login import LoginManager, UserMixin, current_user, login_user

from backend.login import User

app = Flask(__name__)

# Redis for Session
redis = Redis(host='localhost', port=6379)

# Session
secret_key = 'JYL_FRONT_END'  # TODO: change asbolutely
app.secret_key = secret_key
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Login
login_manager = LoginManager()
login_manager.init_app(app)  # Handles the session creation


# TODO: change but where ?
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
def main():
    return render_template('calendar.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    print('coucou')
    if current_user.is_authenticated:  # Already authenticated but goes to /login
        return redirect(url_for('main'))
    
    if request.method == 'GET':
        return render_template('login.html')
    
    # Assume POST
    email = request.form['inputEmail']
    password = request.form['inputPassword']
    remember_me = request.form['rememberMe']
    user = User.query.filter_by(username=email).first()
    if user is None or not user.check_password(password):
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user, remember=remember_me)
    return redirect(url_for('main'))



@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run()
    # app.run(host="10.42.0.1")

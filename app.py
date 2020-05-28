from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('calendar.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


if __name__ == '__main__':
    # app.run()
    app.run(host="10.42.0.1")

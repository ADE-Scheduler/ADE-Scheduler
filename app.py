from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('calendar.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        print(request.form['email'])
        print(request.form['password'])
        if request.form.get('remember'):
            print('Remember me please senpai !')
        return redirect(url_for('main'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        print(request.form['email'])
        print(request.form['password'])
        return redirect(url_for('main'))

    return render_template('signup.html')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="10.42.0.1", debug=True)

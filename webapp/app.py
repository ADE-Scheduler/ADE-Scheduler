from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('calendar.html')

# To be chosed
@app.route('/tobecontinued')
def continued():
    return render_template('continued.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

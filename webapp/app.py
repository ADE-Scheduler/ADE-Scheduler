from flask import Flask, render_template
from flask import jsonify

app = Flask(__name__)


@app.route('/')
def index():
    # event = jsonify(title='MAY 2',
    #                 start='2019-08-11',
    #                 end='2019-08-12')
    title = 'MAY 2'
    start = '2019-08-11'
    end = '2019-08-12'
    return render_template('calendar.html', **locals())


# To be chosed
@app.route('/tobecontinued')
def continued():
    return render_template('continued.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

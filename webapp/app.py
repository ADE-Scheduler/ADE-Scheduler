from flask import Flask, render_template

app = Flask(__name__)

basic_context = {}
basic_context['name'] = 'Gilles'

@app.route('/')
def index():
    context = basic_context
    return render_template('calendar.html', **context)

# To be chosed
@app.route('/tobecontinued')
def continued():
    return render_template('continued.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
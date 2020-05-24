from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('calendar.html')


if __name__ == '__main__':
    # app.run()
    app.run(host="10.42.0.1")

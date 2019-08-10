from flask import Flask, render_template
import json

import sys

sys.path.insert(1, '../python')
from ade import getCoursesFromCodes
from static_data import Q1, Q2
from computation import parallel_compute

app = Flask(__name__)

basic_context = {'t': 'Gilles', 's': '2019-08-11', 'e': '2019-08-12'}

codes_master = ['LELEC2660', 'LELEC2811', 'LMECA2755', 'LELEC2313', 'LELEC2531', 'LMECA2801', 'LELME2002']
c = getCoursesFromCodes(codes_master, Q1 + Q2, 9)
year = parallel_compute(c)
to_send = list()
i = 0
for week, score in year:
    for event in week[0]:
        temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name}
        to_send.append(temp)
        i += 1
        print(i)

@app.route('/')
def index():
    data = to_send
    return render_template('calendar.html', data=json.dumps(data))


# To be chosed
@app.route('/tobecontinued')
def continued():
    return render_template('continued.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

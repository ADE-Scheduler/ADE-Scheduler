from ade import *
from computation import *
from events import *
from static_data import Q2, Q3
from ics import Calendar

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
projectID = 2
weeks = [21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 34, 35, 36]

c = getCoursesFromCodes(codes, Q2+Q3, projectID)
best, score = compute(c)

cal = Calendar()
for event in best:
    cal.events.add(event)

with open('my.ics', 'w') as f:
    f.writelines(cal)

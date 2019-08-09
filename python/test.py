from ade import *
from computation import *
from static_data import Q1, Q2, Q3
from ics import Calendar
from time import time

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
codes_master = ['LELEC2660', 'LELEC2811', 'LMECA2755', 'LELEC2313', 'LELEC2531', 'LMECA2801', 'LELME2002']
codes_info = ['lelec2531', 'lingi2241', 'lingi2255', 'lingi2261', 'lingi2266', 'lfsab2351']
codes_q5 = ['langl1873', 'lelec1530', 'lelec1755', 'lepl2351', 'lfsab1105', 'lmeca1451', 'lmeca1855', 'lmeca1901']


cal = Calendar()

# projectID: 2 pour 18-19 ou 9 pour 19-20
c = getCoursesFromCodes(codes_q5, Q1, 9)

year = parallel_compute(c)
for week, score in year:
    for event in week:
        cal.events.add(event)

# for week in range(53):
#     best, score = compute(c, week)
#     if score > 0:
#         print('Probleme avec la semaine numero '+str(week)+', score de: '+str(score))
#     for event in best:
#         cal.events.add(event)

with open('my.ics', 'w') as f:
    f.writelines(cal)

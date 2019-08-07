from ade import *
from computation import *
from static_data import Q1, Q2, Q3
from ics import Calendar

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
codes_master = ['LELEC2660', 'LELEC2811', 'LMECA2755', 'LELEC2313', 'LELEC2531', 'LMECA2801', 'LELME2002']
codes_info = ['lelec2531','lingi2241','lingi2255','lingi2261','lingi2266','lingi2142']
projectID = 2   # = 9 pour 2019-2020 !

cal = Calendar()
c = getCoursesFromCodes(codes_info, Q1+Q2+Q3, 9)
for week in range(53):
    best, score = compute(c, week)
    if score > 0:
        print('Probleme avec la semaine numero '+str(week)+', score de: '+str(score))
    for event in best:
        cal.events.add(event)

with open('my.ics', 'w') as f:
    f.writelines(cal)

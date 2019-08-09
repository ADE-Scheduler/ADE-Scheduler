from ade import *
from computation import *
from static_data import Q1, Q2, Q3
from ics import Calendar
from time import time

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
codes_master = ['LELEC2660', 'LELEC2811', 'LMECA2755', 'LELEC2313', 'LELEC2531', 'LMECA2801', 'LELME2002']
codes_info = ['lelec2531', 'lingi2241', 'lingi2255', 'lingi2261', 'lingi2266', 'lfsab2351']
projectID = 2  # = 9 pour 2019-2020 !

cal = Calendar()
t = time()
c = getCoursesFromCodes(codes_master, Q1 + Q2 + Q3, 9)
print('Time elapsed for fetching :', time()-t)

for course in c:
        t = time()
        # Les 4 fonctionnent, les deux meilleurs étant les deux premiers
        print(course.name, course.getSummary())
        #print(course.name, course.getSummary(weeks=slice(0,53)))
        #print(course.name, course.getSummary(weeks=range(53)))
        #print(course.name, course.getSummary(weeks=[3,4,5,6,7,8,9,10,25,26,27,28,29,30,31,33,35,40,45,50]))
        print('Time elapsed :', time()-t)

"""
year = parallel_compute(c)
for week, score in year:
    for event in week:
        cal.events.add(event)
        
"""

# for week in range(53):
#     best, score = compute(c, week)
#     if score > 0:
#         print('Probleme avec la semaine numero '+str(week)+', score de: '+str(score))
#     for event in best:
#         cal.events.add(event)

"""
with open('my.ics', 'w') as f:
    f.writelines(cal)
"""
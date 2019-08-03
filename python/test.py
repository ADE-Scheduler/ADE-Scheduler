from ade import *
from computation import *
from datetime import datetime, timedelta
import re

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
projectID = 2
weeks = [21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 34, 35]

cm, tp = getCoursesFromCodes(codes, weeks, projectID)

#for course in tp:
#    course.scheduling()

print(len(tp))
print(len(cm))

computation = Computation()

for course in cm:
    computation.add_course(course)
for t in tp:
    computation.add_course(t)

valid, courses = computation.compute(4)

print(len(valid))
print(len(courses))

for perm in valid:
    print(perm)
    print("NEW PERMUTATION\n-----------------------")
    for course in courses:
        print(course)
        print(perm[course.code])
        print('\n\n')
    print("----------------------\n")

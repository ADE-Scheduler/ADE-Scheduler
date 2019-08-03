from ade import *
from datetime import datetime, timedelta
import re

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
projectID = 2
weeks = [21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 33, 34, 35]

a = getCoursesFromCodes(codes, weeks, projectID)

for course in a:
    course.scheduling()
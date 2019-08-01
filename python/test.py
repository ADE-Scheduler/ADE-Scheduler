from ade import *
from datetime import datetime, timedelta
import re

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
projectID = 2
weeks = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]

d = getCoursesFromCodes(codes, weeks, projectID)
print(d)


# convertir les informations de getCoursesFromCodes en heure de début - heure de fin
duration = '2h'
date = '17/05/2019'
time = '14h00'

tdebut = datetime.strptime(date+'-'+time, '%d/%m/%Y-%Hh%M')
h, m = [0 if x is '' else int(x) for x in duration.split('h')]
dt = timedelta(hours=h, minutes=m)
tfin = tdebut + dt

print(tdebut)
print(tfin)

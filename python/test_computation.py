from computation import *
from ade import *
from static_data import Q1, Q2

codes = ['LELEC1310', 'LELEC1360', 'LINMA1510', 'LMECA1321', 'LMECA1100', 'LFSAB1508']
mes_cours = getCoursesFromCodes(codes, Q1+Q2)
for e in mes_cours:
    print(e)

semaine, score = compute(mes_cours)
print(semaine)
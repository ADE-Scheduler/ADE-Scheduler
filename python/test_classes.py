from cours import *
from slot import *
from datetime import datetime, timedelta

if __name__ == '__main__':
    a = CM("Autolin", "LINMA1510", "Denis Dochain", "denis@uc.c", Q = Q2, nb_weeks = 13)

    ########

    duration = '2h'
    date = '13/05/2019'
    date2 = '14/05/2019'
    time = '14h00'
    time2 = '12h01'

    tdebut = datetime.strptime(date+'-'+time, '%d/%m/%Y-%Hh%M')
    h, m = [0 if x is '' else int(x) for x in duration.split('h')]
    dt = timedelta(hours=h, minutes=m)
    tfin = tdebut + dt

    tdebut2 = datetime.strptime(date2+'-'+time2, '%d/%m/%Y-%Hh%M')
    h, m = [0 if x is '' else int(x) for x in duration.split('h')]
    dt = timedelta(hours=h, minutes=m)
    tfin2 = tdebut2 + dt

    slotA = Slot(tdebut, tfin)
    slotB = Slot(tdebut2, tfin2)
    slotC = Slot(tdebut, tfin)

    a.add_slot(slotA)
    a.add_slot(slotB)
    a.add_slot(slotC)
    a.scheduling()
    print(slotA.overlap(slotB))

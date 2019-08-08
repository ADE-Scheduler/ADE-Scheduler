from itertools import combinations, product
from event import overlappingTime
import math


def compute(courses, week, forbiddenTimeSlots=None):
    # List of all events in form of : [[ELEC TP1, ELEC TP2], [ELEC CM], [MATH TP1, MATH TP2, MATH TP3], ...]
    s = map(iter, filter(lambda e: len(e) != 0, sum((course.getweek(week) for course in courses), ())))

    # All possible weeks by selecting one element in each list of the list 's'
    perm = product(*s)

    # Best schedule
    best_score = math.inf
    best = None
    for weekEvents in perm:
        if best is None:
            best = weekEvents
        x = costFunction(weekEvents, forbiddenTimeSlots)
        if x < best_score:
            best_score = x
            best = weekEvents
    return best, best_score


def costFunction(weekEvents, forbiddenTimeSlots=None):
    """
    weekEvents : array of events.CustomeEvent - contains all the events of one week
    forbiddenTimeSlots : array of events.CustomEvent - contains all the time slots you want to be free
    """
    # do a n^2 comparison for all overlaps
    p = sum(overlappingTime(*e) for e in combinations(weekEvents, 2))

    if forbiddenTimeSlots:
        f = sum(overlappingTime(*e) for e in product(weekEvents, forbiddenTimeSlots))
        return p + f
    else:
        return p

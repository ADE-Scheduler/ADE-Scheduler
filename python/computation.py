from itertools import combinations, product
from event import  overlap
from concurrent.futures import ThreadPoolExecutor
import math

from time import time


def parallel_compute(courses, weeks=range(53), forbiddenTimeSlots=None, max_workers=53):
    """
    Calls the compute() function for all weeks using parallel programming
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(compute, *(courses, i, forbiddenTimeSlots)) for i in weeks]
        executor.shutdown(wait=True)

    return [future.result() for future in futures]


def compute(courses, week, forbiddenTimeSlots=None):
    """
    Generates all the possible schedules for a given week.
    Then evaluates all those possibilities to pick the best one(s).
    Parameters:
    -----------
    courses: list of course.Course
        The different courses to be added to the schedule
    week: int
        The number of the to-be-scheduled week
    forbiddenTimeSlots: list of event.CustomEvents
        The slots that are marked as "busy" by the user
    Returns:
    --------
    best: list of event.CustomEvents
        The best schedule according to the evaluation function (costFunction())
    best_score: int
        The score of said best schedule
    """
    # List of all events in form of : [[ELEC TP1, ELEC TP2], [ELEC CM], [MATH TP1, MATH TP2, MATH TP3], ...]
    #print('Start computing')
    #t1 = time()
    #print('Generating all possible permutations')
    #t2 = time()
    all_events = map(iter, filter(lambda e: len(e) != 0, sum((course.getweek(week) for course in courses), ())))

    # All possible weeks by selecting one element in each list of the list 's'
    perm = product(*all_events)

    #print('Time elapsed for generating... :', time()-t2)

    # Selecting the best possible schedule
    best_score = math.inf
    best = None
    #best = max(perm, key=lambda f:costFunction(f, forbiddenTimeSlots))
    
    for weekEvents in perm:
        if best is None:
            best = weekEvents
        x = costFunction(weekEvents, forbiddenTimeSlots)
        if x < best_score:
            best_score = x
            best = weekEvents

    #print('Time elapsed for computing :', time()-t1)
    return best, best_score


def costFunction(weekEvents, forbiddenTimeSlots=None):
    """
    Function that evaluates the "quality" of a given schedule based on diverse parameters
    Parameters:
    -----------
    weekEvents : array of event.CustomEvent
        The schedule that is to be evaluated (corresponding to a week)
    forbiddenTimeSlots: list of event.CustomEvents
        The slots that are marked as "busy" by the user
    Returns:
    --------
    int, the "cost" of this particular schedule
    """
    # do a n^2 comparison for all overlaps
    p = sum(overlap(*e) for e in combinations(weekEvents, 2))
    #p = sum(overlappingTime(*e) for e in combinations(weekEvents, 2))

    if forbiddenTimeSlots:
        f = sum(overlap(*e) for e in product(weekEvents, forbiddenTimeSlots))
        #f = sum(overlappingTime(*e) for e in product(weekEvents, forbiddenTimeSlots))
        return p + f
    else:
        return p

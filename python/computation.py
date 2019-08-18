from itertools import combinations, product, tee
from event import overlap, EventTP, EventCM, intersect
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from heapq import nsmallest
from functools import reduce
import operator


def parallel_compute(courses, weeks=range(53), forbiddenTimeSlots=None, nbest=5):
    """
   Calls the compute() function for all weeks using parallel programming
   """

    """ cela n'a jamais marche
   choice = 2
   if choice == 1:
       with ThreadPoolExecutor(max_workers=max_workers) as executor:
           futures = [executor.submit(compute, *(courses, i, forbiddenTimeSlots, nbest)) for i in weeks]
           executor.shutdown(wait=True)

       return [future.result() for future in futures]
   else:
   """
    # solution temporaire car j'ai pas le temps ajd
    # oktamer = [compute(courses, i, forbiddenTimeSlots, nbest=5) for i in weeks]
    sched = [[] for i in range(nbest)]
    scores = [[] for i in range(nbest)]
    for i in weeks:
        fd, p = compute(courses, i, forbiddenTimeSlots, nbest)
        if len(p) == 1:
            for j in range(nbest):
                sched[j].append(fd[0])
                scores[j].append(p[0])
        else:
            for j in range(nbest):
                sched[j].append(fd[j])
                scores[j].append(p[j])
    # sched = [horaire1, horaire2, horaire3,...] avec horaire contenant toutes les weeks
    # scores = [score1, score2, ...]
    print(len(sched[0]))
    return sched, scores


def compute(courses, week, forbiddenTimeSlots=None, nbest=5):
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
    nbest : int
        The n-bests weeks you want to save (lower is better for performance).
    Returns:
    --------
    best: list of lists of event.CustomEvents
        The n best schedules according to the evaluation function (costFunction())
    best_scores: list of int
        The scores of best schedules
    """

    mergeTypes = {EventTP, EventCM}
    priorTypes = {EventCM}

    # List of all events in form of : [[ELEC TP1, ELEC TP2], [ELEC CM], [MATH TP1, MATH TP2, MATH TP3], ...]
    # By default, EventOTHER are all chosen are accessed with Course.getEvent(self, weeks)[-1]
    def __extractAllEvents(courses, week, views=None):
        # We merge
        if views is None:
            # (Course 1, Course 2, ...), Course # = [CM, TP, ...]
            m_courses = sum((course.getWeek(week)[:-1] for course in courses), ())
        else:
            m_courses = sum((tuple(course.getView(week, view))[:-1] for course, view in zip(courses, views)), ())
        # We filter empty lists
        fm_courses = filter(lambda e: len(e) != 0, m_courses)
        return fm_courses
        

    all_events, all_events_bis = tee(__extractAllEvents(courses, week))

    safe_compute = True # Should be chosen by user if possible
    threshold = 0 # Arbitrary value
    # Under a certain amount of permutations, we remove TP that are conflicting CM and same TP at the same period

    if safe_compute:
        n_perm = reduce(operator.mul, (len(list(list_e)) for list_e in all_events_bis), 1)
        if n_perm > threshold:
            # views of courses where multiple TP at same period are omitted
            views = [course.mergeEvents(mergeTypes, week) for course in courses]

            # We remove all non-prior events that interesect prior events
            # !! List comprehesion read loop from left to right
            prior = (e for course in courses for eventType in priorTypes for e in course[eventType])
            non_prior = (e for course in courses for eventType in set(course.events.keys())-priorTypes for e in course[eventType])

            to_reject = [set(map(lambda t: t[1].getId(), 
                                filter(lambda t: intersect(t[0], t[1]), product(p, n)))) for p, n in zip(prior, non_prior)]

            views = [view-view_reject for view, view_reject in zip(views, to_reject)]

            all_events = __extractAllEvents(courses, week, views)
            

    # All possible weeks by selecting one element in each list of the list
    perm = product(*all_events)

    # Selecting the best possible schedule
    if nbest == 1:
        best = [min(perm, key=lambda f:costFunction(f, forbiddenTimeSlots))]
    else:
        best = nsmallest(nbest, perm, key=lambda f:costFunction(f, forbiddenTimeSlots))

    # Return best week + add all EventOTHER
    other = tuple(sum((course.getWeek(week)[-1] for course in courses),[]))
    return [best[i] + other for i in range(len(best))], [costFunction(week, forbiddenTimeSlots) for week in best]


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

    if forbiddenTimeSlots:
        f = sum(overlap(*e) for e in product(weekEvents, forbiddenTimeSlots))
        return p + f
    else:
        return p

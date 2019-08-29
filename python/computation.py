from itertools import combinations, product, chain
from event import overlap, EventTP, EventCM, EventORAL, EventEXAM, EventOTHER, intersect
from heapq import nsmallest
from functools import reduce
import operator
from static_data import N_WEEKS


def extractEvents(courses, weeks=None, view=None, eventTypes=None):
    """
    Return a generator containing len(weeks) elements, each
    being a list of all the possible events in form of :
        [[ELEC TP1, ELEC TP2], [ELEC CM1], [MATH TP1, MATH TP2, MATH TP3], ...]
    Allows passing a view to pre-select events.
    """
    # First we merge courses
    if eventTypes is None:
        eventTypes = {EventTP, EventCM, EventORAL, EventEXAM}
    else:
        eventTypes = set(eventTypes)

    courses_m = (course.getViews(weeks=weeks, views=view, eventTypes=eventTypes, swap=True, repeatView=True) for course
                 in courses)
    return [list(filter(None,
                        [list(filter(None,
                                     [weekEvent for weekEvent in weekEvents])) for course in weekCourses for weekEvents
                         in course])) for weekCourses in zip(*courses_m)]


def compute_best(courses, weeks=range(N_WEEKS), fts=None, nbest=5, safe_compute=True, mergeTypes={EventTP, EventCM},
            priorTypes={EventCM}, view=None):
    """
    Generates all the possible schedules for given weeks.
    Then evaluates all those possibilities to pick the best one(s).
    Parameters:
    -----------
    courses: list of course.Course
        The different courses to be added to the schedule
    week: iterable of int
        The number of the to-be-scheduled week
    fts: list of event.CustomEvents
        The slots that are marked as "busy" by the user
    nbest : int
        The n-bests weeks you want to save (lower is better for performance).
    Returns:
    --------
    best: list of lists of event.CustomEvents
        The n best schedules according to the evaluation function (costFunction())
    """

    events = extractEvents(courses, weeks, view=view)

    threshold = 10  # Arbitrary value
    # Under a certain amount of permutations, we remove TP that are conflicting CM and same TP at the same period

    best = [[] for i in range(nbest)]

    for weekEvents, week in zip(events, weeks):
        if safe_compute and weekEvents:
            n_perm = reduce(operator.mul, (len(list_e) for list_e in weekEvents), 1)
            if n_perm > threshold:
                if view: view = set(view)
                # views of courses where multiple TP at same period are omitted
                views = [course.mergeEvents(mergeTypes, week) for course in courses]

                # We remove all non-prior events that interesect prior events
                # !! List comprehesion read loop from left to right
                prior = (e for course in courses for eventType in priorTypes for e in course[eventType])
                non_prior = (e for course in courses for eventType in set(course.events.keys()) - priorTypes for e in
                             course[eventType])

                to_reject = [set(map(lambda t: t[1].getId(),
                                     filter(lambda t: intersect(t[0], t[1]), product(p, n)))) for p, n in
                             zip(prior, non_prior)]

                views = [view - view_reject for view, view_reject in zip(views, to_reject)]
                if view:
                    view = set.intersection(view, set.union(*views))
                else:
                    view = set.union(*views)
                weekEvents = extractEvents(courses, week, view=view)
                if events:
                    weekEvents = weekEvents[0]

        if weekEvents:
            # All possible weeks by selecting one element in each list of the list
            perm = product(*weekEvents)

            # Selecting the best possible schedule
            if nbest == 1:
                best.extend(min(perm, key=lambda f: costFunction(f, fts)))
            else:
                temp = nsmallest(nbest, perm, key=lambda f: costFunction(f, fts))
                n_temp = len(temp)
                for i in range(n_temp):
                    best[i].extend(temp[i])
                # If we could only find n_temp < nbest best scores, we fill the rest in with same values
                for j in range(n_temp, nbest):
                    best[j].extend(temp[-1])

    other = list(
        filter(None, list(chain(list(chain(extractEvents(courses, weeks=weeks, view=view, eventTypes={EventOTHER})))))))

    if other:
        return [best[i].extend(other) for i in range(nbest)]
    else:
        return best


def costFunction(weekEvents, fts=None):
    """
    Function that evaluates the "quality" of a given schedule based on diverse parameters
    Parameters:
    -----------
    weekEvents : array of event.CustomEvent
        The schedule that is to be evaluated (corresponding to a week)
    fts: list of event.CustomEvents
        The slots that are marked as "busy" by the user
    Returns:
    --------
    int, the "cost" of this particular schedule
    """
    # do a n^2 comparison for all overlaps
    p = sum(overlap(*e) for e in combinations(weekEvents, 2))

    if fts:
        f = sum(overlap(*e) for e in product(weekEvents, fts))
        return p + f
    else:
        return p

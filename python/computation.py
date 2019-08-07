from itertools import combinations, product
from event import overlappingTime
import math

def compute(courses, week, forbiddenTimeSlots=None):
    # All possible schedules
    all_courses = []
    for c in courses:
        cm, tp, exam, oral = c.getweek(week)
        if cm:
            all_courses.append(cm)
        if tp:
            all_courses.append(tp)
        if exam:
            all_courses.append(exam)
        if oral:
            all_courses.append(oral)
    perm = product(*all_courses)

    # Best schedule
    best_score = math.inf
    best = None
    for weekEvents in perm:
        if best is None:
            best = weekEvents
        x = costFunction(weekEvents)
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


class Computation:
    """
    Class defining the computation of a scheduling.
    For the moment, computed to work for a one-week schedule
    => Class not necessary, but for the moment, it is simpler to do so
    """

    def __init__(self):
        self.courses = []
        self.up_to_date = False
        self.valid = []
        self.working_courses = []

    def add_course(self, course):
        if not course in self.courses:
            self.courses.append(course)
        self.up_to_date = False
    
    def remove_course(self, course):
        if course in self.courses:
            self.courses.remove(course)
        self.up_to_date = False
    
    def add_valid_schedule(self, schedule):
        """
        Add the valid schedule in valid as a form of dictionnary
        @pre: schedule is a valid schedule
        @post: -
        """
        new_valid = {}
        for i, course in enumerate(self.courses):
            new_valid[course.code] = schedule[i]
        self.valid.append(new_valid)

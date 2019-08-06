import re
from static_data import COURSE_REGEX
from datetime import datetime, timedelta
from ics import Event


# Information extraction functions
def extractCode(code):
    s = re.search(COURSE_REGEX, code, re.IGNORECASE)
    if s:
        return s.group(1)
    else:
        return None

def extractType(course):
    if re.search(COURSE_REGEX + "_", course, re.IGNORECASE):
        return EventCM
    elif re.search(COURSE_REGEX + "-", course, re.IGNORECASE):
        return EventTP
    elif re.search(COURSE_REGEX + "=E", course, re.IGNORECASE):
        return EventEXAM
    else:
        return EventOTHER

def extractDateTime(date, time, delta):
    t0 = datetime.strptime(date + '-' + time, '%d/%m/%Y-%Hh%M')
    h, m = [0 if x is '' else int(x) for x in delta.split('h')]
    dt = timedelta(hours=h, minutes=m)
    t1 = t0 + dt
    return t0, t1, dt


# Event classes (from ics python package)
class CustomEvent(Event):
    def __init__(self, name, begin, duration, descr, loc, weight=1):
        super().__init__(name=name, begin=begin, duration=duration, description=descr, location=loc)
        self.weight = weight

    def __str__(self):
        return self.name + '\n' + str(self.begin) + ' --> ' + str(self.end)

    def getweek(self):
        """
        returns the week of this event in the gregorian calendar, starting at 0 for the first week
        """
        return self.begin.isocalendar()[1] - 1

class EventCM(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'Cours Magistral\n' + code + ' : ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)

class EventTP(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'Séance de TP\n' + code + ' : ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)

class EventEXAM(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'EXAMEN\n' + code + ' : ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)

class EventOTHER(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'Other\n' + code + ' : ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class Course:
    def __init__(self, code, name, weight=1):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight

        # A course can be composed of 4 different events: CM, TP, Exam and Other
        # Each individual event is classed by week
        self.CM = [[] for i in range(53)]
        self.TP = [[] for i in range(53)]
        self.E  = [[] for i in range(53)]
        self.Other = [[] for i in range(53)]

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.code == other.code
        else:
            raise TypeError

    def __str__(self):
        return self.code + ": " + self.name

    def addEvent(self, event):
        """
        Add an event to this course
        The event is added in the corresponding week
        If the event is already there, it is not added
        """
        week = event.getweek()
        if isinstance(event, EventCM):
            if event not in self.CM[week]:
                self.CM[week].append(event)
                return True
            else:
                return False
        elif isinstance(event, EventTP):
            if event not in self.TP[week]:
                self.TP[week].append(event)
                return True
            else:
                return False
        elif isinstance(event, EventEXAM):
            if event not in self.E[week]:
                self.E[week].append(event)
                return True
            else:
                return False
        elif isinstance(event, EventOTHER):
            if event not in self.Other[week]:
                self.Other[week].append(event)
                return True
            else:
                return False
        else:
            raise TypeError

    def removeEvent(self, event):
        """
        Removes an event from this course
        """
        week = event.getweek()
        if isinstance(event, EventCM):
            if event not in self.CM[week]:
                return False
            else:
                self.CM[week].remove(event)
                return True
        if isinstance(event, EventTP):
            if event not in self.TP[week]:
                return False
            else:
                self.TP[week].remove(event)
                return True
        if isinstance(event, EventEXAM):
            if event not in self.E[week]:
                return False
            else:
                self.E[week].remove(event)
                return True
        if isinstance(event, EventOTHER):
            if event not in self.Other[week]:
                return False
            else:
                self.Other[week].remove(event)
                return True
        else:
            raise TypeError
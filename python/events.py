import re
from static_data import COURSE_REGEX
from datetime import datetime, timedelta
from ics import Event
from pytz import timezone


# Information extraction functions
def extractCode(code):
    s = re.search(COURSE_REGEX, code, re.IGNORECASE)
    if s:
        return s.group(1)
    else:
        return ''


def extractType(course):
    if re.search(COURSE_REGEX + "-", course, re.IGNORECASE):
        return EventCM
    elif re.search(COURSE_REGEX + "_", course, re.IGNORECASE):
        return EventTP
    elif re.search(COURSE_REGEX + "=E", course, re.IGNORECASE):
        return EventEXAM
    elif re.search(COURSE_REGEX + "=O", course, re.IGNORECASE):
        return EventORAL
    else:
        return EventOTHER


def extractDateTime(date, time, delta):
    # We need to set the timzeone
    tz = timezone('Europe/Brussels')

    t0 = datetime.strptime(date + '-' + time, '%d/%m/%Y-%Hh%M').astimezone(tz)
    s = re.findall(r'[0-9]+', delta)
    if len(s) == 2:
        h = int(s[0])
        m = int(s[1])
    else:
        h = int(s[0])
        m = 0
    dt = timedelta(hours=h, minutes=m)
    t1 = t0 + dt
    return t0, t1, dt


def overlappingTime(event1, event2, onlyOverlap=True, saveCheck=True):
    if saveCheck and event1 == event2:  # No overlap if same event
        return 0
    if not isinstance(event2, CustomEvent):
        raise TypeError

    time = event1.weight * event2.weight * (
                min(event1.end, event2.end) - max(event1.begin, event2.begin)).total_seconds()
    if onlyOverlap:  # Only positive overlap is counted
        return max(time, 0)
    else:
        return time


# Event classes (from ics python package)
class CustomEvent(Event):
    def __init__(self, name, begin, duration, descr, loc, weight=1):
        super().__init__(name=name, begin=begin, duration=duration, description=descr, location=loc)
        self.weight = weight

    def __eq__(self, other):
        if isinstance(other, CustomEvent):
            return (self.name == other.name
                    and self.begin == other.begin
                    and self.duration == other.duration)
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    # Askip il faut rendre CustomEvent hashable pour pouvoir l'ajouter a un calendrier
    # et si on définit pas __hash__() ça fonctionne pas (héritage svp ? :'( )
    def __hash__(self):
        return super().__hash__()

    def getweek(self):
        """
        returns the week of this event in the gregorian calendar, starting at 0 for the first week
        """
        return self.begin.isocalendar()[1] - 1


class EventCM(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'CM: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventTP(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'TP: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventEXAM(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'EXAM: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventORAL(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'ORAL: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventOTHER(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'Other: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class Course:
    def __init__(self, code, name, weight=1):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight

        # A course can be composed of 4 different events: CM, TP, Exam and Other
        # Each event is classed by week
        self.CM = [[] for i in range(53)]
        self.TP = [[] for i in range(53)]
        self.E = [[] for i in range(53)]
        self.O = [[] for i in range(53)]
        self.Other = [[] for i in range(53)]

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.code == other.code
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.code + ": " + self.name

    def getweek(self, week):
        # Bon on gère pas encore les "Other".. trop chiant
        return self.CM[week], self.TP[week], self.E[week], self.O[week]

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
        elif isinstance(event, EventORAL):
            if event not in self.O[week]:
                self.O[week].append(event)
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
        if isinstance(event, EventORAL):
            if event not in self.O[week]:
                return False
            else:
                self.O[week].remove(event)
                return True
        if isinstance(event, EventOTHER):
            if event not in self.Other[week]:
                return False
            else:
                self.Other[week].remove(event)
                return True
        else:
            raise TypeError

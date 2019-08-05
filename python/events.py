from enum import Enum
import re # regex
from static_data import COURSE_REGEX
from datetime import datetime, timedelta

class EventType(Enum):
    CM = 1
    TP = 2
    E = 3 # Exams
    Other = 4 # For other events

def extractName(course):
    s = re.search(COURSE_REGEX, course, re.IGNORECASE)
    if s:
        return s.group(1)
    else:
        return None

def extractType(course):
    if re.search(COURSE_REGEX + "_", course, re.IGNORECASE):
        return EventType.CM
    elif re.search(COURSE_REGEX + "-", course, re.IGNORECASE):
        return EventType.TP
    elif re.search(COURSE_REGEX + "=E", course, re.IGNORECASE):
        return EventType.E
    else:
        return EventType.Other

class Course:
    def __init__(self, name, professor, CM=None, TP=None, E=None, Other=None):
        self.name = name
        self.professor = professor
        self.CM = CM
        self.TP = TP
        self.E = E
        self.Other = Other

class Event:
    def __init__(self, date_start, time_start, duration, title=None, location=None):
        self.title = title
        self.location = location
        self.start = datetime.strptime(date_start + '-' + time_start, '%d/%m/%Y-%Hh%M')
        self.end = datetime.strptime(date_start + '-' + time_start, '%d/%m/%Y-%Hh%M')
        self.duration = timedelta()

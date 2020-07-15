import re
from pytz import timezone
from ics import Event
from ics.utils import arrow_to_iso, get_arrow
from datetime import datetime
from backend.classrooms import merge_classrooms, Classroom
from backend.professors import Professor
from typing import Type, Tuple, Iterable, Optional

# We need to set the timezone
TZ = timezone('Europe/Brussels')
COURSE_REGEX = '([A-Z]+[0-9]+)'


class CustomEvent(Event):
    def __init__(self, name, location, description, begin, end):
        super().__init__(name=name, begin=begin, end=end, location=location, description=description)
        self.weight = 5     # default weight

    def __hash__(self) -> int:
        return super().__hash__()

    def intersects(self, other: 'AcademicalEvent') -> bool:
        """
        Returns whether two events intersect each other.

        :param other: the event to compare with
        :type other: AcademicalEvent
        :return: True if both events intersect
        :rtype: bool
        """
        return self.end > other.begin and other.end > self.begin  # not(A or B) = notA and notB

    __xor__ = intersects

    def overlap(self, other: 'CustomEvent') -> float:
        """
        If both events intersect, returns the product of the weights.

        :param other: the event to compare with
        :type other: AcademicalEvent
        :return: self.weight * other.weight if intersect, else 0
        :rtype: float
        """
        return self.weight * other.weight * self.intersects(other)

    __mul__ = overlap

    def get_week(self) -> int:
        """
        Returns the week of this event in the gregorian calendar, starting at 0 for the first week.

        :return: the week number relative to gregorian calendar numbering
        :rtype: int
        """
        return self.begin.isocalendar()[1] - 1

    def set_weight(self, weight: float) -> None:
        """
        Changes the weight of the event.

        :param weight: the weight
        :type weight: float
        """
        self.weight = weight

    def json(self) -> dict:
        """
        Returns the event as a json-like format.

        :return: a dictionary containing relevant information
        :rtype: dict
        """
        return {}


class RecurringCustomEvent(CustomEvent):
    """
    Represents a recurring event, formattable according to iCalendar's rules.
    """
    def __init__(self, name, location, description, begin, end, end_recurr, freq):
        super().__init__(name=name, location=location, description=description, begin=begin, end=end)
        self.end_recurr = get_arrow(end_recurr)
        self.freq = [int(i) for i in freq]

    def json(self) -> dict:
        """
        Returns the event as a json-like format.

        :return: a dictionary containing relevant information
        :rtype: dict
        """
        return {}

    def __str__(self):
        days = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']

        s = 'BEGIN:VEVENT\n'
        s += 'DTSTART:' + arrow_to_iso(self.begin) + '\n'
        s += 'DTEND:' + arrow_to_iso(self.end) + '\n'
        s += 'RRULE:FREQ=WEEKLY;INTERVAL=1;';
        s += 'BYDAY=' + ','.join([days[i] for i in self.freq]) + ';'
        s += 'UNTIL=' + arrow_to_iso(self.end_recurr) + '\n'
        if self.description:    s += 'DESCRIPTION:' + self.description + '\n'
        if self.location:       s += 'LOCATION:' + self.location + '\n'
        if self.name:           s += 'SUMMARY:' + self.name + '\n'
        if self.uid:            s += 'UID:' + self.uid + '\n'
        s += 'END:VEVENT'
        return s


class AcademicalEvent(CustomEvent):
    """
    An academical event is an object used to represent any event in the academical calendar.

    :param name: the name of the event
    :type name: str
    :param begin: the start of the event
    :type begin: datetime
    :param end: the end of the event
    :type end: datetime
    :param professor: the professor(s) in charge of this event
    :type professor: Professor
    :param classrooms: all the classrooms were this event takes place
    :type classrooms: Optional[List[Classroom]]
    :param id: the id of the event
    :type id: Optional[str]
    :param weight: the weight attributed to the event
    :type weight: float
    :param code: code of the course related to this event
    :type code: Optional[str]
    :param prefix: the prefix used for to describe the type of event
    :type prefix: Optional[str]
    """
    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Optional[Iterable[Classroom]] = None, id: Optional[str] = None, weight: float = 5,
                 code: Optional[str] = None, prefix: Optional[str] = None):

        super().__init__(name=f'{prefix} {code}-{name}', location='OMG FIX UR SHIT JEROM',
                         description=str(professor), begin=begin, end=end)
                         # TODO: merge_classrooms fait du gros caca ici
        self.weight = weight
        self.id = f'{prefix}{id}'
        self.code = code
        self.classrooms = classrooms

    def __repr__(self) -> str:
        tmp = self.id + ':' if self.id is not None else 'FTS:'
        return tmp + self.begin.strftime('%d/%m - %Hh%M') + ' to ' + self.end.strftime('%Hh%M')

    def __eq__(self, other: 'AcademicalEvent') -> bool:
        return (self.get_id() == other.get_id()
                and self.begin == other.begin
                and self.duration == other.duration)

    def __ne__(self, other: 'AcademicalEvent') -> bool:
        return not self.__eq__(other)

    def get_id(self) -> str:
        """
        Returns the id of this event.

        :return: the id of the event
        :rtype: str
        """
        return self.id

    def json(self) -> dict:
        """
        Returns the event as a json-like format.

        :return: a dictionary containing relevant information
        :rtype: dict
        """
        return {
            'start': str(self.begin),
            'end': str(self.end),
            'title': self.id,
            'editable': False,
            'description': self.name + '\n' + self.location + ' - ' + str(self.duration) + '\n' + str(self.description),
            'code': self.code
        }


class EventCM(AcademicalEvent):
    PREFIX = 'CM:'

    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Iterable[Classroom] = None, id: str = None, weight: float = 5,
                 code: str = None):
        super().__init__(name=name, begin=begin, end=end, professor=professor, classrooms=classrooms, id=id,
                         weight=weight, code=code, prefix=EventCM.PREFIX)


class EventTP(AcademicalEvent):
    PREFIX = 'TP:'

    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Iterable[Classroom] = None, id: str = None, weight: float = 5,
                 code: str = None):
        super().__init__(name=name, begin=begin, end=end, professor=professor, classrooms=classrooms, id=id,
                         weight=weight, code=code, prefix=EventTP.PREFIX)


class EventEXAM(AcademicalEvent):
    PREFIX = 'EXAM:'

    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Iterable[Classroom] = None, id: str = None, weight: float = 5,
                 code: str = None):
        super().__init__(name=name, begin=begin, end=end, professor=professor, classrooms=classrooms, id=id,
                         weight=weight, code=code, prefix=EventEXAM.PREFIX)


class EventORAL(AcademicalEvent):
    PREFIX = 'ORAL:'

    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Iterable[Classroom] = None, id: str = None, weight: float = 5,
                 code: str = None):
        super().__init__(name=name, begin=begin, end=end, professor=professor, classrooms=classrooms, id=id,
                         weight=weight, code=code, prefix=EventORAL.PREFIX)


class EventOTHER(AcademicalEvent):
    PREFIX = 'OTHER'

    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Iterable[Classroom] = None, id: str = None, weight: float = 5,
                 code: str = None):
        super().__init__(name=name, begin=begin, end=end, professor=professor, classrooms=classrooms, id=id,
                         weight=weight, code=code, prefix=EventOTHER.PREFIX)


def extract_code(course_id: str) -> str:
    """
    Extracts a code from a course id.

    :param course_id: str given by ADE API to represent the id
    :return: The code of the course. None if nothing matched the pattern required
    """
    s = re.search(COURSE_REGEX, course_id, re.IGNORECASE)
    if s:
        return s.group(1)
    else:
        return ''


def extract_type(course_type: str, course_id: str) -> Type[AcademicalEvent]:
    """
    Extract the type of Academical event from course type or course id.
    Sometimes, information from ADE API is wrong...
    :param course_type: str given by ADE API to represent the type
    :param course_id: str given by ADE API to represent the id
    :return: AcademicalEvent subclass
    """
    # We first try to detect the type with the ID regex
    if re.search(COURSE_REGEX + "-", course_id, re.IGNORECASE):
        return EventCM
    elif re.search(COURSE_REGEX + "_", course_id, re.IGNORECASE):
        return EventTP
    elif re.search(COURSE_REGEX + "=E", course_id, re.IGNORECASE) or \
            re.search(COURSE_REGEX + "=P", course_id, re.IGNORECASE):
        return EventEXAM
    elif re.search(COURSE_REGEX + "=O", course_id, re.IGNORECASE):
        return EventORAL

    # If it fails, we look at the given type (there are some mistakes in the data from ADE, not always trustworthy)
    elif course_type == 'Cours magistral':
        return EventCM
    elif course_type == 'TP' or 'TD':
        return EventTP
    elif course_type == 'Examen écrit' or type == 'Test / Interrogation / Partiel':
        return EventEXAM
    elif course_type == 'Examen oral':
        return EventORAL

    # The search failed, return the "Other" type
    else:
        return EventOTHER


def extract_datetime(date: str, start: str, end: str) -> Tuple[datetime, datetime]:
    """
    Parses info to return the start and end time of an event
    :param date: the date matching %d/%m/%Y format
    :type date: str
    :param start: the start hour matching %H:%M format
    :type start: str
    :param end: the end hour matching %H:%M format
    :type end: str
    :return: datetime objects (start date, end date)
    :rtype: Tuple[datetime, datetime]
    """
    t0 = datetime.strptime(date + '-' + start, '%d/%m/%Y-%H:%M').astimezone(TZ)
    t1 = datetime.strptime(date + '-' + end, '%d/%m/%Y-%H:%M').astimezone(TZ)
    if t0 < t1:
        return t0, t1
    else:
        return t1, t0

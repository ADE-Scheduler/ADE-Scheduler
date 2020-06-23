import re
from pytz import timezone
from ics import Event
from datetime import datetime
from backend.classrooms import merge_classrooms, Classroom
from backend.professors import Professor
from typing import Type, Tuple, Iterable

# We need to set the timezone
TZ = timezone('Europe/Brussels')
COURSE_REGEX = '([A-Z]+[0-9]+)'


class AcademicalEvent(Event):

    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Iterable[Classroom] = None, id: str = None, weight: float = 5,
                 code: str = None, prefix: str = None):

        super().__init__(name=f'{prefix} {code}-{name}',
                         begin=begin, end=end, description=str(professor),
                         location=merge_classrooms(classrooms).location())
        self.weight = weight
        self.id = f'{prefix}{id}'
        self.code = code
        self.classrooms = classrooms

    def __eq__(self, other: 'AcademicalEvent') -> bool:
        return (self.get_id() == other.get_id()
                and self.begin == other.begin
                and self.duration == other.duration)

    def __ne__(self, other: 'AcademicalEvent') -> bool:
        return not self.__eq__(other)

    def get_id(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return super().__hash__()

    def __repr__(self) -> str:
        tmp = self.id + ':' if self.id is not None else 'FTS:'
        return tmp + self.begin.strftime('%d/%m - %Hh%M') + ' to ' + self.end.strftime('%Hh%M')

    def set_weight(self, weight: float) -> None:
        self.weight = weight

    def json(self) -> dict:
        # TODO: fix ?
        return {'start': str(self.begin), 'end': str(self.end), 'title': self.id + '\n' + self.classrooms,
                'editable': False, 'description': self.name + '\n' + self.location + ' - ' +
                                                  str(self.duration) + '\n' + str(self.description), 'code': self.code}

    def intersects(self, other: 'AcademicalEvent') -> bool:
        return self.end > other.begin and other.end > self.begin  # not(A or B) = notA and notB

    __xor__ = intersects

    def overlap(self, other: 'AcademicalEvent') -> float:
        return self.weight * other.weight * self.intersects(other)

    __mul__ = overlap

    def get_week(self) -> int:
        """
        Returns the week of this event in the gregorian calendar, starting at 0 for the first week
        """
        return self.begin.isocalendar()[1] - 1


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
    :param date: str
    :param start: str
    :param end: str
    :return: datetime objects (start date, end date)
    """
    t0 = datetime.strptime(date + '-' + start, '%d/%m/%Y-%H:%M').astimezone(TZ)
    t1 = datetime.strptime(date + '-' + end, '%d/%m/%Y-%H:%M').astimezone(TZ)
    if t0 < t1:
        return t0, t1
    else:
        return t1, t0


def json_from_events(events):
    """
    TODO: edit
    Converts the events into a json-like format
    :param events: list of CustomEvents
    :return: list of dict
    """
    return [{'start': str(event.begin), 'end': str(event.end), 'title': event.id + '\n' + event.classroom, 'editable':
        False, 'code': event.code, 'description': event.name + '\n' + event.location + ' - ' + str(event.duration)
                                                  + '\n' + str(event.description)} for event in events]

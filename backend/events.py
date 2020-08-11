import re
from pytz import timezone
from ics import Event
from ics.utils import arrow_to_iso, get_arrow
from datetime import datetime
from backend.classrooms import merge_classrooms, Classroom
from backend.professors import Professor
from typing import Type, Tuple, Iterable, Optional, Union, Any, Dict

from flask_babelex import _

# We need to set the timezone
TZ = timezone('Europe/Brussels')
COURSE_REGEX = '([A-Z]+[0-9]+)'


class CustomEvent(Event):
    """
    Subclass of ics.Event, implementing more methods useful to know if two events are conflicting.

    :param weight: the weight of this event
    :type weight: Union[int, float]
    :param kwargs: parameters passed to :func:`ics.Event` constructor, but should as least contain :
        - name: str
        - begin: datetime
        - end: datetime
        - location: str
        - description: str
    :type kwargs: Any
    """

    def __init__(self, weight: Union[int, float] = 5, **kwargs: Any):
        super().__init__(**kwargs)
        self.weight = weight

    def __hash__(self) -> int:
        return super().__hash__()

    def intersects(self, other: 'CustomEvent') -> bool:
        """
        Returns whether two events intersect each other.

        :param other: the event to compare with
        :type other: CustomEvent
        :return: true if both events intersect
        :rtype: bool
        """
        return self.end > other.begin and other.end > self.begin  # not(a or b) = not(a) and not(b)

    __xor__ = intersects

    def overlap(self, other: 'CustomEvent') -> float:
        """
        If both events intersect, returns the product of the weights.

        :param other: the event to compare with
        :type other: CustomEvent
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

    def set_weight(self, weight: float):
        """
        changes the weight of the event.

        :param weight: the weight
        :type weight: float
        """
        self.weight = weight

    def json(self, color: str = '#9e742f') -> Dict[str, Any]:
        """
        Returns the event as a json-like format.

        :param color: the color of the event
        :type color: str
        :return: a dictionary containing relevant information
        :rtype: Dict[str, Any]
        """
        return {
            'id': self.uid,
            'title': self.name,
            'start': str(self.begin),
            'end': str(self.end),
            'location': self.location,
            'description': self.description,
            'editable': False,
            'backgroundColor': color,
            'borderColor': color,
        }


class RecurringCustomEvent(CustomEvent):
    """
    Subclass of CustomEvent, representing a recurring event, according to iCalendar's rules.

    :param end_recurrence: the end of the recurrence
    :type end_recurrence: datetime
    :param freq: the frequency of the recurrence
    :type freq: Iterable[str]
    :param kwargs: parameters passed to :func:`CustomEvent` constructor
    :type kwargs: Any
    """

    def __init__(self, end_recurrence, freq, **kwargs):
        super().__init__(**kwargs)
        self.end_recurrence = get_arrow(end_recurrence)
        self.freq = [int(i) for i in freq]

    def json(self, color='#8a7451'):
        r = super().json(color=color)
        del r['start']
        del r['end']
        days = [_('Sunday'), _('Monday'), _('Tuesday'), _('Wednesday'), _('Thursday'), _('Friday'), _('Saturday')]
        r.update(
            {
                'daysOfWeek': self.freq,
                'startTime': self.begin.format('hh:mmz'),
                'endTime': self.end.format('hh:mmz'),
                'starRecur': str(self.begin),
                'endRecur': str(self.end_recurrence),
                'rrule': {
                    'days': [days[i] for i in self.freq],
                    'start': str(self.begin),
                    'end': str(self.end_recurrence)
                }

            }
        )

        return r

    def __str__(self):
        days = ['su', 'mo', 'tu', 'we', 'th', 'fr', 'sa']
        return 'BEGIN:VEVENT\n'\
               f'DTSTART:{arrow_to_iso(self.begin)}\n'\
               f'DTEND:{arrow_to_iso(self.end)}\n'\
               f'RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY={",".join([days[i] for i in self.freq])};UNTIL={arrow_to_iso(self.end_recurrence)}\n'\
               f'DESCRIPTION:{self.description if self.description else ""}\n'\
               f'LOCATION:{self.location if self.location else ""}\n'\
               f'SUMMARY:{self.name if self.name else ""}\n'\
               f'UID:{self.uid if self.uid else ""}\n'\
               'END:VEVENT'


class AcademicalEvent(CustomEvent):
    """
    An academical event is an object used to represent any event in the academical calendar.

    It subclasses CustomEvent.

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
    :type weight: Union[int, float]
    :param code: code of the course related to this event
    :type code: Optional[str]
    :param prefix: the prefix used for to describe the type of event
    :type prefix: Optional[str]
    """

    def __init__(self, name: str, begin: datetime, end: datetime, professor: Professor,
                 classrooms: Optional[Iterable[Classroom]] = None, id: Optional[str] = None,
                 weight: Union[int, float] = 5,
                 code: Optional[str] = None, prefix: Optional[str] = None):
        super().__init__(name=name, location=merge_classrooms(classrooms).location(),
                         description=str(professor), begin=begin, end=end, weight=weight)
        # TODO: merge_classrooms fait du gros caca ici
        self.id = f'{prefix}{id}'
        self.code = code
        self.classrooms = classrooms

    def __hash__(self) -> int:
        return super().__hash__()

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

    def json(self, color=''):
        r = super().json(color=color)
        r.update(
            {
                'title': self.id,
                'description': f'{self.name}\n'
                               f'{str(self.location)}\n'
                               f'{str(self.duration)}\n'
                               f'{str(self.description)}',
                'code': self.code
            }
        )

        return r


class EventCM(AcademicalEvent):
    PREFIX = 'CM: '

    def __init__(self, **kwargs):
        super().__init__(prefix=EventCM.PREFIX, **kwargs)


class EventTP(AcademicalEvent):
    PREFIX = 'TP: '

    def __init__(self, **kwargs):
        super().__init__(prefix=EventTP.PREFIX, **kwargs)


class EventEXAM(AcademicalEvent):
    PREFIX = 'EXAM: '

    def __init__(self, **kwargs):
        super().__init__(prefix=EventEXAM.PREFIX, **kwargs)


class EventORAL(AcademicalEvent):
    PREFIX = 'ORAL: '

    def __init__(self, **kwargs):
        super().__init__(prefix=EventORAL.PREFIX, **kwargs)


class EventOTHER(AcademicalEvent):
    PREFIX = 'OTHER: '

    def __init__(self, **kwargs):
        super().__init__(prefix=EventOTHER.PREFIX, **kwargs)


def extract_code(course_id: str) -> str:
    """
    Extracts a code from a course id.

    :param course_id: str given by ADE API to represent the id
    :type course_id: str
    :return: The code of the course. None if nothing matched the pattern required
    :rtype: str
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

    :param course_type: string given by ADE API to represent the type
    :type course_type: str
    :param course_id: string given by ADE API to represent the id
    :type course_id: str
    :return: the type of the event
    :rtype: Type[AcademicalEvent]
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
    Parses infos to return the start and end time of an event.

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

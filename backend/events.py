import re
import unicodedata
from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple, Type, Union

from flask_babel import gettext
from ics import Event
from ics.utils import arrow_to_iso, get_arrow
from pytz import timezone

from backend.classrooms import Classroom, merge_classrooms
from backend.professors import Professor

# We need to set the timezone
TZ = timezone("Europe/Brussels")
COURSE_REGEX = "^([A-Z]+[0-9]+)"
PRETTY_HOUR_FORMAT = "HH:mm"
PRETTY_DATE_FORMAT = "DD/MM/YY"
PRETTY_FORMAT = "HH:mm - DD/MM/YY"


def pretty_hour_formatter(arrow) -> str:
    return arrow.format(PRETTY_HOUR_FORMAT).replace(":", "h")


def pretty_date_formatter(arrow) -> str:
    return arrow.format(PRETTY_DATE_FORMAT)


def pretty_formatter(arrow) -> str:
    return f"{pretty_hour_formatter(arrow)} - {pretty_date_formatter(arrow)}"


def remove_accents(input_str: str) -> str:
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def sanitize_string(input_str: str) -> str:
    return remove_accents(input_str).lower()


def remove_prefix(s: str, prefix: str) -> str:
    if s.startswith(prefix):
        return s[len(prefix) :]
    return s


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

    DEFAULT_COLOR = "#9e742f"

    def __init__(self, weight: Union[int, float] = 5, **kwargs: Any):
        super().__init__(**kwargs)
        self.weight = weight
        self.color = CustomEvent.DEFAULT_COLOR

    def __getattr__(self, item):
        if item == "color" and not hasattr(super(), "color"):
            setattr(self, "color", self.DEFAULT_COLOR)
            return self.DEFAULT_COLOR
        else:
            return super().__getattr__(item)

    def __hash__(self) -> int:
        return super().__hash__()

    def intersects(self, other: "CustomEvent") -> bool:
        """
        Returns whether two events intersect each other.

        :param other: the event to compare with
        :type other: CustomEvent
        :return: true if both events intersect
        :rtype: bool
        """
        return (
            self.end > other.begin and other.end > self.begin
        )  # not(a or b) = not(a) and not(b)

    __xor__ = intersects

    def overlap(self, other: "CustomEvent") -> float:
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

    def json(self, color: str = None) -> Dict[str, Any]:
        """
        Returns the event as a json-like format.

        :param color: the color of the event
        :type color: str
        :return: a dictionary containing relevant information
        :rtype: Dict[str, Any]
        """

        if color is None:
            color = self.color

        return {
            "id": self.uid,
            "title": self.name,
            "start": str(self.begin),
            "end": str(self.end),
            "location": self.location,
            "description": self.description,
            "editable": False,
            "backgroundColor": color,
            "borderColor": color,
            "pretty_start": pretty_formatter(self.begin),
            "pretty_end": pretty_formatter(self.end),
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

    DEFAULT_COLOR = "#8a7451"

    def __init__(self, end_recurrence, freq, **kwargs):
        super().__init__(**kwargs)
        self.end_recurrence = get_arrow(end_recurrence)
        self.freq = [int(i) for i in freq]
        self.color = RecurringCustomEvent.DEFAULT_COLOR

    def json(self, color=None):
        if color is None:
            color = self.color

        r = super().json(color=color)
        del r["start"]
        del r["end"]
        DAYS = [
            gettext("Sunday"),
            gettext("Monday"),
            gettext("Tuesday"),
            gettext("Wednesday"),
            gettext("Thursday"),
            gettext("Friday"),
            gettext("Saturday"),
        ]

        self.freq.sort()

        r.update(
            {
                "daysOfWeek": self.freq,
                "startTime": self.begin.format("HH:mm"),
                "endTime": self.end.format("HH:mm"),
                "pretty_startTime": pretty_hour_formatter(self.begin),
                "pretty_endTime": pretty_hour_formatter(self.end),
                "startRecur": self.begin.format(),
                "endRecur": self.end_recurrence.format(),
                "rrule": {
                    "days": [DAYS[i] for i in self.freq],
                    "start": str(self.begin),
                    "end": str(self.end),
                    "pretty_days": ", ".join(DAYS[i] for i in self.freq),
                    "pretty_start": f"{DAYS[(self.begin.weekday() + 1) % 7]} {self.begin.format(PRETTY_DATE_FORMAT)}",
                    "pretty_end": f"{DAYS[(self.end_recurrence.weekday() + 1) % 7]} {self.end_recurrence.format(PRETTY_DATE_FORMAT)}",
                },
            }
        )

        return r

    def __str__(self):
        days = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
        rrule = (
            f"RRULE:FREQ=WEEKLY;"
            f"INTERVAL=1;"
            f'BYDAY={",".join([days[i] for i in self.freq])};'
            f"UNTIL={arrow_to_iso(self.end_recurrence)} "
        )
        s = super().__str__()
        lines = s.splitlines()
        lines.insert(-1, rrule)
        return "\n".join(lines)


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
    :param note: a note to be added to the event description
    :type str: Optional[str]
    """

    KEYWORDS = ()

    def __init__(
        self,
        name: str,
        begin: datetime,
        end: datetime,
        professor: Professor,
        classrooms: Optional[Iterable[Classroom]] = None,
        id: Optional[str] = None,
        weight: Union[int, float] = 5,
        code: Optional[str] = None,
        prefix: Optional[str] = None,
        note: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            location=merge_classrooms(classrooms).location() if classrooms else "",
            description=str(professor),
            begin=begin,
            end=end,
            weight=weight,
        )
        self.id = f"{prefix}{id}"
        self.code = code
        self.classrooms = classrooms
        self.description = (
            f"{self.name}\n" f"{str(self.duration)}\n" f"{self.description}"
        )
        self.note = note

        if self.note:
            self.description = f"{self.description}\n{self.note}"

        if name is None or len(name) == 0:  # Fix for special events with no name
            self.name = id
        else:
            self.name = f"{prefix}{self.name}"

    def __hash__(self) -> int:
        return super().__hash__()

    def __repr__(self) -> str:
        tmp = self.id + ":" if self.id is not None else "FTS:"
        return (
            tmp
            + self.begin.strftime("%d/%m - %Hh%M")
            + " to "
            + self.end.strftime("%Hh%M")
        )

    def __eq__(self, other: "AcademicalEvent") -> bool:
        return (
            self.get_id() == other.get_id()
            and self.begin == other.begin
            and self.duration == other.duration
        )

    def __ne__(self, other: "AcademicalEvent") -> bool:
        return not self.__eq__(other)

    @classmethod
    def matches(cls, string):
        return any(kw in string for kw in cls.KEYWORDS)

    def get_id(self) -> str:
        """
        Returns the id of this event.

        :return: the id of the event
        :rtype: str
        """
        return self.id

    def json(self, color=""):
        r = super().json(color=color)
        r.update(
            {"title": self.name, "description": self.description, "code": self.code}
        )

        # Remove empty lines
        r["description"] = "\n".join(
            line for line in r["description"].splitlines() if line
        )

        return r


class EventCM(AcademicalEvent):
    PREFIX = "CM: "
    KEYWORDS = ("cm", "cours", "magistral")

    def __init__(self, **kwargs):
        super().__init__(prefix=EventCM.PREFIX, **kwargs)


class EventTP(AcademicalEvent):
    PREFIX = "TP: "
    KEYWORDS = ("tp", "td", "ape", "app")

    def __init__(self, **kwargs):
        super().__init__(prefix=EventTP.PREFIX, **kwargs)


class EventEXAM(AcademicalEvent):
    PREFIX = "EXAM: "
    KEYWORDS = ("partiel", "ecrit", "oral", "interro", "test")

    def __init__(self, **kwargs):
        super().__init__(prefix=EventEXAM.PREFIX, **kwargs)


class EventORAL(AcademicalEvent):
    PREFIX = "ORAL: "
    KEYWORDS = ("oral",)

    def __init__(self, **kwargs):
        super().__init__(prefix=EventORAL.PREFIX, **kwargs)


class EventLABO(AcademicalEvent):
    PREFIX = "LABO: "
    KEYWORDS = "labo"

    def __init__(self, **kwargs):
        super().__init__(prefix=EventLABO.PREFIX, **kwargs)


class EventOTHER(AcademicalEvent):
    PREFIX = "OTHER: "
    KEYWORDS = ("autre", "info", "monitorat", "consult", "copie")

    def __init__(self, **kwargs):
        super().__init__(prefix=EventOTHER.PREFIX, **kwargs)


class EventEXTERN(AcademicalEvent):
    PREFIX = "EXT: "
    KEYWORDS = ("extern",)

    def __init__(self, **kwargs):
        super().__init__(prefix=EventEXTERN.PREFIX, **kwargs)
        self.name = remove_prefix(self.name, self.PREFIX)

    @classmethod
    def from_event(cls, event: Event, code: str) -> "EventEXTERN":
        e = cls(
            id=event.name,
            code=code,
            name=event.name,
            begin=event.begin,
            end=event.end,
            professor=event.description,
        )
        e.location = event.location or ""
        return e


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
        return ""


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
    # We look at the given type (there are some mistakes in the data from ADE,
    # not always trustworthy)

    course_type = sanitize_string(course_type)

    classes = (EventCM, EventTP, EventEXAM, EventORAL, EventOTHER, EventLABO)

    for cls in classes:
        if cls.matches(course_type):
            return cls

    # Then try regex matching
    if re.search(COURSE_REGEX + "=E", course_id, re.IGNORECASE) or re.search(
        COURSE_REGEX + "=P", course_id, re.IGNORECASE
    ):
        return EventEXAM
    elif re.search(COURSE_REGEX + "=O", course_id, re.IGNORECASE):
        return EventORAL
    elif re.search(COURSE_REGEX + r"\-", course_id, re.IGNORECASE):
        return EventCM
    elif re.search(COURSE_REGEX + "_", course_id, re.IGNORECASE):
        return EventTP

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
    t0 = datetime.strptime(date + "-" + start, "%d/%m/%Y-%H:%M").astimezone(TZ)
    t1 = datetime.strptime(date + "-" + end, "%d/%m/%Y-%H:%M").astimezone(TZ)
    if t0 < t1:
        return t0, t1
    else:
        return t1, t0

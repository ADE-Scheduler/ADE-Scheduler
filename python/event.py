import re
from static_data import COURSE_REGEX
from datetime import datetime
from ics import Event
from pytz import timezone

# We need to set the timezone
tz = timezone('Europe/Brussels')


def extractCode(code: str):
    """
    Extracts the course code from a string. Any course should start with something like
        " LEPL1104 "
    Parameters:
    -----------
    code : str
        The string from which the code is to be extracted.
    Returns:
    --------
    s : str
        The code of the course. None if nothing matched the pattern required
    """
    s = re.search(COURSE_REGEX, code, re.IGNORECASE)
    if s:
        return s.group(1)
    else:
        return ''


def extractType(ctype: str, cid: str):
    """
    # TODO
    :param ctype:
    :param cid:
    :return:
    """
    # We first try to detect the type with the ID regex
    if re.search(COURSE_REGEX + "-", cid, re.IGNORECASE):
        return EventCM
    elif re.search(COURSE_REGEX + "_", cid, re.IGNORECASE):
        return EventTP
    elif re.search(COURSE_REGEX + "=E", cid, re.IGNORECASE) or re.search(COURSE_REGEX + "=P", cid, re.IGNORECASE):
        return EventEXAM
    elif re.search(COURSE_REGEX + "=O", cid, re.IGNORECASE):
        return EventORAL

    # If it fails, we look at the given type (there are some mistakes in the data from ADE, not always trustworthy)
    elif ctype == 'Cours magistral':
        return EventCM
    elif ctype == 'TP' or 'TD':
        return EventTP
    elif ctype == 'Examen écrit' or type == 'Test / Interrogation / Partiel':
        return EventEXAM
    elif ctype == 'Examen oral':
        return EventORAL

    # The search failed, return the "Other" type
    else:
        return EventOTHER


def extractDateTime(date, start, end):
    """
    # TODO
    :param date:
    :param start:
    :param end:
    :return:
    """
    t0 = datetime.strptime(date + '-' + start, '%d/%m/%Y-%H:%M').astimezone(tz)
    t1 = datetime.strptime(date + '-' + end, '%d/%m/%Y-%H:%M').astimezone(tz)
    if t0 < t1:
        return t0, t1
    else:
        return t1, t0


def event_prefix(event_type):
    """
    # TODO
    :param event_type:
    :return:
    """
    if event_type == EventTP:
        return 'TP:'
    elif event_type == EventCM:
        return 'CM:'
    elif event_type == EventEXAM:
        return 'EXAM:'
    elif event_type == EventORAL:
        return 'ORAL:'
    else:
        return 'Other:'


def JSONfromEvents(events):
    """
    # TODO s'en débarasser (utiliser la fonction de la classe Course...)
    :param events:
    :return:
    """
    return [{'start': str(event.begin), 'end': str(event.end), 'title': event.id + '\n' + event.location, 'editable':
            False, 'code': event.code, 'description': event.name + '\n' + event.location + ' - ' + str(event.duration)
            + '\n' + str(event.description)} for event in events]


# Event classes (subclasses of ics.Event)
class CustomEvent(Event):
    def __init__(self, name, begin, end, descr, loc, id=None, weight=5, code=None):
        super().__init__(name=name, begin=begin, end=end, description=descr, location=loc)
        self.weight = weight
        self.id = id
        self.code = code

    def __eq__(self, other):
        if isinstance(other, CustomEvent):
            return (self.getId() == other.getId()
                    and self.begin == other.begin
                    and self.duration == other.duration)
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def getId(self):
        return self.id

    def __hash__(self):
        return super().__hash__()

    def __repr__(self):
        tmp = self.id + ':' if self.id is not None else 'FTS:'
        return tmp + self.begin.strftime('%d/%m - %Hh%M') + ' to ' + self.end.strftime('%Hh%M')

    def set_weight(self, weight):
        self.weight = weight

    def __str__(self):
        return repr(self)

    def json(self):
        return {'start': str(self.begin), 'end': str(self.end), 'title': self.id + '\n' + self.location,
                'editable': False, 'description': self.name + '\n' + self.location + ' - ' +
                str(self.duration) + '\n' + str(self.description), 'code': self.code}

    def intersects(self, other):
        return self.end > other.begin and self.end > other.begin  # not(A or B) = notA and notB

    __xor__ = intersects

    def overlap(self, other):
        return self.weight * other.weight * self.intersects(other)

    __mul__ = overlap

    def get_week(self):
        """
        returns the week of this event in the gregorian calendar, starting at 0 for the first week
        """
        return self.begin.isocalendar()[1] - 1


class EventCM(CustomEvent):
    def __init__(self, begin, end, code, name, professor, loc, id=None, weight=5):
        name = 'CM: ' + code + ' - ' + name
        id = 'CM:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, id=id, weight=weight,
                         code=code)


class EventTP(CustomEvent):
    def __init__(self, begin, end, code, name, professor, loc, id=None, weight=5):
        name = 'TP: ' + code + ' - ' + name
        id = 'TP:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, id=id, weight=weight,
                         code=code)


class EventEXAM(CustomEvent):
    def __init__(self, begin, end, code, name, professor, loc, id=None, weight=5):
        name = 'EXAM: ' + code + ' - ' + name
        id = 'EXAM:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, id=id, weight=weight,
                         code=code)


class EventORAL(CustomEvent):
    def __init__(self, begin, end, code, name, professor, loc, id=None, weight=5):
        name = 'ORAL: ' + code + ' - ' + name
        id = 'ORAL:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, id=id, weight=weight,
                         code=code)


class EventOTHER(CustomEvent):
    def __init__(self, begin, end, code, name, professor, loc, id=None, weight=5):
        name = 'Other: ' + code + ' - ' + name
        id = 'Other:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, id=id, weight=weight,
                         code=code)

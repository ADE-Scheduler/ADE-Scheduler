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
    Extracts the event type from a string.
    Parameters:
    -----------
    code : str
        The string from which the type is to be extracted.
    Returns:
    --------
    t : CustomEvent constructor
        The constructor of the right event type.
    """
    # We first try to detect with the given type
    if ctype == 'Cours magistral':
        return EventCM
    elif ctype == 'TP' or 'TD':
        return EventTP
    elif ctype == 'Examen écrit' or type == 'Test / Interrogation / Partiel':
        return EventEXAM
    elif ctype == 'Examen oral':
        return EventORAL

    # If it fails, do a search using the given ID
    elif re.search(COURSE_REGEX + "-", cid, re.IGNORECASE):
        return EventCM
    elif re.search(COURSE_REGEX + "_", cid, re.IGNORECASE):
        return EventTP
    elif re.search(COURSE_REGEX + "=E", cid, re.IGNORECASE) or re.search(COURSE_REGEX + "=P", cid, re.IGNORECASE):
        return EventEXAM
    elif re.search(COURSE_REGEX + "=O", cid, re.IGNORECASE):
        return EventORAL

    # The search failed, return the "Other" type
    else:
        return EventOTHER


def extractDateTime(date, start, end):
    t0 = datetime.strptime(date + '-' + start, '%d/%m/%Y-%H:%M').astimezone(tz)
    t1 = datetime.strptime(date + '-' + end, '%d/%m/%Y-%H:%M').astimezone(tz)
    return t0, t1


def intersect(event1, event2):
    """
    Check if two events intersect. No safe check is operated.
    Parameters
    ----------
    event1, event2 : ics.Event
        Two events to be compared.
    Returns
    -------
    c : bool
        True if events intersect, False otherwise.
    """
    return event1.end > event2.begin and event2.end > event1.begin  # not(A or B) = notA and notB


def overlap(event1, event2):
    """
    Check if two events intersect. No safe check is operated.
    Parameters
    ----------
    event1, event2 : ics.Event
        Two events to be compared.
    Returns
    -------
    c : int
        The product of the weights if events intersect, 0 otherwise.
    """
    return event1.weight * event2.weight * intersect(event1, event2)


def overlappingTime(event1, event2, onlyPositive=True):
    """
    Compute the overlapping time between two events.
    In option, it can count non-overlap time as negative overlap, in others words, the time between two events.
    Parameters
    ----------
    event1, event2 : ics.Event
        Two events to be compared.
    onlyPositive : boolean
        If True, only positive overlap is counted.
    Returns
    -------
    c : int
        The total overlapping time, multiplied by the weights, in seconds.
    Raises
    ------
    TypeError
        If event1 or event2 are not subclass of ics.Event.
    """

    if event1 == event2:  # No overlap if same event
        return 0
    if not isinstance(event1, CustomEvent) or not isinstance(event2, CustomEvent):
        raise TypeError

    time = event1.weight * event2.weight * (
            min(event1.end, event2.end) - max(event1.begin, event2.begin)).total_seconds()
    if onlyPositive:  # Only positive overlap is counted
        return max(time, 0)
    else:
        return time


def settingsFromEvents(events):
    """
    settings format :
    {codes:[list of Course.code],
        weeks:{
            dict containing (key->int, value->[list of ids])
        }
    }
    where:
        key is week # (following ADE's numbering).
        value contains all the ids to pass as a view to a Course object.
    """
    events = list(events)
    codes = set(event.code for event in events)
    weeks = set(map(gregorianToADE), (event.getweek() for event in events))
    settings = {'codes': codes,
                'weeks': {week: {event.getId() for event in events if event.getweek() == week} for week in weeks}}
    return settings


def JSONfromEvents(events):
    """
        Returns the list of events, in "JSON format"
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
        return self.id

    def getweek(self):
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

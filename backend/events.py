import re
from pytz import timezone
from ics import Event
from datetime import datetime


class AcademicalEvent(Event):
    # We need to set the timezone
    TZ = timezone('Europe/Brussels')
    COURSE_REGEX = '([A-Z]+[0-9]+)'

    def __init__(self, name, begin, end, description, loc, classroom=None, id=None, weight=5, code=None):
        super().__init__(name=name, begin=begin, end=end, description=description, location=loc)
        self.weight = weight
        self.id = id
        self.code = code
        self.classroom = classroom

    def __eq__(self, other):
        if isinstance(other, AcademicalEvent):
            return (self.get_id() == other.get_id()
                    and self.begin == other.begin
                    and self.duration == other.duration)
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_id(self):
        return self.id

    def __hash__(self):
        return super().__hash__()

    def __repr__(self):
        tmp = self.id + ':' if self.id is not None else 'FTS:'
        return tmp + self.begin.strftime('%d/%m - %Hh%M') + ' to ' + self.end.strftime('%Hh%M')

    def set_weight(self, weight):
        self.weight = weight

    def json(self):
        return {'start': str(self.begin), 'end': str(self.end), 'title': self.id + '\n' + self.classroom,
                'editable': False, 'description': self.name + '\n' + self.location + ' - ' +
                str(self.duration) + '\n' + str(self.description), 'code': self.code}

    def intersects(self, other):
        return self.end > other.begin and other.end > self.begin  # not(A or B) = notA and notB

    __xor__ = intersects

    def overlap(self, other):
        return self.weight * other.weight * self.intersects(other)

    __mul__ = overlap

    def get_week(self):
        """
        returns the week of this event in the gregorian calendar, starting at 0 for the first week
        """
        return self.begin.isocalendar()[1] - 1

    @staticmethod
    def extract_code(code: str):
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
        s = re.search(AcademicalEvent.COURSE_REGEX, code, re.IGNORECASE)
        if s:
            return s.group(1)
        else:
            return ''

    @staticmethod
    def extract_type(ctype: str, cid: str):
        """
        # TODO
        :param ctype:
        :param cid:
        :return:
        """
        # We first try to detect the type with the ID regex
        if re.search(AcademicalEvent.COURSE_REGEX + "-", cid, re.IGNORECASE):
            return EventCM
        elif re.search(AcademicalEvent.COURSE_REGEX + "_", cid, re.IGNORECASE):
            return EventTP
        elif re.search(AcademicalEvent.COURSE_REGEX + "=E", cid, re.IGNORECASE) or\
                re.search(AcademicalEvent.COURSE_REGEX + "=P", cid, re.IGNORECASE):
            return EventEXAM
        elif re.search(AcademicalEvent.COURSE_REGEX + "=O", cid, re.IGNORECASE):
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

    @staticmethod
    def extract_datetime(date, start, end):
        """
        Parses info to return the start and end time of an event
        :param date: str
        :param start: str
        :param end: str
        :return: datetime object
        """
        t0 = datetime.strptime(date + '-' + start, '%d/%m/%Y-%H:%M').astimezone(AcademicalEvent.TZ)
        t1 = datetime.strptime(date + '-' + end, '%d/%m/%Y-%H:%M').astimezone(AcademicalEvent.TZ)
        if t0 < t1:
            return t0, t1
        else:
            return t1, t0

    @staticmethod
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

    @staticmethod
    def json_from_events(events):
        """
        Converts the events into a json-like format
        :param events: list of CustomEvents
        :return: list of dict
        """
        return [{'start': str(event.begin), 'end': str(event.end), 'title': event.id + '\n' + event.classroom, 'editable':
                False, 'code': event.code, 'description': event.name + '\n' + event.location + ' - ' + str(event.duration)
                + '\n' + str(event.description)} for event in events]


class EventCM(AcademicalEvent):
    def __init__(self, begin, end, code, name, professor, loc, classroom=None, id=None, weight=5):
        name = 'CM: ' + code + ' - ' + name
        id = 'CM:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, classroom=classroom, id=id,
                         weight=weight, code=code)


class EventTP(AcademicalEvent):
    def __init__(self, begin, end, code, name, professor, loc, classroom=None, id=None, weight=5):
        name = 'TP: ' + code + ' - ' + name
        id = 'TP:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, classroom=classroom, id=id,
                         weight=weight, code=code)


class EventEXAM(AcademicalEvent):
    def __init__(self, begin, end, code, name, professor, loc, classroom=None, id=None, weight=5):
        name = 'EXAM: ' + code + ' - ' + name
        id = 'EXAM:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, classroom=classroom, id=id,
                         weight=weight, code=code)


class EventORAL(AcademicalEvent):
    def __init__(self, begin, end, code, name, professor, loc, classroom=None, id=None, weight=5):
        name = 'ORAL: ' + code + ' - ' + name
        id = 'ORAL:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, classroom=classroom, id=id,
                         weight=weight, code=code)


class EventOTHER(AcademicalEvent):
    def __init__(self, begin, end, code, name, professor, loc, classroom=None, id=None, weight=5):
        name = 'Other: ' + code + ' - ' + name
        id = 'Other:' + id
        super().__init__(name=name, begin=begin, end=end, descr=str(professor), loc=loc, classroom=classroom, id=id,
                         weight=weight, code=code)
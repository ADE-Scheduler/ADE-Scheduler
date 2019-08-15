from event import *
from itertools import chain
from operator import itemgetter


class Course:
    def __init__(self, code, name, weight=1):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight

        # A course can be composed of 5 different events: CM, TP, Exam, Oral and Other
        # Each event is classed by week
        CM = [[] for i in range(53)]  # EventCM
        TP = [[] for i in range(53)]  # EventTP
        E = [[] for i in range(53)]  # EventEXAM
        O = [[] for i in range(53)]  # EventORAL
        Other = [[] for i in range(53)]  # EventOTHER
        self.events = {EventCM:CM, EventTP:TP, EventEXAM:E, EventORAL:O, EventOTHER:Other}

    def __getitem__(self, item):
        return self.events[item]
    
    
    def __setitem__(self, name, value):
        self.events[name] = value
    

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
        # TODO: Gérer les Other (trop chiant)
        return self[EventCM][week], self[EventTP][week], self[EventEXAM][week], self[EventORAL][week]

    def getEvents(self, weeks=None):
        if weeks is None:
            return self.events.values()
        elif isinstance(weeks, slice):
            return (events[slice] for events in self.events.values())
        else:
            itg = itemgetter(*list(weeks))
            return (itg(events) for events in self.events.values())

    def join(self):
        for eventType, course in self.events.items():
            for week in range(len(course)):
                course[week].sort(key=lambda e: e.getId())
                n_events = len(course[week])
                if n_events == 0:
                    pass
                else:
                    c = [course[week][0]] # the new list of courses (joined when possible)
                    for i in range(1, n_events):
                        if c[-1].getId() == course[week][i].getId(): # If we can join [i-1] & [i]
                            c[-1] = eventType(c[-1].begin, 2*c[-1].duration, self.code, self.name, c[-1].description, c[-1].location, c[-1].id)
                        else:
                            c.append(course[week][i])
                    self[eventType][week] = c

    def getSummary(self, weeks=None):
        w = chain(*self.getEvents(weeks))
        e = chain(*w)  # [CM1, CM2,... , TP1, ...]
        return set(map(lambda x: x.getId(), e))

    def addEvent(self, event):
        """
        Add an event to this course
        The event is added in the corresponding week
        If the event is already there, it is not added
        """
        week = event.getweek()
        eventType = type(event)

        if event not in self[eventType][week]:
            self[eventType][week].append(event)
            return True
        else:
            return False

    def removeEvent(self, event):
        """
        Removes an event from this course
        """
        week = event.getweek()
        eventType = type(event)

        if event not in self[eventType][week]:
            self[eventType][week].remove(event)
            return True
        else:
            return False
       

    def getEventsJSON(self):
        """
        Returns the list of events for this course, in "JSON format"
        """
        events = list()
        for course in self.events.values():
            for week in course:
                for event in week:
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.name, 'editable': False,
                            'description': event.name + '\n' + event.location + ' - ' + str(event.duration) + '\n' + str(
                                event.description)}
                    events.append(temp)
        return events

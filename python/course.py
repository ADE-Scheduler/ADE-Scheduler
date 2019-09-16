from event import *
from itertools import chain, repeat
from operator import itemgetter
from collections.abc import Iterable
from static_data import N_WEEKS
import pandas as pd
import numpy as np


class Course:
    def __init__(self, code, name, weight=1):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight
        index = ['type', 'id']
        columns = ['week', 'event']

        self.activities = pd.DataFrame(columns=index+columns)
        self.activities.set_index(keys=index, inplace=True)

        # A course can be composed of 5 different events: CM, TP, Exam, Oral and Other
        # Each event is classed by week
        CM = [[] for i in range(N_WEEKS)]  # EventCM
        TP = [[] for i in range(N_WEEKS)]  # EventTP
        E = [[] for i in range(N_WEEKS)]  # EventEXAM
        O = [[] for i in range(N_WEEKS)]  # EventORAL
        Other = [[] for i in range(N_WEEKS)]  # EventOTHER
        self.events = {EventCM: CM, EventTP: TP, EventEXAM: E, EventORAL: O, EventOTHER: Other}

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

    def __repr__(self):
        return str(self)

    def add_activity(self, type_: str, id: str, events: list):
        data = [[event.getweek(), event] for event in events]

        tuples = list(repeat((type_, id), len(data)))
        index = pd.MultiIndex.from_tuples(tuples, names=self.activities.index.name)
        df = pd.DataFrame(data=data, columns=self.activities.columns, index=index)

        self.activities = self.activities.append(df)

        print('activities \n', self.activities)


    def setEventWeight(self, percentage=None, eventType=None):
        """
        Modify this course's events weight
        :param percentage: int, the "priority" required for this course in (0-100)%
        :param eventType: if we want to modify the weight of a certain type of event only
        :return: /
        """
        # No percentage specified, set to default value
        if percentage is None:  percentage = 50

        if eventType is None:
            self.activities['event'].apply(lambda e: e.set_weight(percentage/10))


        # No event type sepcified, meaning we modify the weight of all events
        if eventType is None: eventType = self.events.keys()
        # Set the weight (0 --> 10) as a function of the percentage
        for eT in eventType:
            for week in self.events[eT]:
                for event in week:
                    event.weight = percentage/10

    def getEvents(self, weeks=None, eventTypes=None, swap=False):
        """
        Returns events of this course.
        Parameters:
        -----------
        weeks : None, int, slice or iterable
            If None, return all the weeks. Otherwise, return weeks specified (from 0 to 52).
        eventTypes : set of event.CustomEvent
            Event types to include. If None, includes all the types.
        swap : bool
            If False, returns a len(evenTypes) generator containing each time a len(weeks) generator.
            If True, returns a len(weeks) generator containing each time a len(eventTypes) generator.
            Makes iterating through weeks easier if needed.
        Returns:
        --------
        e : generator
            A generator of all the events that are happening during the weeks
        """
        if eventTypes is None: eventTypes = self.events.keys()
        if weeks is None:
            if swap:
                return ((self.events[eventType][week] for eventType in eventTypes) for week in range(N_WEEKS))
            else:
                return (self.events[eventType] for eventType in eventTypes)
        elif isinstance(weeks, slice) or isinstance(weeks, int):
            if swap:
                if isinstance(weeks, slice):
                    step = weeks.step if weeks.step else 1
                    return ((self.events[eventType][week] for eventType in eventTypes) for week in
                            range(weeks.start, weeks.stop, step))
                else:
                    return ((self.events[eventType][week] for eventType in eventTypes) for week in [weeks])
            else:
                return (self.events[eventType][weeks] for eventType in eventTypes)
        else:
            if swap:
                return ((self.events[eventType][week] for eventType in eventTypes) for week in weeks)
            else:
                itg = itemgetter(*list(weeks))
                return (list(itg(self.events[eventType][weeks])) for eventType in eventTypes)

    def getWeek(self, week):
        return tuple(self.getEvents(week))

    def join(self):
        for eventType, course in self.events.items():
            for week in range(len(course)):
                course[week].sort(key=lambda e: e.getId())
                n_events = len(course[week])
                if n_events == 0:
                    pass
                else:
                    c = [course[week][0]]  # the new list of courses (joined when possible)
                    for i in range(1, n_events):
                        if c[-1].getId() == course[week][i].getId():  # If we can join [i-1] & [i]
                            id = c[-1].id[c[-1].id.index(':') + 1:]
                            c[-1] = eventType(c[-1].begin, course[week][i].end, self.code, self.name, c[-1].description,
                                              c[-1].location, id)   # TODO: FIX HERE
                        else:
                            c.append(course[week][i])
                    self[eventType][week] = c

    def getSummary(self, weeks=None, view=None):
        w = chain(*self.getView(weeks, view))
        if isinstance(weeks, int):
            return set(map(lambda x: x.getId(), w))
        else:
            e = chain(*w)  # [CM1, CM2,... , TP1, ...]
            return set(map(lambda x: x.getId(), e))

    def getViews(self, weeks=None, views=None, eventTypes=None, swap=False, repeatView=False):
        if eventTypes is None: eventTypes = self.events.keys()
        w = self.getEvents(weeks=weeks, eventTypes=eventTypes, swap=swap)
        if views is None:
            return w
        else:
            if repeatView: views = repeat(views)
            if swap:
                return ((filter(lambda e: e.getId() in view, eventWeek) for eventWeek in eventsWeek) for
                        view, eventsWeek in zip(views, w))
            else:
                return ((filter(lambda e: e.getId() in view, eventWeek) for view, eventWeek in zip(views, eventWeeks))
                        for eventWeeks in w)

    def getView(self, weeks=None, ids=None):
        w = self.getEvents(weeks)
        if ids is None:
            return w
        else:
            ids = set(ids)
            return (list(filter(lambda e: e.getId() in ids, weekEvents)) for weekEvents in w)

    def mergeEvents(self, eventTypes, week):
        if not isinstance(eventTypes, Iterable):
            eventTypes = {eventTypes}
        view = set()
        for eventType in eventTypes:  # What we merge
            to_merge = sorted(self[eventType][week], key=lambda e: e.begin)
            if len(to_merge) == 0:
                pass
            else:
                ev = [to_merge[0]]
                for e in to_merge[1:]:
                    if intersect(ev[-1], e):
                        pass
                    else:
                        ev.append(e)
                view.update(e.getId() for e in ev)
        for eventType in set(self.events.keys()) - set(eventTypes):  # What we don't merge
            view.update(e.getId() for e in self[eventType][week])
        return view  # A set to pass to getView function

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
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.id, 'editable': False,
                            'description': event.name + '\n' + event.location + ' - ' + str(event.duration) + '\n' +
                                           str(event.description), 'code': event.code}
                    events.append(temp)
        return events

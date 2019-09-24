from event import *
from itertools import repeat
from static_data import N_WEEKS
import pandas as pd


class Course:
    def __init__(self, code, name, weight=1):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight
        index = ['code', 'type', 'id']
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

    def add_activity(self, event_type, id_: str, events: list):
        """
        # TODO
        :param event_type:
        :param id_:
        :param events:
        :return:
        """
        if len(events) == 0:
            return
        data = [[event.get_week(), event] for event in events]
        id_ = event_prefix(event_type) + id_
        tuples = list(repeat((self.code, event_type, id_), len(data)))
        index = pd.MultiIndex.from_tuples(tuples, names=self.activities.index.name)
        df = pd.DataFrame(data=data, columns=self.activities.columns, index=index)
        self.activities = self.activities.append(df)

    def setEventWeight(self, percentage=None, event_type=None):
        """
        Modify this course's events weight
        :param percentage: int, the "priority" required for this course in (0-100)%
        :param event_type: if we want to modify the weight of a certain type of event only
        :return: /
        """
        # No percentage specified, set to default value
        if percentage is None:
            percentage = 50

        def f(event):
            event.set_weight(percentage/10)

        if event_type is None:
            self.activities['event'].apply(f)
        else:
            level = self.activities.index.names.index(event_type)
            valid = self.activities.index.get_level_values(level) == event_type
            self.activities['event'][valid].apply(f)

    def get_summary(self):
        """
        # TODO
        :return:
        """
        return self.activities.index.get_level_values('id').unique()

    def getEventsJSON(self):
        """
        # TODO
        :return:
        """
        return list(map(lambda e: e.json(), self.activities['event'].values))

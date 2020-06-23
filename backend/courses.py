from itertools import repeat
import pandas as pd
from backend.events import AcademicalEvent
from typing import List, Union, Dict, Iterable


View = Union[List[int], Dict[int, str]]


class Course:
    """
    A course aims to represent one or more courses. It contains its events and is represented with a name and a code.
    """
    def __init__(self, code: str, name: str, weight: float = 1, activities: pd.DataFrame = None):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight

        if activities:
            self.activities = activities
        else:
            index = ['code', 'type', 'id']
            columns = ['week', 'event']

            self.activities = pd.DataFrame(columns=index+columns)
            self.activities.set_index(keys=index, inplace=True)

    def __eq__(self, other: 'Course') -> bool:
        if isinstance(other, Course):
            return self.code == other.code
        else:
            raise TypeError

    def __ne__(self, other: 'Course') -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.code + ": " + self.name

    def __repr__(self) -> str:
        return str(self)

    def add_activity(self, events: List[AcademicalEvent]) -> None:
        """
        Add an activity to the current course's activities. An activity is a set of events with the same id.
        :param events: list of academical events coming from the same activity
        :return: /
        """
        if len(events) == 0:
            return
        data = [[event.get_week(), event] for event in events]
        event_type = type(events[0])
        id = events[0].id
        tuples = list(repeat((self.code, event_type, id), len(data)))
        index = pd.MultiIndex.from_tuples(tuples, names=self.activities.index.name)
        df = pd.DataFrame(data=data, columns=self.activities.columns, index=index)
        self.activities = self.activities.append(df)

    def set_weights(self, percentage: float = None, event_type: AcademicalEvent = None) -> None:
        """
        Modifies this course's events weight.
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

    def get_summary(self) -> pd.DataFrame:
        """
        Returns the summary of all activities in the course.
        :return: list of activity ids
        """
        return self.activities.index.get_level_values('id').unique()

    def get_events(self, view: View = None) -> Iterable[AcademicalEvent]:
        """
        Returns a list of events that matches correct ids.
        :param view: list of ids, or dict {week_number : ids}
        :return: list of events
        """
        if view is None:
            return self.activities['event'].values
        elif isinstance(view, list):
            valid = self.activities.index.get_level_values('id').isin(view)
            return self.activities['event'][valid].values
        elif isinstance(view, dict):
            events = list()

            grp_weeks = self.activities.groupby('week')

            # weeks that are both in ids dict and in activities
            valid_weeks = set(view.keys()).intersection(set(grp_weeks.groups.keys()))

            for week in valid_weeks:
                week_data = grp_weeks.get_group(week)
                valid = week_data.index.get_level_values('id').isin(view[week])
                events.extend(week_data['event'][valid].values.tolist())

            return events

    def getEventsJSON(self):
        """
        # TODO
        :return:
        """
        return list(map(lambda e: e.json(), self.activities['event'].values))


def merge_courses(courses: Iterable[Course], code: str = None, name: str = None, weight: float = None) -> Course:
    activities = pd.concat(course.activities for course in courses)
    return Course(code=code, name=name, weight=weight, activities=activities)

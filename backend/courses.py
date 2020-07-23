from itertools import repeat
import pandas as pd
from backend.events import AcademicalEvent
from typing import List, Union, Dict, Iterable, Optional
from collections import defaultdict


View = Union[List[int], Dict[int, str]]


class Course:
    """
    A course aims to represent one or more courses.
    It contains its events and is represented with a name and a code.

    :param code: the code of the course
    :type code: str
    :param name: the full name of the course
    :type name: str
    :param weight: the weight attributed to the course
    :type weight: float
    :param activities: a structure of all the events indexed by code, type and id
    :type activities: Optional[pd.Dataframe]

    :Example:

    >>> course = Course('LMECA2732', 'Robotics')
    """
    def __init__(self, code: str, name: str, weight: float = 1, activities: Optional[pd.DataFrame] = None):
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
        :type events: List[AcademicalEvent]
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

    def set_weights(self, percentage: float = 50, event_type: Optional[AcademicalEvent] = None) -> None:
        """
        Modifies this course's events weight.

        :param percentage: the "priority" required for this course in (0-100)%, default is 50%
        :type percentage: float
        :param event_type: if present, modify the weight of a certain type of event only
        :type event_type: Optional[AcademicalEvent]
        """

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

        :return: dict of activity ids, ordered by activity type (CM, TP, etc.)
        :rtype: dict
        """
        summary = defaultdict(list)
        ids = self.activities.index.get_level_values('id').unique()
        for id in ids:
            [type, code] = id.split(': ')
            summary[type].append(code)
        return dict(summary)

    def get_events(self, view: Optional[View] = None, reverse: bool = False) -> Iterable[AcademicalEvent]:
        """
        Returns a list of events that optionally matches correct ids.

        :param view: if present, list of ids or dict {week_number : ids}
        :type view: Optional[View]
        :param reverse: if True, the View will be removed from events
        :type reverse: bool
        :return: list of events
        :rtype: Iterable[AcademicalEvent]
        """
        if view is None:
            return self.activities['event'].values
        elif isinstance(view, list):
            valid = self.activities.index.get_level_values('id').isin(view)

            if reverse:
                valid = ~valid

            return self.activities['event'][valid].values
        elif isinstance(view, dict):
            events = list()

            grp_weeks = self.activities.groupby('week')

            # weeks that are both in ids dict and in activities
            valid_weeks = set(view.keys()).intersection(set(grp_weeks.groups.keys()))

            for week in valid_weeks:
                week_data = grp_weeks.get_group(week)
                valid = week_data.index.get_level_values('id').isin(view[week])

                if reverse:
                    valid = ~valid

                events.extend(week_data['event'][valid].values.tolist())

            return events


def merge_courses(courses: Iterable[Course], code: Optional[str] = None,
                  name: Optional[str] = None, weight: float = 1) -> Course:
    """
    Merges multiple courses into one.

    :param courses: multiple courses
    :type courses: Iterable[Courses]
    :param code: the new code
    :type code: Optional[str]
    :param name: the new name
    :type name: Optional[str]
    :param weight: the new weight
    :type weight: float
    :return: the new course
    :rtype: Course
    """
    activities = pd.concat(course.activities for course in courses)
    return Course(code=code, name=name, weight=weight, activities=activities)

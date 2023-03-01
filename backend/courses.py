from collections import defaultdict
from itertools import repeat
from typing import Any, Dict, Iterable, List, Optional, Set, Union

import pandas as pd

from backend.events import AcademicalEvent

View = Union[List[str], Set[str], Dict[int, str]]


def generate_empty_dataframe():
    index = ["code", "type", "id"]
    columns = ["week", "event"]

    activities = pd.DataFrame(columns=index + columns)
    activities.set_index(keys=index, inplace=True)

    return activities


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

    def __init__(
        self,
        code: str,
        name: str,
        weight: float = 1,
        activities: Optional[pd.DataFrame] = None,
    ):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight

        if activities is not None:
            self.activities = activities
        else:
            self.activities = generate_empty_dataframe()

    def __eq__(self, other: Union["Course", str]) -> bool:
        if isinstance(other, Course):
            return self.code == other.code
        elif isinstance(other, str):
            return self.code == other
        else:
            raise TypeError

    def __ne__(self, other: Union["Course", str]) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.code + ": " + self.name

    def __repr__(self) -> str:
        return str(self)

    def add_activity(self, events: List[AcademicalEvent]):
        """
        Adds an activity to the current course's activities. An activity is a set of events with the same id.

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
        self.activities = pd.concat([self.activities, df])

    def set_weights(
        self, percentage: float = 50, event_type: Optional[AcademicalEvent] = None
    ):
        """
        Modifies this course's events weight.

        :param percentage: the "priority" required for this course in (0-100)%, default is 50%
        :type percentage: float
        :param event_type: if present, modify the weight of a certain type of event only
        :type event_type: Optional[AcademicalEvent]
        """

        def f(event):
            event.set_weight(percentage / 10)

        if event_type is None:
            self.activities["event"].apply(f)
        else:
            level = self.activities.index.names.index(event_type)
            valid = self.activities.index.get_level_values(level) == event_type
            self.activities["event"][valid].apply(f)

    def get_summary(self) -> Dict[str, Set[str]]:
        """
        Returns the summary of all activities in the course.

        :return: dict of activity codes, ordered by activity type (CM, TP, etc.)
        :rtype: Dict[str, Set[str]]
        """
        # TODO: Fix summary for external calendar
        summary = defaultdict(set)
        ids = self.activities.index.get_level_values("id").sort_values().unique()
        for id in ids:
            event_type, code = id.split(": ", maxsplit=1)
            summary[event_type].add(code)

        return summary

    def get_activities(
        self, view: Optional[View] = None, reverse: bool = False
    ) -> pd.DataFrame:
        """
        Returns a table of all activities that optionally match correct ids.

        :param view: if present, list of ids or dict {week_number : ids}
        :type view: Optional[View]
        :param reverse: if True, the activities in View will be removed
        :type reverse: bool
        :return: table containing all the activities and their events
        :rtype: pd.DataFrame
        """
        if view is None:
            return self.activities
        elif isinstance(view, list) or isinstance(view, set):
            valid = self.activities.index.get_level_values("id").isin(view)

            if reverse:
                valid = ~valid

            return self.activities[valid]
        elif isinstance(view, dict):
            activities = [generate_empty_dataframe()]

            grp_weeks = self.activities.groupby("week")

            # weeks that are both in ids dict and in activities
            valid_weeks = set(view.keys()).intersection(grp_weeks.groups.keys())

            for week in valid_weeks:
                week_data = grp_weeks.get_group(week)
                valid = week_data.index.get_level_values("id").isin(view[week])

                if reverse:
                    valid = ~valid

                activities.append(week_data[valid])

            return pd.concat(activities)
        else:
            return None

    def get_events(self, **kwargs) -> Iterable[AcademicalEvent]:
        """
        Returns a list of events that optionally matches correct ids.

        :param kwargs: parameters that will be passed to :func:`Course.get_activities`
        :type kwargs: Any
        :return: list of events
        :rtype: Iterable[AcademicalEvent]
        """
        return self.get_activities(**kwargs)["event"].values


def merge_courses(
    courses: Iterable[Course],
    code: str = "0000",
    name: str = "merged",
    weight: float = 1,
    views: Optional[Dict[str, View]] = None,
    **kwargs: Any,
) -> Course:
    """
    Merges multiple courses into one.

    :param courses: multiple courses
    :type courses: Iterable[Courses]
    :param code: the new code
    :type code: str
    :param name: the new name
    :type name: str
    :param weight: the new weight
    :type weight: float
    :param views: map of views that will be passed to :func:`Course.get_activities`
    :type views: Optional[Dict[str, View]]
    :param kwargs: additional parameters that will be passed to :func:`Course.get_activities`
    :type kwargs: Any
    :return: the new course
    :rtype: Course
    """
    if views:
        activities = pd.concat(
            course.get_activities(view=views[course.code], **kwargs)
            for course in courses
        )
    else:
        activities = pd.concat(course.get_activities(**kwargs) for course in courses)
    return Course(code=code, name=name, weight=weight, activities=activities)

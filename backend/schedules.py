from itertools import product, chain, starmap, repeat
from collections import deque, defaultdict
from heapq import nsmallest
import operator
from typing import Iterable, Union, List, SupportsInt, Dict, Set, Any
from backend.courses import Course, merge_courses
from flask import current_app as app
from ics import Calendar
import json

import backend.events as evt

"""
Schedule needed data:
{
    codes: {LMECA2660, LELEC2760, etc},                     // requested course codes
    filtered_subcodes:  {
                            LELEC2760: {CM: LELEC2760_Q1},
                            LMECA2660: {CM: LMECA2660_Q2},
                        }                                   // unselected subcodes
    best_schedules:     [{
                            LELEC2760:  {
                                            week1: {CM: LELEC2760_Q1}
                                        }
                        }]                                  // filtered subcodes, week by week
    custom_events: [event1, event2],                        // custom user events
    project_id: id,
    schedule_id: id,
}
"""


class ScheduleEncoder(json.JSONEncoder):
    """
    Subclass of json encoder aiming to convert sets of strings into lists of strings.
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, set):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class ScheduleDecoder(json.JSONDecoder):
    """
    Subclass of json decoder aiming to convert back the lists of strings into sets of strings.
    """
    def decode(self, obj: Any, w: Any = None) -> str:
        decoded = json.JSONDecoder().decode(obj)
        for key in decoded:
            obj = decoded[key]
            if isinstance(obj, list) and isinstance(obj[0], str):
                decoded[key] = set(obj)
        return decoded


class Schedule:
    """
    A schedule is essentially a combination of courses stored as a master course, from which some events can be removed.

    :param project_id: the schedule id matching this of the Database it is currently saved in.
               This parameter is automatically set when the schedule is saved for the first time.
    """
    def __init__(self, project_id: SupportsInt, schedule_id: int = None, label: str = 'New schedule'):
        self.id = schedule_id
        self.project_id = project_id
        self.label = label
        self.codes = set()
        self.filtered_subcodes = defaultdict(set)
        self.best_schedules = None
        self.custom_events = list()
        self.priorities = dict()
        self.color_palette = ['#374955', '#005376', '#00c0ff', '#1f789d', '#4493ba',
                              '#64afd7', '#83ccf5', '#3635ff', '#006c5a', '#3d978a']

    def add_filter(self, code: str, filter: Union[Iterable[str], str]):
        if isinstance(filter, str):
            self.filtered_subcodes[code].add(filter)
        else:
            self.filtered_subcodes[code].update(filter)

    def remove_filter(self, code: str, filter: Union[Iterable[str], str]):
        if isinstance(filter, str):
            self.filtered_subcodes[code].remove(filter)
        else:
            self.filtered_subcodes[code].difference_update(filter)

    def add_course(self, code: Union[Iterable[str], str]) -> Set[str]:
        """
        Adds one or many courses to the schedule.

        :param code: the code of the course added
        :type code: Union[Iterable[str], str])
        :return: all the new codes added to the schedule
        :rtype: Set[str]
        """
        old = set(self.codes)
        if isinstance(code, str):
            self.codes.add(code)
        else:
            self.codes.update(code)

        return self.codes - old

    def remove_course(self, code: str):
        """
        Removes a course from the schedule.

        :param code: the code of the course to remove
        :type code: str
        """
        if code in self.codes:
            self.codes.discard(code)

    def add_custom_event(self, event: evt.CustomEvent):
        """
        Adds a custom event to the schedule.

        :param event: the event to add
        :type event: CustomEvent (or RecurringCustomEvent)
        """
        self.custom_events.append(event)

    def remove_custom_event(self, event: evt.CustomEvent = None, id: str = None):
        """
        Removes a custom event from the schedule.
        If this event is present multiple times in the schedule, only delete the first occurrence.

        :param event: the event to remove
        :type event: CustomEvent
        """
        if event is not None:
            self.custom_events.remove(event)
        if id is not None:
            event = next(e for e in self.custom_events if e.uid == id)
            self.custom_events.remove(event)

    def get_courses(self) -> List[Course]:
        """
        Returns all the courses of this schedule as a list.

        :return: the courses
        :rtype: List[Course]
        """
        mng = app.config['MANAGER']
        return mng.get_courses(*self.codes, project_id=self.project_id)

    def get_events(self, json: bool = False, schedule_number: int = 0) -> List[evt.Event]:
        """
        Extracts all the events matching ids in the filtered_subcodes list.

        :param json: whether or not the events are to be returned in a JSON format
        :type json: bool
        :param schedule_number: the # of the schedule, 0 for main and 1 for best one, 2 for second best, etc.
        :type schedule_number: int
        :return: the events
        :rtype: List[events]
        """
        events = list()
        courses = self.get_courses()

        if schedule_number == 0:
            views = self.filtered_subcodes
        else:
            views = self.best_schedules[schedule_number - 1]

        # Course Events
        n = len(self.color_palette)
        for i, course in enumerate(courses):
            course_events = course.get_events(view=views[course.code], reverse=True)
            if json:
                events.extend([e.json(self.color_palette[i % n]) for e in course_events])
            else:
                events.extend(course_events)

        # Custom user events
        if json:
            events.extend([e.json() for e in self.custom_events])
        else:
            events.extend(self.custom_events)

        return events

    def get_summary(self) -> Dict[str, Dict[str, Set[str]]]:
        """
        Returns the summary of all activities within the schedule.

        :return: dict of course summaries
        :rtype:  Dict[str, Dict[str, Set[str]]]
        """
        courses = self.get_courses()
        summary = dict()
        for course in courses:
            summary[course.code] = course.get_summary()
        return summary

    def get_ics_file(self, schedule_number: int = 0):
        """
        Returns the .ics (iCalendar) representation of this Schedule.

        :param schedule_number: the # of the schedule, 0 for main and 1 for best one, 2 for second best, etc.
        :type schedule_number: int
        :return: iCalendar-formatted schedule
        :rtype: str
        """
        return str(Calendar(events=self.get_events(schedule_number=schedule_number)))

    def compute_best(self, n_best: int = 5, safe_compute: bool = True) -> List[Iterable[evt.CustomEvent]]:
        """
        Computes best schedules trying to minimize conflicts selecting, for each type of event, one event.
        :param n_best: number of best schedules to produce
        :type n_best: int
        :param safe_compute: if True, ignore all redundant events at same time period
        :type safe_compute: bool
        :return: the n_best schedules
        :rtype: List[Iterable[evt.CustomEvent]]
        """
        courses = self.get_courses()

        # Reset the best schedules
        # TODO: pas sûr que c'est la meilleure manière de faire...
        self.best_schedules = [defaultdict(lambda: defaultdict(set)) for _ in range(n_best)]
        best = [[] for _ in range(n_best)]  # We create an empty list which will contain best schedules

        # Forbidden time slots = events that we cannot move and that we want to minimize conflicts with them
        fts = self.custom_events

        # Merge courses applying reverse view on all of them, then get all the activities
        df = merge_courses(courses, views=self.filtered_subcodes, reverse=True).get_activities()

        # We only take care of events which are not of type EvenOTHER
        valid = df.index.get_level_values('type') != evt.EventOTHER
        df_main, df_other = df[valid], df[~valid]

        for week, week_data in df_main.groupby('week'):
            if safe_compute:  # We remove events from same course that happen at the same time
                for _, data in week_data.groupby(level=['code', 'type']):
                    tmp = deque()  # Better for appending
                    # For each event in a given course, for a given type...
                    for index, row in data.iterrows():
                        e = row['event']
                        r = repeat(e)
                        # If that event overlaps with any of the events in tmp
                        if any(starmap(operator.xor, zip(tmp, r))):
                            week_data.drop(index=index, inplace=True, errors='ignore')
                        else:
                            # We append to left because last event is most likely to conflict (if sorted)
                            tmp.appendleft(e)

            # First, each event is considered to be filtered out.
            for event in week_data['event']:
                for i in range(n_best):
                    self.best_schedules[i][event.code][week].add(event.id)
            # Events present in the best schedule will be later removed from the filter

            events = [[data_id.values for _, data_id in data.groupby(level='id')]
                      for _, data in week_data.groupby(level=['code', 'type'])['event']]

            # Generate all possible schedules for a given week
            permutations = product(*events)

            best_weeks = nsmallest(n_best, permutations, key=lambda f: evaluate_week(f, fts))

            n = len(best_weeks)  # Sometimes n < n_best

            for i in range(n):
                events = list(chain.from_iterable(best_weeks[i]))
                best[i].extend(events)

                for event in events:
                    # Remove the event from the filter
                    self.best_schedules[i][event.code][week].remove(event.id)

            # If we could only find n < n_best best scores, we fill the rest in with same last values
            for i in range(n, n_best):
                best[i].extend(events)
                for event in events:
                    self.best_schedules[i][event.code][week].remove(event.id)

        other = df_other['event'].values.flatten().tolist()
        if other:
            [schedule.extend(other) for schedule in best]

        return best


def evaluate_week(week: Iterable[Iterable[evt.CustomEvent]], fts: Iterable[evt.CustomEvent] = None) -> float:
    """
    Evaluates how much a given week contains conflicts.

    :param week: events in a week as provided by :func:`Schedule.compute_best`
    :type week: Iterable[Iterable[evt.CustomEvent]]
    :param fts: additional events to take into account
    :type fts: Iterable[evt.CustomEvent]
    :return: the sum of all the conflicts
    :rtype: float
    """
    week = sorted(chain.from_iterable(week))  # We sort all the events

    if fts is not None:
        week = sorted(week + fts)  # We additionally sort the fts, within the week
    return sum(starmap(operator.mul, zip(week[:-1], week[1:])))  # We sum all the overlaps

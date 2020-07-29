from itertools import product, chain, starmap, repeat
from collections import deque, defaultdict
from heapq import nsmallest
import operator
from typing import Iterable, Union, List, SupportsInt
from backend.courses import Course, merge_courses, View
from flask import current_app as app

import backend.events as evt

"""
Schedule needed data:
{
    code_list: [LMECA2660, LELEC2760, etc],                 // requested course codes
    filtered_subcodes: {
                            LELEC276: [LELEC2760_Q1],
                            LMECA2660: [LMECA2660_Q2],
                        }                                   // unselected subcodes
    best_schedules: [{
                        week1: filtered_subcodes,
                        week2: ...,
                    }, ...]                                 // filtered subcodes, week by week
    custom_events: [event1, event2],                        // custom user events
    priority_levels: {code1: 5, code2: 1, subcode1: 3},     // priority level of the various code & subcodes
    project_id: id,
    schedule_id: id,
}
"""
# TODO: priority_levels -> utile ?


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
        self.codes = list()
        self.filtered_subcodes = defaultdict(list)
        self.best_schedules = list()
        self.custom_events = list()
        self.priorities = dict()
        self.color_palette = ['#374955', '#005376', '#00c0ff', '#1f789d', '#4493ba',
                              '#64afd7', '#83ccf5', '#3635ff', '#006c5a', '#3d978a']

    def add_filter(self, code: str, filter: Union[Iterable[str], str]):
        if isinstance(filter, str):
            self.filtered_subcodes[code].append(filter)
        else:
            self.filtered_subcodes[code].extend(filter)

    def remove_filter(self, code: str, filter: Union[Iterable[str], str]):
        if isinstance(filter, str):
            self.filtered_subcodes[code].remove(filter)
        else:
            for filt in filter:
                self.filtered_subcodes[code].remove(filt)

    def add_course(self, code: Union[Iterable[str], str]) -> List[str]:
        """
        Adds one or many courses to the schedule.

        :param code: the code of the course added
        :type code: Union[Iterable[str], str])
        :return: the codes that were added to the schedule
        """
        if isinstance(code, str):
            if code not in self.codes:
                self.codes.append(code)
                return [code]
        else:
            added_codes = list()
            for c in code:
                if c not in self.codes:
                    self.codes.append(c)
                    added_codes.append(c)
            return added_codes

    def remove_course(self, code: str):
        """
        Removes a course from the schedule.

        :param code: the code of the course to remove
        :type code: str
        """
        if code in self.codes:
            self.codes.remove(code)

    def add_custom_event(self, event: evt.CustomEvent):
        """
        Adds a custom event to the schedule.

        :param event: the event to add
        :type event: CustomEvent (or RecurringCustomEvent)
        """
        self.custom_events.append(event)

    def remove_custom_events(self, event: evt.CustomEvent):
        """
        Removes a custom event from the schedule.
        If this event is present multiple times in the schedule, only delete the first occurrence.

        :param event: the event to remove
        :type event: CustomEvent
        """
        self.custom_events.remove(event)

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
        mng = app.config['MANAGER']
        courses = mng.get_courses(*self.codes, project_id=self.project_id)

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

    def get_summary(self):
        """
        Returns the summary of all activities within the schedule.

        :return: dict of course summaries
        :rtype: dict
        """
        mng = app.config['MANAGER']
        courses = mng.get_courses(*self.codes, project_id=self.project_id)
        summary = dict()
        for course in courses:
            summary[course.code] = course.get_summary()
        return summary

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
        mng = app.config['MANAGER']
        courses = mng.get_courses(*self.codes, project_id=self.project_id)

        self.best_schedules = list()

        # Forbidden time slots = events that we cannot move and that we want to minimize conflicts with them
        fts = self.custom_events

        # Merge courses applying reverse view on all of them, then get all the activities
        df = merge_courses(courses, view=self.filtered_subcodes, reverse=True).get_activities()

        # We only take care of events which are not of type EvenOTHER
        valid = df.index.get_level_values('type') != evt.EventOTHER
        df_main, df_other = df[valid], df[~valid]
        best = [[] for _ in range(n_best)]  # We create an empty list which will contain best schedules

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

            events = [[data_id.values for _, data_id in data.groupby(level='id')]
                      for _, data in week_data.groupby(level=['code', 'type'])['event']]
            permutations = product(*events)

            # TODO: add events code to self.best_schedules

            if n_best == 1:
                best.extend(chain.from_iterable(min(permutations, key=lambda f: evaluate_week(f, fts))))
            else:
                temp = nsmallest(n_best, permutations, key=lambda f: evaluate_week(f, fts))
                n_temp = len(temp)
                for i in range(n_temp):
                    best[i].extend(chain.from_iterable(temp[i]))
                # If we could only find n_temp < n_best best scores, we fill the rest in with same values
                for j in range(n_temp, n_best):
                    best[j].extend(chain.from_iterable(temp[-1]))

        other = df_other['event'].values.flatten().tolist()
        if other:
            [schedule.extend(other) for schedule in best]

        self.best_schedules = best

        return best


def evaluate_week(week: Iterable[evt.AcademicalEvent], fts: Iterable[evt.AcademicalEvent] = None) -> float:
    """
    Evaluates the how much a given week contains conflicts.
    :param week: an iterable of evt.CustomEvent objects
    :param fts: a list of evt.CustomEvent objects
    :return: the sum of all the conflicts
    """
    week = sorted(chain.from_iterable(week))  # We sort all the events

    if fts is not None:
        week = sorted(week + fts)  # We additionally sort the fts, within the week
    return sum(starmap(operator.mul, zip(week[:-1], week[1:])))  # We sum all the overlaps

import operator
from collections import defaultdict, deque
from datetime import timedelta
from heapq import nsmallest
from itertools import chain, product, repeat, starmap
from random import randint
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from flask import current_app as app
from flask_babel import lazy_gettext as _l
from ics import Calendar

import backend.events as evt
from backend.courses import Course, merge_courses

DEFAULT_SCHEDULE_NAME = _l("New schedule")
COLOR_PALETTE = [
    "#bf616a",
    "#2e3440",
    "#a3be8c",
    "#5e81ac",
    "#ebcb8b",
    "#88c0d0",
    "#d08770",
    "#b48ead",
    "#4c566a",
    "#81a1c1",
]


def default_dict_any_to_set() -> defaultdict:
    """
    Create a collections.defaultdict object mapping each key to a set.

    :return: the dictionary
    :rtype: collections.defaultdict
    """
    return defaultdict(set)


def default_options() -> defaultdict:
    """
    Create a collections.defaultdict object mapping each key to a boolean.
    Default value is false.

    :return: the dictionary
    :rtype: collections.defaultdict
    """

    def false():
        return False

    return defaultdict(false)


class Schedule:
    """
    A schedule is essentially a combination of courses stored as a master course, from which some events can be removed.

    :param project_id: the schedule id matching this of the Database it is currently saved in.
               This parameter is automatically set when the schedule is saved for the first time.
    """

    def __init__(
        self,
        project_id: str,
        schedule_id: int = None,
        label: str = DEFAULT_SCHEDULE_NAME,
    ):
        self.id = schedule_id
        self.project_id = project_id
        self.label = label
        self.codes = list()
        self.filtered_subcodes = default_dict_any_to_set()
        self.best_schedules = list()
        self.custom_events = list()
        self.priorities = dict()
        self.color_palette = list(COLOR_PALETTE)
        self.options = dict()

    def get_min_max_time_slots(self) -> Tuple[str, str]:
        mng = app.config["MANAGER"]
        ext_cals = filter(lambda s: "EXT:" in s, self.codes)

        courses = mng.get_courses(*ext_cals, project_id=self.project_id)
        min_time_slot, max_time_slot = (8, 0, 0), (20, 0, 0)
        for course in courses:
            course_events = course.get_events()
            for event in course_events:
                if event.all_day or (event.end - event.begin) == timedelta(hours=24):
                    continue

                for dt in [event.begin, event.end]:
                    tup = dt.hour, dt.minute, dt.second

                    if tup < min_time_slot:
                        min_time_slot = tup
                    elif tup > max_time_slot:
                        max_time_slot = tup

        # slotMaxTime is exclusive
        max_time_slot = max_time_slot[0] + 1, max_time_slot[1], max_time_slot[2]

        return "{:02d}:{:02d}:{:02d}".format(
            *min_time_slot
        ), "{:02d}:{:02d}:{:02d}".format(*max_time_slot)

    def reset_best_schedules(self):
        self.best_schedules = list()

    def get_option(self, option: str) -> bool:
        if not hasattr(self, "options"):
            setattr(self, "options", default_options())

        return self.options[option]

    def set_option(self, option: str, value: bool):
        if not hasattr(self, "options"):
            setattr(self, "options", default_options())

        self.options[option] = value

    def is_empty(self):
        return len(self.codes) == 0 and len(self.custom_events) == 0

    def reset_color_palette(self):
        self.color_palette = list(COLOR_PALETTE)
        return self.color_palette

    def add_filter(self, code: str, filter: Union[Iterable[str], str]):
        if isinstance(filter, str):
            self.filtered_subcodes[code].add(filter)
        else:
            self.filtered_subcodes[code].update(filter)

    def remove_filter(self, code: str, filter: Union[Iterable[str], str]):
        if isinstance(filter, str):
            self.filtered_subcodes[code].discard(filter)
        else:
            self.filtered_subcodes[code].difference_update(filter)

    def reset_filters(self, code):
        self.filtered_subcodes[code] = set()

    def add_course(self, codes: Union[Iterable[str], str]) -> List[str]:
        """
        Adds one or many courses to the schedule.

        :param codes: the codes of the course added
        :type codes: Union[Iterable[str], str])
        :return: all the new codes added to the schedule
        :rtype: List[str]
        """
        self.codes = list(self.codes)
        added = list()
        if isinstance(codes, str):
            codes = [codes]

        for code in codes:
            if code not in self.codes:
                added.append(code)
                self.codes.append(code)

        return added

    def remove_course(self, code: str):
        """
        Removes a course from the schedule.

        :param code: the code of the course to remove
        :type code: str
        """
        self.codes = list(self.codes)
        if code in self.codes:
            self.codes.remove(code)
        if code in self.filtered_subcodes:
            self.filtered_subcodes.pop(code)

    def add_custom_event(self, event: evt.CustomEvent):
        """
        Adds a custom event to the schedule.

        :param event: the event to add
        :type event: CustomEvent (or RecurringCustomEvent)
        """
        if not event in self.custom_events:
            self.custom_events.append(event)

    def get_custom_event(self, id: str) -> Optional[evt.CustomEvent]:
        """
        Returns the custom event matching given id, or None if not found.

        :param id: the unique id of the event
        :type id: str
        :return: the custom event
        :rtype: Optional[CustomEvent]
        """
        return next((e for e in self.custom_events if e.uid == id), None)

    def remove_custom_event(
        self, event: Optional[evt.CustomEvent] = None, id: Optional[str] = None
    ):
        """
        Removes a custom event from the schedule.
        If this event is present multiple times in the schedule, only delete the first occurrence.

        :param event: the event to remove
        :type event: Optional[CustomEvent]
        :param id: the unique id of the event
        :type id: Optional[str]
        """
        if event is not None and event in self.custom_events:
            self.custom_events.remove(event)
        elif id is not None:
            event = self.get_custom_event(id)

            if event:
                self.custom_events.remove(event)

    def set_custom_event_attributes(self, id: str, **kwargs: str):
        """
        Changes the custom event's attributes.

        :param id: the unique id of the event
        :type id: str
        :param kwargs: the attributes and their value
        :type kwargs: str
        """
        event = self.get_custom_event(id)

        if event is None:
            return

        for attr, value in kwargs.items():
            setattr(event, attr, value)

    def get_custom_event_color(
        self, event: Optional[evt.CustomEvent] = None, id: Optional[str] = None
    ) -> Optional[str]:
        """
        Returns the color of a given custom event

        :param event: the event to remove
        :type event: Optional[CustomEvent]
        :param id: the unique id of the event
        :type id: Optional[str]
        :return: the color
        :rtype: Optional[str]
        """
        if event is not None:
            return event.color
        elif id is not None:
            event = self.get_custom_event(id)

            if event:
                return event.color
            return None

    def get_courses(self) -> List[Course]:
        """
        Returns all the courses of this schedule as a list.

        :return: the courses
        :rtype: List[Course]
        """
        mng = app.config["MANAGER"]
        return mng.get_courses(*self.codes, project_id=self.project_id)

    def get_events(
        self, json: bool = False, schedule_number: int = 0
    ) -> List[evt.Event]:
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

        if schedule_number == 0 or schedule_number > len(self.best_schedules):
            views = self.filtered_subcodes
        else:
            views = self.best_schedules[schedule_number - 1]

        # Course Events
        n = len(self.color_palette)
        for i, course in enumerate(courses):
            course_events = course.get_events(view=views[course.code], reverse=True)
            if json:
                events.extend(
                    [e.json(self.color_palette[i % n]) for e in course_events]
                )
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

    def compute_best(
        self, n_best: int = 5, safe_compute: bool = True
    ) -> List[Iterable[evt.CustomEvent]]:
        """
        Computes best schedules trying to minimize conflicts selecting, for each type of event, one event.

        :param n_best: number of best schedules to produce
        :type n_best: int
        :param safe_compute: if True, ignore all redundant events at same time period
        :type safe_compute: bool
        :return: the n_best schedules, but maybe less if cannot find n_best different schedules
        :rtype: List[Iterable[evt.CustomEvent]]
        """
        courses = self.get_courses()

        seed = randint(1, 9999)

        if len(courses) == 0:
            return None

        # Reset the best schedules
        # TODO: pas sûr que c'est la meilleure manière de faire...
        self.best_schedules = [
            defaultdict(default_dict_any_to_set) for _ in range(n_best)
        ]
        best = [
            [] for _ in range(n_best)
        ]  # We create an empty list which will contain best schedules

        # Forbidden time slots = events that we cannot move and that we want to
        # minimize conflicts with them
        fts = self.custom_events

        # Merge courses applying reverse view on all of them, then get all the
        # activities
        df = merge_courses(
            courses, views=self.filtered_subcodes, reverse=True
        ).get_activities()

        # We only take care of events which are not of type EvenOTHER
        valid = df.index.get_level_values("type") != evt.EventOTHER
        df_main, df_other = df[valid], df[~valid]

        max_bests_found = (
            1  # Number of best schedules found (will take the maximum value out of all
        )
        # weeks)

        for week, week_data in df_main.groupby("week"):
            if (
                safe_compute
            ):  # We remove events from same course that happen at the same time
                for _, data in week_data.groupby(level=["code", "type"]):
                    tmp = deque()  # Better for appending
                    # For each event in a given course, for a given type...
                    for index, row in data.iterrows():
                        e = row["event"]
                        r = repeat(e)
                        # If that event overlaps with any of the events in tmp
                        if any(starmap(operator.xor, zip(tmp, r))):
                            week_data = week_data.drop(index=index, errors="ignore")
                        else:
                            # We append to left because last event is most likely to
                            # conflict (if sorted)
                            tmp.appendleft(e)

            # First, each event is considered to be filtered out.
            for event in week_data["event"]:
                for i in range(n_best):
                    self.best_schedules[i][event.code][week].add(event.id)

            # We add actual filter to current week
            for event_code, filtered_ids in self.filtered_subcodes.items():
                for i in range(n_best):
                    self.best_schedules[i][event_code][week].update(filtered_ids)
            # Events present in the best schedule will be later removed from the filter

            events = [
                [
                    data_id.values
                    for _, data_id in data.sample(frac=1, random_state=seed).groupby(
                        level="id", sort=False
                    )
                ]
                for _, data in week_data.groupby(level=["code", "type"], sort=False)[
                    "event"
                ]
            ]

            # Generate all possible schedules for a given week
            permutations = product(*events)

            best_weeks = nsmallest(
                n_best, permutations, key=lambda f: evaluate_week(f, fts)
            )

            n = len(best_weeks)  # Sometimes n < n_best

            max_bests_found = max(n, max_bests_found)

            for i in range(n):
                events = list(chain.from_iterable(best_weeks[i]))
                best[i].extend(events)

                for event in events:
                    # Remove the event from the filter
                    self.best_schedules[i][event.code][week].discard(event.id)

            # If we could only find n < n_best best scores, we fill the rest in with same last values
            for i in range(n, n_best):
                best[i].extend(events)
                for event in events:
                    self.best_schedules[i][event.code][week].discard(event.id)

        # Will delete all redundant schedules
        del best[max_bests_found:]
        del self.best_schedules[max_bests_found:]

        other = df_other["event"].values.flatten().tolist()
        if other:
            [schedule.extend(other) for schedule in best]

        return best


def evaluate_week(
    week: Iterable[Iterable[evt.CustomEvent]], fts: Iterable[evt.CustomEvent] = None
) -> float:
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
    return sum(
        starmap(operator.mul, zip(week[:-1], week[1:]))
    )  # We sum all the overlaps

from itertools import product, chain, starmap, repeat
from collections import deque
from event import EventOTHER
from heapq import nsmallest
import operator
import pandas as pd


def eval_week(week, fts=None):
    """
    Evaluates the how much a given week contains conflicts.
    :param week: an iterable of event.CustomEvent objects
    :param fts: a list of event.CustomEvent objects
    :return: the sum of all the conflicts
    """
    week = sorted(chain.from_iterable(week))  # We sort all the events

    if fts is not None:
        week = sorted(week + fts)  # We additionally sort the fts, within the week
    return sum(starmap(operator.mul, zip(week[:-1], week[1:])))  # We sum all the overlaps


def extract_events(courses, view=None):
    """
    Extracts all the events matching ids in the view list.
    :param courses: a list of course.Course objects
    :param view: if None extracts everything, otherwise must be a list of ids
    :return: the array of events
    """
    if courses is None or len(courses) == 0:
        return []

    df = pd.concat(course.activities for course in courses)

    if view is None:
        return df['event'].values
    else:
        valid = df.index.isin(values=view, level='id')
        return df['event'][valid].values


def compute_best(courses, fts=None, n_best=5, safe_compute=True, view=None):
    """
    Computes best schedules trying to minimize conflicts selecting, for each type of event, one event.
    :param courses: a list of course.Course objects
    :param fts: a list of event.CustomEvent objects
    :param n_best: number of best schedules to produce
    :param safe_compute: if True, ignore all redundant events at same time period
    :param view: list of ids to filter
    :return: the n_best schedules
    """
    df = pd.concat(course.activities for course in courses)

    if view is not None:
        valid = df.index.isin(values=view, level='id')
        df = df[valid]

    # We only take care of events which are not of type EvenOTHER
    valid = df.index.get_level_values('type') != EventOTHER
    df_main, df_other = df[valid], df[~valid]
    best = [[] for i in range(n_best)]  # We create an empty list which will contain best schedules

    for _, week_data in df_main.groupby('week'):
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

        if n_best == 1:
            best.extend(chain.from_iterable(min(permutations, key=lambda f: eval_week(f, fts))))
        else:
            temp = nsmallest(n_best, permutations, key=lambda f: eval_week(f, fts))
            n_temp = len(temp)
            for i in range(n_temp):
                best[i].extend(chain.from_iterable(temp[i]))
            # If we could only find n_temp < n_best best scores, we fill the rest in with same values
            for j in range(n_temp, n_best):
                best[j].extend(chain.from_iterable(temp[-1]))

    other = df_other['event'].values.flatten().tolist()
    if other:
        [schedule.extend(other) for schedule in best]
        return best
    else:
        return best

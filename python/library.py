from ade import get_courses_from_codes
from computation import extract_events
from database import set_link, get_settings_from_link, update_settings_from_link, is_link_present
from ics import Calendar
from computation import compute_best
from itertools import chain
from pytz import timezone
from dateutil.parser import parse
from event import CustomEvent
from itertools import groupby

"""
settings format :
{
    choice: user's schedule choice (int),
    project_id: int,
    codes: [list of codes],
    priority: {code: priority}
    fts: [list of fts],
    id_list: [list of selected ids],
    weeks: dict {week_number : ids}
    check: state of checkboxes (from the UI)
}
"""


def generate_weeks(events):
    grp = groupby(events, key=lambda e: e.get_week())
    weeks = ((week, [e.get_id() for e in e_list]) for week, e_list in grp)
    return dict(weeks)


def save_settings(link, session, choice=0, username=None, check=None):
    """
    Saves a user's session in the database with the corresponding link
    :param check: state of checkbobxes
    :param link: str, given to the user
    :param session: dict, the user's session
    :param choice: int, the choice of schedule to save
    :param username: if specified, the user's username
    :return: /
    """
    courses = get_courses_from_codes(session['codes'], session['basic_context']['project_id'])
    courses = list(chain.from_iterable(courses.values()))
    if choice < 0:
        events = extract_events(courses, view=session['id_list'])
    else:
        for course in courses: course.set_weights(session['basic_context']['priority'].get(course.code))
        events = compute_best(courses, fts=load_fts(session['fts']), n_best=3, view=session['id_list'],
                              safe_compute=session['basic_context']['safe_compute'])[choice]
    weeks = generate_weeks(events)
    settings = {
        'choice': choice,
        'project_id': session['basic_context']['project_id'],
        'codes': session['codes'],
        'priority': session['basic_context']['priority'],
        'fts': session['fts'],
        'id_list': session['id_list'],
        'weeks': weeks,
        'check': check
    }
    set_link(link=link, username=username, settings=settings)


def update_settings(link, session, choice=None, check=None):
    """
    Update a link's corresponding settings, after modifications imposed by the user
    :param check: state of checkboxes
    :param link: str, given to the user
    :param session: dict, the user's session
    :param choice: int, the choice of schedule to save
    :param username: if specified, the user's username
    :return: /
    """
    if choice is None:
        old_settings = get_settings_from_link(link)
        choice = old_settings['choice']

    courses = get_courses_from_codes(session['codes'], session['basic_context']['project_id'])
    courses = list(chain.from_iterable(courses.values()))
    if choice < 0:
        events = extract_events(courses, view=session['id_list'])
    else:
        for course in courses: course.set_weights(session['basic_context']['priority'].get(course.code))
        events = compute_best(courses, fts=load_fts(session['fts']), n_best=3, view=session['id_list'],
                              safe_compute=session['basic_context']['safe_compute'])[choice]
    weeks = generate_weeks(events)
    settings = {
        'choice': choice,
        'project_id': session['basic_context']['project_id'],
        'codes': session['codes'],
        'priority': session['basic_context']['priority'],
        'fts': session['fts'],
        'id_list': session['id_list'],
        'weeks': weeks,
        'check': check
    }
    update_settings_from_link(link=link, settings=settings)


def load_settings(link):
    """
    :param link: str, given by the user
    :return: this link's corresponding settings
    """
    return get_settings_from_link(link)


def get_calendar_from_link(link):
    """
    Returns the user's saved calendar in .ics format
    :param link: str, given by the user
    :return: str, the calendar in .ics format, or None if the link doesn't exist
    """
    if not is_link_present(link):
        return None
    settings = get_settings_from_link(link)

    courses = get_courses_from_codes(settings['codes'], project_id=settings['project_id'])
    courses = list(chain.from_iterable(courses.values()))
    if isinstance(settings['weeks'], list):
        if not isinstance(settings['weeks'][0], list):
            weeks = settings['weeks'][0]
        else:
            weeks = dict(enumerate(settings['weeks']))
    elif isinstance(settings['weeks'], dict):
        weeks = settings['weeks']

    events = chain.from_iterable(course.get_view(weeks) for course in courses)
    return str(Calendar(events=events))


def load_fts(fts_json):
    tz = timezone('Europe/Brussels')
    fts = list()
    for el in fts_json:
        t0 = parse(el['start']).astimezone(tz)
        t1 = parse(el['end']).astimezone(tz)
        if el['title'] == 'High' or el['title'] == 'Haut':
            fts.append(CustomEvent(el['title'], t0, t1, el['description'], '', weight=9))
        elif el['title'] == 'Medium' or el['title'] == 'Moyen':
            fts.append(CustomEvent(el['title'], t0, t1, el['description'], '', weight=6))
        elif el['title'] == 'Low' or el['title'] == 'Bas':
            fts.append(CustomEvent(el['title'], t0, t1, el['description'], '', weight=1))
    return fts

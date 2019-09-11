from ade import getCoursesFromCodes
from computation import extractEvents
from database import setLink, getSettingsFromLink, updateSettingsFromLink, isLinkPresent
from ics import Calendar
from computation import compute_best
from itertools import chain
from pytz import timezone
from dateutil.parser import parse
from static_data import N_WEEKS
from event import CustomEvent
"""
settings format :
{
    choice: user's schedule choice (int),
    projectID: int,
    codes: [list of codes],
    priority: {code: priority}
    fts: [list of fts],
    id_list: [list of selected ids],
    weeks: [[list of IDs], [list of IDs], ..., [list of IDs]]
    check: state of checkboxes (from the UI)
}
"""


def saveSettings(link, session, choice=0, username=None, check=None):
    """
    Saves a user's session in the database with the corresponding link
    :param check: state of checkbobxes
    :param link: str, given to the user
    :param session: dict, the user's session
    :param choice: int, the choice of schedule to save
    :param username: if specified, the user's username
    :return: /
    """
    courses = getCoursesFromCodes(session['codes'], session['basic_context']['projectID'])
    if choice < 0:
        events = list(chain.from_iterable(chain.from_iterable(extractEvents(courses, view=session['id_list']))))
        weeks = [[event.getId() for event in events if event.getweek() == week] for week in range(N_WEEKS)]
    else:
        for course in courses: course.setEventWeight(session['basic_context']['priority'].get(course.code))
        events = compute_best(courses, fts=load_fts(session['fts']), nbest=3, view=session['id_list'], safe_compute=session['basic_context']['safe_compute'])[choice]
        weeks = [[event.getId() for event in events if event.getweek() == week] for week in range(N_WEEKS)]
    settings = {
        'choice': choice,
        'projectID': session['basic_context']['projectID'],
        'codes': session['codes'],
        'priority': session['basic_context']['priority'],
        'fts': session['fts'],
        'id_list': session['id_list'],
        'weeks': weeks,
        'check': check
    }
    setLink(link=link, username=username, settings=settings)


def updateSettings(link, session, choice=None, check=None):
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
        old_settings = getSettingsFromLink(link)
        choice = old_settings['choice']

    courses = getCoursesFromCodes(session['codes'], session['basic_context']['projectID'])
    if choice < 0:
        events = list(chain.from_iterable(chain.from_iterable(extractEvents(courses, view=session['id_list']))))
        weeks = [[event.getId() for event in events if event.getweek() == week] for week in range(N_WEEKS)]
    else:
        for course in courses: course.setEventWeight(session['basic_context']['priority'].get(course.code))
        events = compute_best(courses, fts=load_fts(session['fts']), nbest=3, view=session['id_list'], safe_compute=session['basic_context']['safe_compute'])[choice]
        weeks = [[event.getId() for event in events if event.getweek() == week] for week in range(N_WEEKS)]
    settings = {
        'choice': choice,
        'projectID': session['basic_context']['projectID'],
        'codes': session['codes'],
        'priority': session['basic_context']['priority'],
        'fts': session['fts'],
        'id_list': session['id_list'],
        'weeks': weeks,
        'check': check
    }
    updateSettingsFromLink(link=link, settings=settings)


def loadSettings(link):
    """
    :param link: str, given by the user
    :return: this link's corresponding settings
    """
    return getSettingsFromLink(link)


def getCalendarFromLink(link):
    """
    Returns the user's saved calendar in .ics format
    :param link: str, given by the user
    :return: str, the calendar in .ics format, or None if the link doesn't exist
    """
    if not isLinkPresent(link):
        return None
    settings = getSettingsFromLink(link)
    courses = getCoursesFromCodes(settings['codes'], projectID=settings['projectID'])
    events = (chain(*course.getView(week, ids)) for course in courses for week, ids in enumerate(settings['weeks']))
    return str(Calendar(events=chain(*events)))


def load_fts(fts_json):
    tz = timezone('Europe/Brussels')
    fts = list()
    for el in fts_json:
        t0 = parse(el['start']).astimezone(tz)
        t1 = parse(el['end']).astimezone(tz)
        dt = t1 - t0
        if el['title'] == 'High':
            fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=9))
        elif el['title'] == 'Medium':
            fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=6))
        elif el['title'] == 'Low':
            fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=1))
    return fts

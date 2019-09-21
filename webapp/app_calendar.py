import inspect
import json
import os
import re
import sys

from itertools import chain
from dateutil.parser import parse
from flask import request, session
from ics import Calendar
from pytz import timezone
from redis import Redis

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir + '/python')
from ade import get_courses_from_codes
from computation import compute_best, extractEvents
from event import CustomEvent, JSONfromEvents
from background_job import update_projects

# letters + number only regex
regex = re.compile('[^A-Z0-9]')
redis = Redis(host='localhost', port=6379)


def clear():
    """
    Called when the Clear button is pressed. Reinitialises this user's session.
    :return: /
    """
    session['data_base'].clear()
    session['data_sched'].clear()
    session['codes'].clear()
    session['fts'].clear()
    session['id_tab'].clear()
    session['id_list'] = None
    session['basic_context']['up_to_date'] = True
    session['basic_context']['priority'].clear()


def compute():
    """
    Computes the three best schedules based on the user sepcifications/settngs.
    Stores the result in data_sched.
    :return: /
    """
    if len(session['codes']) == 0:
        clear()
    else:
        courses = get_courses_from_codes(session['codes'], project_id=session['basic_context']['project_id'])
        for course in courses: course.setEventWeight(session['basic_context']['priority'].get(course.code))
        for i, sched in enumerate(compute_best(courses, fts=load_fts(), nbest=3, view=session['id_list'],
                                               safe_compute=session['basic_context']['safe_compute'])):
            session['data_sched']['sched_' + str(i + 1)] = json.dumps(JSONfromEvents(sched))
        session['basic_context']['up_to_date'] = True
    session.modified = True


def init():
    """
    Initializes this user's session.
    :return: /
    """
    # Is the session initialized ?
    session['init'] = True

    # user's course codes
    session['codes'] = list()

    # ADE event schedule
    session['data_base'] = list()

    # Computed schedules
    session['data_sched'] = dict()

    # Forbidden Time Slots
    session['fts'] = list()

    # Course IDs
    session['id_tab'] = dict()
    session['id_list'] = None

    # Other variables
    color_gradient = ['', '#374955', '#005376', '#00c0ff', '#1f789d', '#4493ba', '#64afd7', '#83ccf5', '#3635ff',
                      '#006c5a', '#3d978a']
    if not redis.exists('ADE_PROJECTS'): update_projects()
    session['basic_context'] = {'up_to_date': True, 'safe_compute': True, 'locale': None, 'gradient': color_gradient,
                                'project_id': 9, 'academic_years': json.loads(redis.get('ADE_PROJECTS')),
                                'priority': dict()}


def add_courses(codes):
    """
    Adds a course to this user's session (from a list of courses, inputed by the user)
    :param codes: user input
    :return: /
    """
    pattern = re.compile("^\s+|\s*,\s*|\s+$")
    codes = [x for x in pattern.split(codes) if x]
    for code in codes:
        add_course(code)


def add_course(code):
    """
    Adds one course to this user's session
    :param code: code of the course to add
    :return: /
    """
    # if len(code) > 12:
    #     code = code[0:12]
    # code = regex.sub('', code)
    if code is '' or code is None:
        return
    if code not in session['codes']:
        session['codes'].append(code)
        fetch_courses()
        session['basic_context']['up_to_date'] = False
        session.modified = True


def fetch_courses():
    """
    Fetches all the courses whose codes are given by session['codes'] and stores the resulting data in 'data_base'
    :return: /
    """
    courses = get_courses_from_codes(session['codes'], project_id=session['basic_context']['project_id'])
    fetch_id()
    events = chain.from_iterable(chain.from_iterable(extractEvents(courses, view=session['id_list'])))
    session['data_base'] = JSONfromEvents(events)
    session.modified = True


def fetch_id():
    """
    Generates the list of event IDs from this session's courses (as specified in session['code']).
    Stores the result in 'id_tab'
    :return: /
    """
    courses = get_courses_from_codes(session['codes'], project_id=session['basic_context']['project_id'])
    for course in courses:
        type_tab = {'CM': list(), 'TP': list(), 'EXAM': list(), 'ORAL': list(), 'Other': list()}
        for course_id in course.getSummary():
            temp = course_id.split(':')
            type_tab[temp[0]].append(temp[1])
        session['id_tab'][course.code] = type_tab
    for code in session['codes']:
        if code not in session['id_tab'].keys():
            session['id_tab'][code] = {}
    session.modified = True


def get_fts():
    """
    Function called when the user adds a FTS aka "Forbidden Time Slot".
    Stores the data transferred from the UI in the 'fts' variable.
    :return: /
    """
    msg = json.loads(request.form['fts'])
    session['fts'].clear()
    for el in msg:
        session['fts'].append(el)
    session['basic_context']['up_to_date'] = False
    session.modified = True


def get_id():
    """
    Called when the user presses the "Refresh" button. Updates the course data stored in data_sched
    according to the IDs the user specified on the UI.
    :return:
    """
    fetch_courses()
    session['basic_context']['up_to_date'] = False
    session.modified = True


def delete_course(code):
    """
    Deletes the course whose code is given by 'code'
    :param code: code of the course to delete
    :return: /
    """
    if code in session['codes']:
        session['codes'].remove(code)
        fetch_courses()
        session['basic_context']['up_to_date'] = False
        session.modified = True


def download_calendar(choice):
    """
    Generate the calendar's .ics file to be then downloaded.
    :param choice: choice of the schedule to download
    :return: string, the calendar's .ics file
    """
    courses = get_courses_from_codes(session['codes'], project_id=session['basic_context']['project_id'])
    if choice < 0:
        events = chain.from_iterable(chain.from_iterable(extractEvents(courses, view=session['id_list'])))
        calendar = Calendar(events=events)
    else:
        for course in courses: course.setEventWeight(session['basic_context']['priority'].get(course.code))
        events = compute_best(courses, fts=load_fts(), nbest=3, view=session['id_list'],
                              safe_compute=session['basic_context']['safe_compute'])
        calendar = Calendar(events=events[choice])
    return str(calendar)


def load_fts():
    """
    FTS parser.
    :return: list of CustomEvents representing the FTS as specified by the user.
    """
    tz = timezone('Europe/Brussels')
    fts = list()
    for el in session['fts']:
        t0 = parse(el['start']).astimezone(tz)
        t1 = parse(el['end']).astimezone(tz)
        if el['title'] == 'High' or el['title'] == 'Haut':
            fts.append(CustomEvent(el['title'], t0, t1, el['description'], '', weight=9))
        elif el['title'] == 'Medium' or el['title'] == 'Moyen':
            fts.append(CustomEvent(el['title'], t0, t1, el['description'], '', weight=6))
        elif el['title'] == 'Low' or el['title'] == 'Bas':
            fts.append(CustomEvent(el['title'], t0, t1, el['description'], '', weight=1))
    return fts

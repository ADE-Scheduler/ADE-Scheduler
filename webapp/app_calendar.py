from flask import request, session

from pytz import timezone
from dateutil.parser import parse
from itertools import chain
from ics import Calendar
import json
import re

import sys, os, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir + '/python')
from ade import getCoursesFromCodes
from computation import compute_best, extractEvents
from event import CustomEvent, JSONfromEvents
from static_data import ACADEMIC_YEARS

# letters + number only regex
regex = re.compile('[^A-Z0-9]')


def clear():
    session['data_base'].clear()
    session['data_sched'].clear()
    session['codes'].clear()
    session['fts'].clear()
    session['id_tab'].clear()
    session['id_list'] = None
    session['basic_context']['up_to_date'] = True
    session['basic_context']['priority'].clear()


def compute():
    if len(session['codes']) == 0:
        clear()
    else:
        courses = getCoursesFromCodes(session['codes'], projectID=session['basic_context']['projectID'])
        for course in courses: course.setEventWeight(session['basic_context']['priority'].get(course.code))
        for i, sched in enumerate(compute_best(courses, fts=load_fts(), nbest=3, view=session['id_list'], safe_compute=session['basic_context']['safe_compute'])):
            session['data_sched']['sched_' + str(i + 1)] = json.dumps(JSONfromEvents(sched))
        session['basic_context']['up_to_date'] = True
    session.modified = True


def init():
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
    color_police = ['white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white', 'white',
                    'white', 'white']
    session['basic_context'] = {'up_to_date': True, 'safe_compute': True, 'locale': None, 'gradient': color_gradient,
                                'police': color_police, 'projectID': 9, 'academic_years': ACADEMIC_YEARS, 'priority': {}}


def add_courses(codes):
    pattern = re.compile("^\s+|\s*,\s*|\s+$")
    codes = [x for x in pattern.split(codes) if x]
    for code in codes:
        add_course(code)


def add_course(code):
    if len(code) > 12:
        code = code[0:12]
    code = regex.sub('', code)
    if code is '' or code is None:
        return
    if code not in session['codes']:
        session['codes'].append(code)
        fetch_courses()
        session['basic_context']['up_to_date'] = False
        session.modified = True


def fetch_courses():
    courses = getCoursesFromCodes(session['codes'], projectID=session['basic_context']['projectID'])
    fetch_id()
    events = chain.from_iterable(chain.from_iterable(extractEvents(courses, view=session['id_list'])))
    session['data_base'] = JSONfromEvents(events)
    session.modified = True


def fetch_id():
    courses = getCoursesFromCodes(session['codes'], projectID=session['basic_context']['projectID'])
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
    msg = json.loads(request.form['fts'])
    session['fts'].clear()
    for el in msg:
        session['fts'].append(el)
    session['basic_context']['up_to_date'] = False
    session.modified = True


def get_id():
    fetch_courses()
    session['basic_context']['up_to_date'] = False
    session.modified = True


def delete_course(code):
    if code in session['codes']:
        session['codes'].remove(code)
        fetch_courses()
        session['basic_context']['up_to_date'] = False
        session.modified = True


def download_calendar(choice):
    courses = getCoursesFromCodes(session['codes'], projectID=session['basic_context']['projectID'])
    if choice < 0:
        events = chain.from_iterable(chain.from_iterable(extractEvents(courses, view=session['id_list'])))
        calendar = Calendar(events=events)
    else:
        for course in courses: course.setEventWeight(session['basic_context']['priority'].get(course.code))
        events = compute_best(courses, fts=load_fts(), nbest=3, view=session['id_list'], safe_compute=session['basic_context']['safe_compute'])
        calendar = Calendar(events=events[choice])
    return str(calendar)


def load_fts():
    tz = timezone('Europe/Brussels')
    fts = list()
    for el in session['fts']:
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

from flask import request, session


from pytz import timezone
from dateutil.parser import parse
import json

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir+'/python')
from ade import getCoursesFromCodes
from static_data import Q1, Q2, Q3
from computation import parallel_compute
from event import CustomEvent, EventCM
import library


def clear():
    session['data_base'].clear()
    session['data_sched'].clear()
    session['codes'].clear()
    session['fts'].clear()
    session['id_tab'].clear()
    session['id_list'] = None
    session['basic_context']['up_to_date'] = True


def compute():
    if len(session['codes']) == 0:
        clear()
    else:
        courses = getCoursesFromCodes(session['codes'])
        tz = timezone('Europe/Brussels')
        fts = list()
        for el in session['fts']:
            t0 = parse(el['start']).astimezone(tz)
            t1 = parse(el['end']).astimezone(tz)
            dt = t1 - t0
            if el['title'] == 'High':
                fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=5))
            elif el['title'] == 'Medium':
                fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=3))
            elif el['title'] == 'Low':
                fts.append(CustomEvent(el['title'], t0, dt, el['description'], '', weight=1))
        scheds, score = parallel_compute(courses, forbiddenTimeSlots=fts, nbest=3)
        i = 1
        for sched in scheds:
            temp_sched = list()
            for week in sched:
                for event in week:
                    temp = {'start': str(event.begin), 'end': str(event.end), 'title': event.id,
                            'editable': False, 'code': event.code,
                            'description': event.name + '\n' + event.location + ' - ' + str(
                                event.duration) + '\n' + str(event.description)}
                    temp_sched.append(temp)
            session['data_sched']['sched_' + str(i)] = json.dumps(temp_sched)
            i += 1
        session['basic_context']['up_to_date'] = True
    session.modified = True


def init():
    # Are cookies initialized ?
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
    color_gradient = ['', '#374955', '#005376', '#00c0ff', '#1f789d', '#4493ba', '#64afd7', '#83ccf5', '#a1eaff', '#006c5a', '#3d978a']
    color_police = ['black', 'white', 'white', 'black', 'black', 'black', 'black', 'black', 'black', 'black', 'black', 'black', 'black']
    session['basic_context'] = {'up_to_date': True, 'safe_compute': None, 'locale': 'en', 'gradient': color_gradient, 'police': color_police}


def add_course(code):
    if code is '' or code is None:
        return
    if code not in session['codes']:
        session['codes'].append(code)
        fetch_courses()
        session['basic_context']['up_to_date'] = False
        session.modified = True


def fetch_courses():
    courses = getCoursesFromCodes(session['codes'])
    fetch_id()
    session['data_base'].clear()
    for course in courses:
        session['data_base'] += course.getEventsJSON()
    session.modified = True


def fetch_id():
    courses = getCoursesFromCodes(session['codes'])
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
    session.modified = True


def get_id():
    pass


def delete_course(code):
    if code in session['codes']:
        session['codes'].remove(code)
        fetch_courses()
        session['basic_context']['up_to_date'] = False
        session.modified = True
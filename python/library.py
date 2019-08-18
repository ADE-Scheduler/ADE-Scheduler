import os
from pickle import dump, load
from glob import glob
from ade import getCoursesFromCodes
from itertools import chain
from ics import Calendar
from event import gregorianToADE
from static_data import ID

current = os.path.dirname(__file__)
save_folder = os.path.join(current, 'saves')
save_type = os.path.join(save_folder, '*.p')

"""
settings format :
{codes:[list of codes],
    weeks:{
        dict containing (key->int, value->[list of ids])
    }}
"""

def get(settings:dict):
    courses = getCoursesFromCodes(settings['codes'], weeks=map(gregorianToADE, settings['weeks'].keys()), projectID=ID)
    events = (chain(*course.getView(week, ids)) for course in courses for week, ids in settings['weeks'].items())
    return chain(*events)

def getCalendar(n=0):
    settings = getSettings(n)
    events = get(settings)
    c = Calendar(events=events)
    file = os.path.join(save_folder, str(n)+'.ics')
    with open(file, 'w') as f:
        f.writelines(c)
    return file


def clearLibrary():
    for file in glob(save_type):
        os.remove(file)

def addSettings(settings):
    files = sorted(glob(save_type))

    if len(files) == 0:
        file = os.path.join(save_folder, '0.p') # first file
    else:
        name, _ = os.path.splitext(os.path.basename(files[-1])) # get last file added
        next_name = 1 + int(name)
        file = os.path.join(save_folder, str(next_name)+'.p')

    f = open(file, 'wb')
    dump(settings, f)

def getSettings(n):
    # TODO: on devrait gerer les erreurs si le fichier n'existe pas
    file = os.path.join(save_folder, str(n)+'.p')
    f = open(file, 'rb')
    return load(f)

def settingsFromEvents(events):
    events =  list(events)
    codes = set(event.code for event in events)
    weeks = set(event.getweek() for event in events)
    settings = {'codes':codes, 'weeks':{week:{event.getId() for event in events if event.getweek()==week} for week in weeks}}
    return settings
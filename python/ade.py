import re
***REMOVED***
***REMOVED***
from event import extractType, extractDateTime
from course import Course
from professor import Professor
***REMOVED***
***REMOVED***
from pickle import dumps, loads
***REMOVED***
from static_data import N_WEEKS
from datetime import timedelta

import time

SPLITTED_COURSES = ['(LANGL)']


def getCoursesFromCodes(codes, projectID=9, weeks=range(N_WEEKS)):
    """
    Fetches course schedule from Redis' course cache
    :param codes: list of str
    :param projectID: int
    :param weeks: list of int
    :return: Course list
    """
    ***REMOVED***
    courses = list()
    not_added = list()

    for code in codes:
        course = redis.get(str(projectID) + code)
        if not course:
            not_added.append(code)
        else:
            courses.append(loads(course))

    tstart = time.clock()
    loaded_courses = getCoursesFromADE(not_added, projectID, redis=redis)
    print('Total time: ' + str(time.clock()-tstart))

    for course in loaded_courses:
        courses.append(course)
        redis.setex(str(projectID) + course.code, timedelta(days=1), value=dumps(course))    # valid for one day

    return courses


def getCoursesFromADE(codes, projectID, redis=None):
    """
    Fetches courses schedule from UCLouvain's ADE web API
    :param codes: list of str
    :param projectID: int
    :param redis: instance of a Redis server, on which an access token may be stored. If not specified, simply retrieve
                  a new token.
    :return: list of Courses
    """
    if not codes:
        return list()

    # Some variables
    course_added = []
    course_list = []

    # We retrieve the access token and construct the URL and the headers for the requests
    if not redis:
        ***REMOVED***
    else:
        token = redis.get('ade_webapi_token')
        if not token:
            token, expiry = get_token()
            if expiry > 10:
                redis.setex('ade_webapi_token', timedelta(seconds=expiry-10), value=dumps(token))
        else:
            token = loads(token)
    ***REMOVED***
    ***REMOVED***
          str(projectID) + '&function='

    tstart2 = time.clock()

    # We get the ressource IDs for each code
    resources_id = ''
    for code in codes:
        print(code)
        r = requests.get(url + 'getResources&name=' + code, headers=headers)
        ***REMOVED***
        for resource in root.xpath('//resource'):
            resource_id = resource.attrib['id']
            resources_id += (resource_id + '|')
    resources_id = resources_id[0:-1]
    print('Temps intermédiaire: ' + str(time.clock()-tstart2))

    # We get the events
    r = requests. get(url + 'getActivities&tree=false&detail=17&resources=' + resources_id, headers=headers)
    ***REMOVED***
    for activity in root.xpath('//activity'):
        activity_type = activity.attrib['type']
        activity_id = activity.attrib['name']
        activity_name = activity.attrib['code']
        for event in activity[0]:
            start = event.attrib['startHour']
            end = event.attrib['endHour']
            date = event.attrib['date']
            event_loc = ''
            event_prof = ''
            event_code = None
            for participant in event[0]:
                category = participant.attrib.get('category')
                if category == 'classroom':
                    event_loc = participant.attrib['name']
                elif category == 'instructor':
                    event_prof = participant.attrib['name']
                elif category == 'category5':
                    event_code = participant.attrib['name']

            # We create the event
            t0, t1 = extractDateTime(date, start, end)
            event = extractType(activity_type, activity_id)(t0, t1, event_code, activity_name, Professor(event_prof,''),
                                                            event_loc, id=activity_id)
            try:  # The course was already added
                i = course_added.index(event_code)
                course_list[i].addEvent(event)
            except ValueError:  # This is a new course
                course_added.append(event_code)
                course_list.append(Course(event_code, activity_name))
                course_list[-1].addEvent(event)

    # # We treat "splitted courses" (such as: LANGL1873)
    # for splitted_course in SPLITTED_COURSES:
    #     for course in filter(lambda c: re.search(splitted_course, c.code, re.IGNORECASE), course_list):
    #         course.join()
    # TODO: SPLITTED COURSES --> .join() function broken

    return course_list

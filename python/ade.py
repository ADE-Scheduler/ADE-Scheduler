import requests
from lxml import etree
from event import extractType, extractDateTime
from course import Course
from professor import Professor
from hidden import get_token, user, password
from redis import Redis
from pickle import dumps, loads
from personnal_data import redis_ip
from datetime import timedelta
from pandas import DataFrame
from collections import Counter


def get_courses_from_codes(codes, project_id=9):
    """
    Fetches course schedule from Redis' course cache
    :param codes: list of str
    :param project_id: int
    :param weeks: list of int
    :return: Course list
    """
    redis = Redis(host=redis_ip)
    courses = list()
    not_added = list()

    for code in codes:
        course = redis.get(str(project_id) + code)
        if not course:
            not_added.append(code)
        else:
            courses.append(loads(course))

    for course in get_courses_from_ade(not_added, project_id, redis=redis):
        courses.append(course)
        redis.setex(str(project_id) + course.code, timedelta(days=1), value=dumps(course))    # valid for one day

    return courses


def get_courses_from_ade(codes, project_id, redis=None):
    """
    Fetches courses schedule from UCLouvain's ADE web API
    :param codes: list of str
    :param project_id: int
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
        token, _ = get_token()
    else:
        token = redis.get('ade_webapi_token')
        if not token:
            token, expiry = get_token()
            if expiry > 10:
                redis.setex('ade_webapi_token', timedelta(seconds=expiry-10), value=token)
        else:
            token = token.decode()
    headers = {'Authorization': 'Bearer ' + token}
    url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&projectId=' + \
          str(project_id) + '&function='

    # We get the ressource IDs for each code
    if not redis or not redis.exists('ade_webapi_id'):
        r = requests.get(url + 'getResources&detail=2', headers=headers)
        root = etree.fromstring(r.content)
        df = DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(), root.xpath('//resource/@name'))
                       , columns=['id'])
        hash_table = df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()
        resources_id = '|'.join(filter(None, [hash_table.get(code) for code in codes]))
        if redis:
            redis.hmset('ade_webapi_id', hash_table)
            redis.expire('ade_webapi_id', timedelta(days=1))
        if not resources_id:
            return list()
    else:
        result = list(filter(None, redis.hmget('ade_webapi_id', codes)))
        if result:
            resources_id = '|'.join(map(lambda x: x.decode(), result))
        else:
            return list()

    # We get the events
    r = requests. get(url + 'getActivities&tree=false&detail=17&resources=' + resources_id, headers=headers)
    root = etree.fromstring(r.content)

    courses = dict()

    for activity in root.xpath('//activity'):
        activity_id = activity.attrib['name']
        activity_type = activity.attrib['type']
        activity_name = activity.attrib['code']

        print(activity_type, activity_id, activity_name)

        codes = activity.xpath('.//eventParticipant[@category="category5"]/@name')

        activity_code = Counter(codes).most_common()[0][0]

        print(activity_code)

        events = list()

        if activity_code not in courses.keys():
            courses[activity_code] = Course(activity_code, activity_name)

        z = activity.xpath('.//event')

        for event in activity.xpath('.//event'):
            event_date = event.attrib['date']
            event_start = event.attrib['startHour']
            event_end = event.attrib['endHour']

            classroom = event.xpath('.//eventParticipant[@category="classroom"]/@name')
            events_classroom = classroom[0] if classroom else ''
            instructor = event.xpath('.//eventParticipant[@category="instructor"]/@name')
            events_instructor = instructor[0] if instructor else ''
            print(events_classroom, events_instructor)

            # We create the event
            t0, t1 = extractDateTime(event_date, event_start, event_end)
            event = extractType(activity_type, activity_id)(t0, t1, activity_code, activity_name,
                                                            Professor(events_instructor, ''),
                                                            events_classroom, id=activity_id)

            courses[activity_code].addEvent(event)

            events.append(event)

        courses[activity_code].add_activity(activity_type, activity_id, events)

    print(courses)

    return courses.values()

"""
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
            event_code = ''
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
                course_list[-1].addEvent(event)"""


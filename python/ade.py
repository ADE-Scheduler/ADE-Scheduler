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


def getCoursesFromCodes(codes, projectID=9):
    """
    Fetches course schedule from Redis' course cache
    :param codes: list of str
    :param projectID: int
    :param weeks: list of int
    :return: Course list
    """
    redis = Redis(host=redis_ip)
    courses = list()
    not_added = list()

    for code in codes:
        course = redis.get(str(projectID) + code)
        if not course:
            not_added.append(code)
        else:
            courses.append(loads(course))

    for course in getCoursesFromADE(not_added, projectID, redis=redis):
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
          str(projectID) + '&function='

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
                course_list[-1].addEvent(event)

    return course_list

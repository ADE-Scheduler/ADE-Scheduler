import requests
from lxml import etree
from event import extractType, extractDateTime
from course import Course
from professor import Professor
from hidden import get_token, user, password
from redis import Redis
from pickle import dumps, loads
from datetime import timedelta
from pandas import DataFrame


def get_courses_from_codes(codes, project_id=9):
    """
    Fetches course schedule from Redis' course cache
    :param codes: list of str
    :param project_id: int
    :param weeks: list of int
    :return: Course list
    """
    redis = Redis(host='localhost')
    courses = list()
    not_added = list()

    for code in codes:
        course = redis.hget(name='Project=' + str(project_id), key=code)
        if not course:
            not_added.append(code)
        else:
            courses.append(loads(course))

    for code in not_added:
        course = get_courses_from_ade(code, project_id, redis=redis)
        courses.append(course)
        redis.hset(name='Project=' + str(project_id), key=course.code, value=dumps(course))
        redis.expire(course.code, time=timedelta(hours=3))

    return courses


def get_courses_from_ade(code, project_id, redis=None):
    """
    Fetches courses schedule from UCLouvain's ADE web API
    :param code: str
    :param project_id: int
    :param redis: instance of a Redis server, on which an access token may be stored. If not specified, simply retrieve
                  a new token.
    :return: Course object
    """
    # Course to be returned
    course = None

    # We retrieve the access token and construct the URL and the headers for the requests
    if not redis:
        token, _ = get_token()
    else:
        token = redis.get('ade_webapi_token')
        if not token:
            token, expiry = get_token()
            if expiry > 10:
                redis.setex('ade_webapi_token', timedelta(seconds=expiry - 10), value=token)
        else:
            token = token.decode()
    headers = {'Authorization': 'Bearer ' + token}
    url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&projectId=' + \
          str(project_id) + '&function='

    # We get the ressource ID
    if not redis or not redis.exists('ade_webapi_id'):
        r = requests.get(url + 'getResources&detail=2', headers=headers)
        root = etree.fromstring(r.content)
        df = DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(), root.xpath('//resource/@name'))
                       , columns=['id'])
        hash_table = df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()
        resources_id = '|'.join(filter(None, [hash_table.get(code)]))
        if redis:
            redis.hmset('ade_webapi_id', hash_table)
            redis.expire('ade_webapi_id', timedelta(days=1))
        if not resources_id:
            return list()
    else:
        result = list(filter(None, redis.hmget('ade_webapi_id', code)))
        if result:
            resources_id = '|'.join(map(lambda x: x.decode(), result))
        else:
            return list()

    # We get the events
    r = requests.get(url + 'getActivities&tree=false&detail=17&resources=' + resources_id, headers=headers)
    root = etree.fromstring(r.content)
    for activity in root.xpath('//activity'):
        activity_type = activity.attrib['type']
        activity_id = activity.attrib['name']
        activity_name = activity.attrib['code']
        for event in activity[0]:
            start = event.attrib['startHour']
            end = event.attrib['endHour']
            date = event.attrib['date']
            event_loc = ' '.join(event.xpath('.//eventParticipant[@category="classroom"]/@name'))
            event_prof = ' '.join(event.xpath('.//eventParticipant[@category="instructor"]/@name'))

            # We create the event and add it to the Course object
            t0, t1 = extractDateTime(date, start, end)
            event = extractType(activity_type, activity_id)(t0, t1, code, activity_name,
                                                            Professor(event_prof, ''), event_loc, id=activity_id)
            if course is None:
                course = Course(code, activity_name)
                course.addEvent(event)
            else:
                course.addEvent(event)

    if course is None:
        return list()
    else:
        return course

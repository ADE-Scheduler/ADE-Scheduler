import requests
from lxml import etree
from event import extractType, extractDateTime, extractCode
from course import Course
from professor import Professor
from hidden import get_token, user, password
from redis import Redis
from pickle import dumps, loads
from datetime import timedelta
from pandas import DataFrame
def getCoursesFromCodes(codes, project_id=9):
    """
    Fetches course schedule from Redis' course cache
    :param codes: list of str
    :param project_id: int
    :return: Course list
    """
    redis = Redis(host='localhost')
    courses = list()
    not_added = list()

    for code in codes:
        course = redis.get(name='{Project=' + str(project_id) + '}' + code)
        if not course:
            not_added.append(code)
        else:
            courses.append(loads(course))

    for code in not_added:
        course = getCoursesFromADE(code, project_id, redis=redis)
        if len(course) != 0:
            course = course[0]
            courses.append(course)
            redis.setex(name='{Project=' + str(project_id) + '}' + course.code, value=dumps(course),
                        time=timedelta(hours=3))

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
    if not codes:
        return None
    elif isinstance(codes, str):
        codes = [codes]

    # We retrieve the access token and construct the URL and the headers for the requests
    if not redis:
        token, _ = get_token()
    else:
        token = redis.get('ADE_WEBAPI_TOKEN')
        if not token:
            token, expiry = get_token()
            if expiry > 10:
                redis.setex('ADE_WEBAPI_TOKEN', timedelta(seconds=expiry - 10), value=token)
        else:
            token = token.decode()
    headers = {'Authorization': 'Bearer ' + token}
    url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&projectId=' + \
          str(project_id) + '&function='

    # We get the ressource ID
    if not redis or not redis.exists('{Project=' + str(project_id) + '}ADE_WEBAPI_ID'):
        r = requests.get(url + 'getResources&detail=2', headers=headers)
        root = etree.fromstring(r.content)
        df = DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(), root.xpath('//resource/@name'))
                       , columns=['id'])
        hash_table = df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()
        resources_id = '|'.join(filter(None, [hash_table.get(code) for code in codes]))

        if redis:
            redis.hmset('{Project=' + str(project_id) + '}ADE_WEBAPI_ID', hash_table)
            redis.expire('{Project=' + str(project_id) + '}ADE_WEBAPI_ID', timedelta(days=1))
        if not resources_id:
            return None
    else:
        result = list(filter(None, redis.hmget('{Project=' + str(project_id) + '}ADE_WEBAPI_ID', code)))
        if result:
            resources_id = '|'.join(map(lambda x: x.decode(), result))
        else:
            return None

    # We get the events
    r = requests.get(url + 'getActivities&tree=false&detail=17&resources=' + resources_id, headers=headers)
    root = etree.fromstring(r.content)

    courses = dict()

    for activity in root.xpath('//activity'):
        activity_id = activity.attrib['name']
        activity_type = activity.attrib['type']
        activity_name = activity.attrib['code']

        event_type = extractType(activity_type, activity_id)

        codes = activity.xpath('.//eventParticipant[@category="category5"]/@name')

        events = activity.xpath('.//event')

        if len(codes) == 0:
            activity_code = extractCode(activity_id)
        else:
            activity_code = Counter(codes).most_common()[0][0]

        events_list = list()

        if activity_code not in courses.keys():
            courses[activity_code] = Course(activity_code, activity_name)

        for event in events:
            event_date = event.attrib['date']
            event_start = event.attrib['startHour']
            event_end = event.attrib['endHour']

            classroom = event.xpath('.//eventParticipant[@category="classroom"]/@name')
            events_classroom = classroom[0] if classroom else ''
            instructor = event.xpath('.//eventParticipant[@category="instructor"]/@name')
            events_instructor = instructor[0] if instructor else ''

            # We create the event
            t0, t1 = extractDateTime(event_date, event_start, event_end)

            event = event_type(t0, t1, activity_code, activity_name,
                               Professor(events_instructor, ''),
                               events_classroom, id=activity_id)

            events_list.append(event)

        courses[activity_code].add_activity(event_type, activity_id, events_list)

    return list(courses.values())

import requests
from lxml import etree
from event import extract_type, extract_datetime, extract_code
from course import Course
from professor import Professor
from hidden import get_token, user, password
from redis import Redis
from pickle import dumps, loads
from datetime import timedelta
from collections import Counter
import json


def ade_request(redis, *args):
    token = redis.get('ADE_WEBAPI_TOKEN')
    if not token:
        token, expiry = get_token()
        if expiry > 10:
            redis.setex('ADE_WEBAPI_TOKEN', timedelta(seconds=expiry - 10), value=token)
    else:
        token = token.decode()
    headers = {'Authorization': 'Bearer ' + token}
    url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&' + '&'.join(args)

    r = requests.get(url=url, headers=headers)
    return etree.fromstring(r.content)


def get_courses_from_codes(codes, project_id=9):
    """
    Fetches course schedule from Redis' course cache
    :param codes: list of str
    :param project_id: int
    :return: dict with: {code1: list of Courses, code2: list of Courses, ...}
    """
    redis = Redis(host='localhost')
    courses = dict()
    not_added = list()

    if isinstance(codes, str):
        codes = [codes]

    for code in codes:
        course = redis.get(name='{Project=' + str(project_id) + '}' + code)
        if not course:
            not_added.append(code)
        else:
            courses[code] = loads(course)

    for code in not_added:
        if 'LOCAL-' in code:
            tab = get_courses_from_ade(code.split('-')[-1], project_id, redis=redis, is_local=True)
        else:
            tab = get_courses_from_ade(code, project_id, redis=redis)
        courses[code] = tab
        redis.setex(name='{Project=' + str(project_id) + '}' + code, value=dumps(tab),
                    time=timedelta(hours=3))

    return courses


def get_courses_from_ade(codes, project_id, redis=None, is_local=False):
    """
    Fetches courses schedule from UCLouvain's ADE web API
    :param is_local: boolean
    :param codes: str or list of str
    :param project_id: int
    :param redis: instance of a Redis server, on which an access token may be stored. If not specified, simply retrieve
                  a new token.
    :return: list of Courses
    """
    if not codes:
        return list()
    elif isinstance(codes, str):
        codes = [codes]

    # Courses to be returned
    courses = dict()

    # We get the resources ID
    h_map = '{Project=%d}ADE_WEBAPI_ID' % project_id
    if not redis or not redis.exists(h_map):
        from background_job import update_resources_ids
        update_resources_ids()

    result = list(filter(None, redis.hmget(h_map, codes)))
    if result:
        resources_id = '|'.join(map(lambda x: x.decode(), result))
    else:
        return list()

    # We get the classrooms
    h_map = '{Project=%d}CLASSROOMS' % project_id
    if not redis or not redis.exists(h_map):
        from background_job import update_classrooms
        update_classrooms()

    # We get the events
    root = ade_request(redis, 'projectId=%d' % project_id,
                       'function=getActivities', 'tree=false',
                       'detail=17', 'resources=' + resources_id)

    for activity in root.xpath('//activity'):
        activity_id = activity.attrib['name']
        activity_type = activity.attrib['type']
        activity_name = activity.attrib['code']

        event_type = extract_type(activity_type, activity_id)
        event_codes = activity.xpath('.//eventParticipant[@category="category5"]/@name')
        events = activity.xpath('.//event')
        events_list = list()

        if len(event_codes) == 0:
            activity_code = extract_code(activity_id)
        else:
            activity_code = Counter(event_codes).most_common()[0][0]
        if activity_code is '':
            activity_code = 'Other'

        for event in events:
            event_date = event.attrib['date']
            event_start = event.attrib['startHour']
            event_end = event.attrib['endHour']
            classrooms = event.xpath('.//eventParticipant[@category="classroom"]/@name')
            location = ''
            for classroom in classrooms:
                infos = redis.hmget(h_map, classroom)
                if infos[0] is not None:
                    address = json.loads(infos[0])
                    location = ''
                    if address['type'] != '':
                        location += '\n' + address['type']
                    if address['size'] != '':
                        if location == '':
                            location += '\nTaille :' + address['size']
                        else:
                            location += ', taille :' + address['size']
                    if address['address_2'] != '':
                        location += '\n' + address['address_2']
                    if address['address_1'] != '':
                        if location != '' and ['address_2'] != '':
                            location += ' ' + address['address_1']
                        else:
                            location += '\n' + address['address_1']
                    if address['zipCode'] != '':
                        location += '\n' + address['zipCode']
                    if address['city'] != '':
                        if location != '' and address['zipCode'] != '':
                            location += ' ' + address['city']
                        else:
                            location += '\n' + address['city']
                    if address['country'] != '':
                        location += '\n' + address['country']
                    break

            event_classroom = ' '.join(classrooms)
            event_address = event_classroom + location
            event_instructor = ' '.join(event.xpath('.//eventParticipant[@category="instructor"]/@name'))

            # Check if the event is taking place in the requested local
            if is_local and any(c.lower() not in event_classroom.lower() for c in codes):
                continue

            # We create the event
            t0, t1 = extract_datetime(event_date, event_start, event_end)
            event = event_type(t0, t1, activity_code, activity_name, Professor(event_instructor, ''), event_address,
                               classroom=event_classroom, id=activity_id)
            events_list.append(event)

        if activity_code not in courses and events_list:
            courses[activity_code] = Course(activity_code, activity_name)
        if events_list:
            courses[activity_code].add_activity(event_type, activity_id, events_list)

    return list(courses.values())

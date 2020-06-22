import requests
import time
from lxml import etree
import pandas as pd
from collections import defaultdict, Counter
from backend.classrooms import Classroom, Address
from backend.courses import Course
from backend import professors
import backend.events


class ExpiredTokenError(Exception):

    def __str__(self):
        return 'The token you were using is now expired! Renew the token to proceed normally.'


class Client:

    def __init__(self, credentials):
        self.credentials = credentials
        self.token = None
        self.expiration = None
        self.renew_token()

    def is_expired(self):
        # TODO: verify validity of this relation
        return self.expiration < time.time()

    def expire(self):
        return self.expiration - time.time()

    def renew_token(self):
        self.token, self.expiration = get_token(self.credentials)
        self.expiration += time.time()

    def request(self, **kwargs):

        if self.is_expired():
            raise ExpiredTokenError

        headers = {'Authorization': 'Bearer ' + self.token}
        user = self.credentials['user']
        password = self.credentials['password']
        args = '&'.join('='.join(map(str, _)) for _ in kwargs.items())
        url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&' + args
        return requests.get(url=url, headers=headers)

    def get_project_id(self):
        return self.request(function='getProjects', detail=2)

    def get_resource_ids(self, project_id):
        return self.request(projectId=project_id, function='getResources', detail=2)

    def get_classrooms(self, project_id):
        return self.request(projectId=project_id, function='getResources',
                            detail=13, tree='false', category='classroom')

    def get_activities(self, resource_ids: list, project_id):
        return self.request(projectId=project_id, function='getActivities',
                            tree='false', detail=17, resources='|'.join(map(str, resource_ids)))


def get_token(credentials):
    url = credentials['url']
    data = credentials['data']
    authorization = credentials['Authorization']
    header = {'Authorization': authorization}
    r = requests.post(url=url, headers=header, data=data).json()
    return r['access_token'], int(r['expires_in'])


def request_to_root(request):
    return etree.fromstring(request.content)


def request_to_project_ids(project_ids_request):
    root = request_to_root(project_ids_request)
    ids = root.xpath('//project/@id')
    years = root.xpath('//project/@name')

    return zip(map(int, ids), years)


def request_to_resource_ids(resource_ids_request):
    root = request_to_root(resource_ids_request)
    df = pd.DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(),
                                                                   root.xpath('//resource/@name'))
                      , columns=['id'])
    return df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()


def room_to_classroom(room):
    address = Address(
        address1=room.get('address1'),
        address2=room.get('address2'),
        zipCode=room.get('zipCode'),
        city=room.get('city'),
        country=room.get('country')
    )
    classroom = Classroom(
        name=room.get('name'),
        type=room.get('type'),
        size=room.get('size'),
        id=room.get('id'),
        address=address
    )

    return classroom


def request_to_classrooms(classrooms_request):

    root = request_to_root(classrooms_request)

    rooms = root.xpath('//room')

    classrooms = []
    for room in rooms:
        classroom = room_to_classroom(room)
        classrooms.append(classroom)

    return classrooms


def request_to_courses(activities_request):

    root = request_to_root(activities_request)

    courses = defaultdict(Course)

    # Each activity has its unique event type
    for activity in root.xpath('//activity'):
        print('ici')
        activity_id = activity.attrib['name']
        activity_type = activity.attrib['type']
        activity_name = activity.attrib['code']

        event_type = backend.events.extract_type(activity_type, activity_id)
        event_codes = activity.xpath('.//eventParticipant[@category="category5"]/@name')
        events = activity.xpath('.//event')
        events_list = list()

        if len(event_codes) == 0:
            activity_code = backend.events.extract_code(activity_id)
        else:
            activity_code = Counter(event_codes).most_common()[0][0]
        if activity_code is '':
            activity_code = 'Other'

        for event in events:
            event_date = event.attrib['date']
            event_start = event.attrib['startHour']
            event_end = event.attrib['endHour']
            rooms = event.xpath('.//eventParticipant[@category="classroom"]')
            classrooms = [room_to_classroom(room) for room in rooms]
            print('classroom', classrooms)

            event_classroom = classrooms
            event_address = backend.classrooms.merge_classrooms(classrooms)

            xy = event.xpath('.//eventParticipant[@category="instructor"]')
            for xyz in xy:
                print(xyz.keys())
            instructor_names = event.xpath('.//eventParticipant[@category="instructor"]/@name')
            instructor_emails = event.xpath('.//eventParticipant[@category="instructor"]/@id')  # TODO: email ?
            event_instructor = professors.merge_professors(professors.Professor(name, email)
                                                           for name, email in zip(instructor_names, instructor_emails))

            # We create the event
            t0, t1 = backend.events.extract_datetime(event_date, event_start, event_end)
            event = event_type(t0, t1, activity_code, activity_name, event_instructor, event_address,
                               classroom=event_classroom, id=activity_id)
            events_list.append(event)

        if events_list:
            courses[activity_code].add_activity(event_type, activity_id, events_list)


if __name__ == "__main__":

    import backend.credentials as credentials

    filename = "/home/jerome/ade_api.json"

    credentials.set_credentials(filename, credentials.ADE_API_CREDENTIALS)

    credentials = credentials.get_credentials(credentials.ADE_API_CREDENTIALS)

    client = Client(credentials)

    request = client.get_project_id()

    ids_years = request_to_project_ids(request)

    # On peut l'obtenir de ids_years
    project_id = 9

    request = client.get_resource_ids(project_id)

    resources_ids = request_to_resource_ids(request)

    print('All resources:')
    print(len(resources_ids), resources_ids)

    id = resources_ids['LMECA2732']

    # 'LBRAI2206': '12438'

    request = client.get_activities([id], project_id)

    resources_ids = request_to_courses(request)

    print(resources_ids)

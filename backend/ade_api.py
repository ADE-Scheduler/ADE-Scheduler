import requests
import time
from lxml import etree
import pandas as pd
from collections import defaultdict, Counter
from backend.classrooms import Classroom, Address
from backend.courses import Course
from backend.resources import Resource
from backend import professors
import backend.events
from typing import Dict, Union, List, Tuple, Iterator


class ExpiredTokenError(Exception):
    """
    Exception that will occur if a token is expired.
    """
    def __str__(self):
        return 'The token you were using is now expired! Renew the token to proceed normally.'


ClientCredentials = Dict[str, Union[str, List[int]]]
Request = Union[str, int]
DEFAULT_PROJECT_ID = 9


class Client:
    """
    A client is an entity which has granted access to ADE API, via its credentials.

    :param credentials: all information needed to make requests to API
    :param credentials: ClientCredentials

    :Example:

    >>> import backend.credentials as credentials
    >>> credentials = credentials.get_credentials(credentials.ADE_API_CREDENTIALS)
    >>> client = Client(credentials)
    """
    def __init__(self, credentials: ClientCredentials):
        self.credentials = credentials
        self.token = None
        self.expiration = None
        self.renew_token()

    def is_expired(self) -> bool:
        """
        Returns whether the current token is expired.

        :return: True if the token is expired
        :rtype: bool
        """
        # TODO: verify validity of this relation
        return self.expiration < time.time()

    def expire_in(self) -> float:
        """
        Returns the time remaining before the token expires.

        :return: the time remaining in seconds, 0 if expired
        :rtype: float
        """
        return max(self.expiration - time.time(), 0)

    def renew_token(self) -> None:
        """
        Renews the current token requesting a new one.
        """
        self.token, self.expiration = get_token(self.credentials)
        self.expiration += time.time()

    def request(self, **kwargs: Request) -> requests.Response:
        """
        Performs a request to the API with given parameters.

        :param kwargs: set of key / value parameters that will be merged
        :type kwargs: Request
        :return: the response
        :rtype: request.Response
        :raises ExpiredTokenError: if the token is expired an exception occurs
        :raises HTTPError: if the request is unsuccessful (oustide the 2XX-3XX range)
        """
        if self.is_expired():
            raise ExpiredTokenError

        headers = {'Authorization': 'Bearer ' + self.token}
        user = self.credentials['user']
        password = self.credentials['password']
        args = '&'.join('='.join(map(str, _)) for _ in kwargs.items())
        url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&' + args

        resp = requests.get(url=url, headers=headers)
        resp.raise_for_status()

        return resp

    def get_project_ids(self) -> requests.Response:
        """
        Requests the project ids currently available; each year (project) corresponds to an id.

        :return: the response
        :rtype: request.Response
        """
        return self.request(function='getProjects', detail=2)

    def get_resources(self, project_id: Union[str, int]) -> requests.Response:
        """
        Requests the ids of all the resource for a specific project.

        :param project_id: the id of the project
        :type project_id: Union[str, int]
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getResources', detail=13, tree='false')

    def get_resource_ids(self, project_id: Union[str, int]) -> requests.Response:
        """
        Requests the ids of all the resource for a specific project.

        :param project_id: the id of the project
        :type project_id: Union[str, int]
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getResources', detail=2)

    def get_classrooms(self, project_id: Union[str, int]) -> requests.Response:
        """
        Requests all the classrooms for a specific project.

        :param project_id: the id of the project
        :type project_id: Union[str, int]
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getResources',
                            detail=13, tree='false', category='classroom')

    def get_activities(self, resource_ids: List[Union[str, int]], project_id: Union[str, int]) -> requests.Response:
        """
        Requests all activities (set of events)  for a specific project.

        :param resource_ids: the ids of all the resources the activities are requested
        :type resource_ids: List[Union[str, int]
        :param project_id: the id of the project
        :type project_id: Union[str, int]
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getActivities',
                            tree='false', detail=17, resources='|'.join(map(str, resource_ids)))


def get_token(credentials: ClientCredentials) -> Tuple[str, int]:
    """
    Requests a new token to the API.

    :param credentials: all information needed to make requests to API
    :param credentials: ClientCredentials
    :return: the token and its time to expiration in seconds
    :rtype: Tuple[str, int]
    """
    url = credentials['url']
    data = credentials['data']
    authorization = credentials['Authorization']
    header = {'Authorization': authorization}
    r = requests.post(url=url, headers=header, data=data).json()
    return r['access_token'], int(r['expires_in'])


def response_to_root(response: requests.Response) -> etree.ElementTree:
    """
    Parses an API response into a tree structure.

    :param response: a response from the API
    :type response: requests.Response
    :return: the tree structure
    :rtype: etree.ElementTree
    """
    return etree.fromstring(response.content)


def response_to_project_ids(project_ids_response: requests.Response) -> Iterator[Tuple[int, str]]:
    """
    Extracts an API response into an iterator of project ids and years.

    :param project_ids_response: a response from the API to the project_ids request
    :type project_ids_response: requests.Response
    :return: all the project ids and years
    :rtype: Iterator[Tuple[int, str]]

    :Example:

    >>> response = client.get_project_ids()
    >>> ids_years = response_to_project_ids(response)
    """
    root = response_to_root(project_ids_response)
    ids = root.xpath('//project/@id')
    years = root.xpath('//project/@name')

    return zip(map(int, ids), years)


def response_to_resources(resources_response) -> Dict[str, Resource]:
    """
    Extracts an API response into an dictionary mapping a resource name to its ids.

    :param resources_response: a response from the API to the resources request
    :type resources_response: requests.Response
    :return: all the resources
    :rtype: Dict[str, Resources]

    :Example:

    >>> response = client.get_resource_ids(9)  # project id for 2019-2020
    >>> resources_ids = response_to_resource_ids(response)
    """
    root = response_to_root(resources_response)

    return {resource.attrib['id']: Resource(**resource.attrib) for resource in root.xpath('//resource')}


def response_to_resource_ids(resource_ids_response) -> Dict[str, str]:
    """
    Extracts an API response into an dictionary mapping a resource name to its ids.

    :param resource_ids_response: a response from the API to the resources or resource_ids request
    :type resource_ids_response: requests.Response
    :return: all the resources names and their ids
    :rtype: Dict[str, str]

    :Example:

    >>> response = client.get_resource_ids(9)  # project id for 2019-2020
    >>> resources_ids = response_to_resource_ids(response)
    """
    root = response_to_root(resource_ids_response)
    df = pd.DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(),
                                                                   root.xpath('//resource/@name'))
                      , columns=['id'])
    return df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()


def room_to_classroom(room: etree.ElementTree) -> Classroom:
    """
    Parses the (class)room retrieved from API to a more convenient Classroom object.

    :param room: (class)room as a tree structure
    :type room: etree.ElementTree
    :return: the classroom
    :rtype: Classroom
    """
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


def response_to_classrooms(classrooms_response: requests.Response) -> List[Classroom]:
    """
    Extracts an API response into list of classrooms.

    :param classrooms_response: a response from the API to the classrooms request
    :type classrooms_response: requests.Response
    :return: all classrooms
    :rtype: List[Classroom]

    :Example:

    >>> response = client.get_classrooms(9)  # project id for 2019-2020
    >>> classrooms = response_to_classrooms(response)
    """
    root = response_to_root(classrooms_response)

    rooms = root.xpath('//room')

    classrooms = []
    for room in rooms:
        classroom = room_to_classroom(room)
        classrooms.append(classroom)

    return classrooms


def response_to_courses(activities_response: requests.Response) -> List[Course]:
    """
    Extracts an API response into list of courses.

    :param activities_response: a response from the API to the activities request
    :type activities_response: requests.Response
    :return: all courses present in the response
    :rtype: List[Courses]

    :Example:

    >>> response = client.get_activities(9)  # project id for 2019-2020
    >>> courses = response_to_courses(response)
    """
    root = response_to_root(activities_response)

    courses = defaultdict(Course)

    # Each activity has its unique event type
    for activity in root.xpath('//activity'):
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

            event_classroom = classrooms
            event_address = 'JEROM FIX UR SHIT' #backend.classrooms.merge_classrooms(classrooms)
                # TODO: This sucks @Jerome

            xy = event.xpath('.//eventParticipant[@category="instructor"]')
            instructor_names = event.xpath('.//eventParticipant[@category="instructor"]/@name')
            instructor_emails = event.xpath('.//eventParticipant[@category="instructor"]/@id')  # TODO: email ?
            event_instructor = professors.merge_professors(professors.Professor(name, email)
                                                           for name, email in zip(instructor_names, instructor_emails))

            # We create the event
            t0, t1 = backend.events.extract_datetime(event_date, event_start, event_end)
            event = event_type(name=activity_name, begin=t0, end=t1, professor=event_instructor,
                                classrooms=event_address, id=activity_id, code=activity_code)
            events_list.append(event)

        if activity_code not in courses and events_list:
            courses[activity_code] = Course(activity_code, activity_name)
        if events_list:
            courses[activity_code].add_activity(events_list)

    return list(courses.values())


if __name__ == "__main__":

    import backend.credentials as credentials

    filename = "/home/jerome/ade_api.json"

    credentials.set_credentials(filename, credentials.ADE_API_CREDENTIALS)

    credentials = credentials.get_credentials(credentials.ADE_API_CREDENTIALS)

    client = Client(credentials)

    request = client.get_project_ids()

    ids_years = response_to_project_ids(request)

    # On peut l'obtenir de ids_years
    project_id = 9

    request = client.get_resource_ids(project_id)

    resources_ids = response_to_resource_ids(request)

    print('All resources:')
    print(len(resources_ids), resources_ids)

    id = resources_ids['LMECA2732']

    # 'LBRAI2206': '12438'

    request = client.get_activities([id], project_id)

    courses = response_to_courses(request)

    print(courses)

    response = client.request(projectId=project_id, function='getResources',
                 detail=13, tree='false')

    root = response_to_root(response)

    ids = [resources_ids['LMECA2732'], resources_ids['FSA11BA'], resources_ids['LEPL1108'], resources_ids['FSA12BA']]

    res = root.xpath('|'.join(f'//resource[@id={id}' for id in ids))

    for r in res:
        etree.tostring(r)


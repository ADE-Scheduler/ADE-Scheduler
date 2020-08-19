import requests
import time
import pickle
import json
from lxml import etree
import pandas as pd
from collections import defaultdict, Counter
from backend.classrooms import Classroom, Address
from backend.courses import Course
from backend import professors
import backend.events
from typing import Dict, Union, List, Tuple, SupportsInt, Callable, Type

AUTO_RENEW_TOKEN = True


class ExpiredTokenError(Exception):
    """
    Exception that will occur if a token is expired.
    """

    def __str__(self):
        return 'The token you were using is now expired! Renew the token to proceed normally.'


ClientCredentials = Dict[str, Union[str, List[int]]]
Request = Union[str, int]


class DummyClient:
    """
    A dummy client is an abstrat class providing just the specific requests, but not the access to the API.
    Access to  the API is to be implemented.

    :param credentials: all information needed to make requests to API
    :param credentials: ClientCredentials

    :Example:

    >>> import backend.credentials as credentials
    >>> credentials = credentials.get_credentials(credentials.ADE_API_CREDENTIALS)
    >>> client = Client(credentials)
    """

    def __init__(self, credentials: ClientCredentials):
        raise NotImplementedError

    def is_expired(self) -> bool:
        """
        Returns whether the current token is expired.

        :return: True if the token is expired
        :rtype: bool
        """
        raise NotImplementedError

    def expire_in(self) -> float:
        """
        Returns the time remaining before the token expires.

        :return: the time remaining in seconds, 0 if expired
        :rtype: float
        """
        raise NotImplementedError

    def renew_token(self) -> None:
        """
        Renews the current token requesting a new one.
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def get_project_ids(self) -> requests.Response:
        """
        Requests the project ids currently available; each year (project) corresponds to an id.

        :return: the response
        :rtype: request.Response
        """
        return self.request(function='getProjects', detail=2)

    def get_resources(self, project_id: SupportsInt) -> requests.Response:
        """
        Requests the ids of all the resource for a specific project.

        :param project_id: the id of the project
        :type project_id: SupportsInt
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getResources', detail=13, tree='false')

    def get_resource_ids(self, project_id: SupportsInt) -> requests.Response:
        """
        Requests the ids of all the resource for a specific project.

        :param project_id: the id of the project
        :type project_id: SupportsInt
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getResources', detail=2)

    def get_classrooms(self, project_id: SupportsInt) -> requests.Response:
        """
        Requests all the classrooms for a specific project.

        :param project_id: the id of the project
        :type project_id: SupportsInt
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getResources',
                            detail=13, tree='false', category='classroom')

    def get_activities(self, resource_ids: List[SupportsInt], project_id: SupportsInt) -> requests.Response:
        """
        Requests all activities (set of events)  for a specific project.

        :param resource_ids: the ids of all the resources the activities are requested
        :type resource_ids: List[SupportsInt]
        :param project_id: the id of the project
        :type project_id: SupportsInt
        :return: the response
        :rtype: request.Response
        """
        return self.request(projectId=project_id, function='getActivities',
                            tree='false', detail=17, resources='|'.join(map(str, resource_ids)))


class Client(DummyClient):
    """
    A client subclasses the DummyClient abstract class and implements access to ADE API using correct credentials.
    If you do not own such credentials, please use :func:`FakeClient`.
    """

    def __init__(self, credentials: ClientCredentials):
        self.credentials = credentials
        self.token = None
        self.expiration = None
        self.renew_token()

    def is_expired(self) -> bool:
        return self.expiration < time.time()

    def expire_in(self) -> float:
        return max(self.expiration - time.time(), 0)

    def renew_token(self) -> None:
        self.token, self.expiration = get_token(self.credentials)
        self.expiration += time.time()

    def request(self, **kwargs: Request) -> requests.Response:

        if self.is_expired():
            if AUTO_RENEW_TOKEN:
                self.renew_token()
            else:
                raise ExpiredTokenError

        headers = {'Authorization': 'Bearer ' + self.token}
        user = self.credentials['user']
        password = self.credentials['password']
        args = '&'.join('='.join(map(str, _)) for _ in kwargs.items())

        url = 'https://api.sgsi.ucl.ac.be:8243/ade/v0/api?login=' + user + '&password=' + password + '&' + args

        resp = requests.get(url=url, headers=headers)
        resp.raise_for_status()

        # save_response(resp, args)

        return resp


def load_responses() -> Dict[str, List[int]]:
    """
    Loads the responses stored in the json file
    :return: the dictionary of all the responses
    :rtype: Dict[str, List[int]]
    """
    with open(FakeClient.FILENAME, 'r') as f:
        return json.load(f)


def load_response(request_name: str) -> requests.Response:
    """
    Loads the response of a given request.

    :param request_name: the parameters used in the request, concatenated as in :func:`FakeClient.request`
    :type request_name: str
    :return: the response
    :rtype: requests.Response
    :raises HTTPError: if the response to the request could not be found in the file
    """
    try:
        return pickle.loads(bytes(load_responses()[request_name]))
    except KeyError:
        raise requests.exceptions.HTTPError(f'key [{request_name}] for request was not found')


def save_response(response: requests.Response, request_name: str):
    """
    Saves the response to a request into the file specified by the FakeClient class.

    :param response: the response to the request
    :type response: requests.Response
    :param request_name: the parameters used in the request, concatenated as in :func:`FakeClient.request`
    :type request_name: str
    """
    responses = load_responses()
    responses[request_name] = list(pickle.dumps(response))

    with open(FakeClient.FILENAME, 'w') as f:
        json.dump(responses, f)


class FakeClient(DummyClient):
    """
    A fake client subclasses the DummyClient abstract class and implements a fake access to ADE API.
    All the API responses you can cannot are stored in json file, which you can change if you want to.
    """
    FILENAME = 'fake_api.json'

    def __init__(self, credentials: ClientCredentials):
        self.credentials = credentials
        self.delay = 150  # Delay in seconds
        self.expiration = 0
        self.renew_token()

    def is_expired(self) -> bool:
        return self.expiration < time.time()

    def expire_in(self) -> float:
        return max(self.expiration - time.time(), 0)

    def renew_token(self) -> None:
        self.expiration = time.time() + self.delay

    def request(self, **kwargs: Request) -> requests.Response:
        if self.is_expired():
            raise ExpiredTokenError

        args = '&'.join('='.join(map(str, _)) for _ in kwargs.items())

        return load_response(args)


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


def response_to_project_ids(project_ids_response: requests.Response) -> Dict[str, int]:
    """
    Extracts an API response into an iterator of project ids and years.

    :param project_ids_response: a response from the API to the project_ids request
    :type project_ids_response: requests.Response
    :return: all the project ids and years (year as key, id as value)
    :rtype: Dict[str, int]

    :Example:

    >>> response = client.get_project_ids()
    >>> ids_years = response_to_project_ids(response)
    """
    root = response_to_root(project_ids_response)
    ids = root.xpath('//project/@id')
    years = root.xpath('//project/@name')

    return {year: int(id) for id, year in zip(ids, years)}


def response_to_resources(resources_response) -> pd.DataFrame:
    """
    Extracts an API response into an dataframe mapping a resource name to its ids.

    :param resources_response: a response from the API to the resources request
    :type resources_response: requests.Response
    :return: all the resources
    :rtype: pd.Dataframe

    :Example:

    >>> response = client.get_resources(9)  # project id for 2019-2020
    >>> resources = response_to_resources(response)
    """
    root = response_to_root(resources_response)

    resources = root.xpath('//resource/.')

    index = resources[0].attrib.keys()

    values = [resource.attrib.values() for resource in resources]

    df = pd.DataFrame(data=values, columns=index, dtype=str)

    df.set_index('id', inplace=True)

    return df


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

    d = df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()

    return d


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


def parse_event(event: etree.ElementTree, event_type: Type[backend.events.AcademicalEvent],
                activity_name: str, activity_id: str, activity_code: str) -> backend.events.AcademicalEvent:
    """
    Parses an element from a request into an academical event.
    An event is from an activity so information about this activity must be provided.

    :param event: the event element
    :type event: etree.ElementTree
    :param event_type: the constructor used to initiate to event object
    :type event_type: Type[backend.events.AcademicalEvent]
    :param activity_name: the name of the activity
    :type activity_name: str
    :param activity_id: the id of the activity
    :type activity_id: str
    :param activity_code: the code of the activity
    :type activity_code: str
    :return: the academical event
    :rtype: backend.events.AcademicalEvent
    """
    event_date = event.attrib['date']
    event_start = event.attrib['startHour']
    event_end = event.attrib['endHour']
    rooms = event.xpath('.//eventParticipant[@category="classroom"]')
    classrooms = [room_to_classroom(room) for room in rooms]

    instructors = list()
    for instructor in event.xpath('.//eventParticipant[@category="instructor"]'):
        instructors.append(
            professors.Professor(instructor.attrib['name'], None)
        )


    event_instructor = professors.merge_professors(instructors)

    # We create the event
    t0, t1 = backend.events.extract_datetime(event_date, event_start, event_end)
    return event_type(name=activity_name, begin=t0, end=t1, professor=event_instructor,
                      classrooms=classrooms, id=activity_id, code=activity_code)


def parse_activity(activity: etree.ElementTree) -> Tuple[List[backend.events.AcademicalEvent], str, str, str]:
    """
    Parses an element from a request into a list of events and some activity information.

    :param activity: the activity element
    :type activity: etree.ElementTree
    :return: the events, the name, the id and the code of this activity
    :rtype: Tuple[List[backend.events.AcademicalEvent], str, str, str]
    """
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
        events_list.append(
            parse_event(event, event_type, activity_name, activity_id, activity_code)
        )

    return events_list, activity_name, activity_id, activity_code


def response_to_courses(activities_response: requests.Response) -> List[Course]:
    """
    Extracts an API response into list of courses.

    :param activities_response: a response from the API to the activities request
    :type activities_response: requests.Response
    :return: all courses present in the response
    :rtype: List[Courses]

    :Example:

    >>> response = client.get_activities(['1234'], 9)  # project id for 2019-2020
    >>> courses = response_to_courses(response)
    """
    root = response_to_root(activities_response)

    courses = defaultdict(Course)

    # Each activity has its unique event type
    for activity in root.xpath('//activity'):

        events_list, activity_name, activity_id, activity_code = parse_activity(activity)

        if activity_code not in courses and events_list:
            courses[activity_code] = Course(activity_code, activity_name)
        if events_list:
            courses[activity_code].add_activity(events_list)

    return list(courses.values())


def response_to_events(activities_response: requests.Response,
                       filter_func: Callable[[backend.events.AcademicalEvent], bool])\
        -> List[backend.events.AcademicalEvent]:
    """
    Extracts an API response into list of events.

    :param activities_response: a response from the API to the activities request
    :type activities_response: requests.Response
    :param filter_func: a function to filter out events
    :type filter_func: Callable[[backend.events.AcademicalEvent], bool]
    :return: all events present in the response, optionnally filtered
    :rtype: List[backend.events.AcademicalEvents]

    :Example:

    >>> response = client.get_activities(['1234'], 9)  # project id for 2019-2020
    >>> events = response_to_events(response)
    """
    root = response_to_root(activities_response)

    events = list()

    # Each activity has its unique event type
    for activity in root.xpath('//activity'):

        events_list, activity_name, activity_id, activity_code = parse_activity(activity)

        events.extend(
            filter(filter_func,
                   events_list)
        )

    return events


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

    id = resources_ids['LMECA2732']

    # 'LBRAI2206': '12438'

    request = client.get_activities([id], project_id)

    courses = response_to_courses(request)

    client.get_classrooms(project_id)

    response = client.get_resources(9)

    resources = response_to_resources(response)

    import random

    for key, val in resources.items():

        n = random.randint(1, 50)

        print('doing some requests')

        ids = []
        while len(ids) < n:
            ids.append(ids)

        client.get_activities(ids, project_id)

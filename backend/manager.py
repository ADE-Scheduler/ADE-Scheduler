from multiprocessing import Process
import pandas as pd
import time
import json
from typing import SupportsInt, List, Iterator, Optional, Union, Dict

import backend.servers as srv
import backend.ade_api as ade
import backend.models  as md
import backend.courses as crs
import backend.schedules as schd
import backend.resources as rsrc
import backend.classrooms as clrm


class ScheduleNotOwnedError(Exception):
    """
    Exception that will occur if a user tries to manipulate a schedule he does not own.
    """
    def __str__(self):
        return 'The schedule you manipulated is not yours.'


class Manager:
    """
    The manager ensures that data is accessible and provides access to it.

    Data can either be found in the server, in the database or obtained from the ADE API.
    At initialization, each source is checked to ensure that they are working properly.

    :param client: the client providing access to ADE API
    :type client: ade_api.Client
    :param server: the server providing temporary memory
    :type server: server.Server
    :param database: the database
    :type database: md.SQLAlchemy
    """

    def __init__(self, client: ade.Client, server: srv.Server, database: md.SQLAlchemy):

        def run_server():
            while not server.is_running():
                server.run()
                time.sleep(1)

        def get_api_token():
            while client.is_expired():
                client.renew_token()
                time.sleep(1)

        # TODO: provide a way to check that the database (db) is operational

        p1 = Process(target=run_server)
        p1.start()
        p1.join(5)  # Timeout after trying to connect during 5s

        p2 = Process(target=get_api_token())
        p2.start()
        p2.join(5)  # Timeout after trying to connect during 5s

        if p1.is_alive() or p2.is_alive():
            raise Exception('Could not initialize the API client and/or the server connection.')
        else:
            self.server = server
            self.client = client
            self.database = database

    def get_courses(self, *codes: str, project_id: SupportsInt = None) -> List[crs.Course]:
        """
        Returns the courses with given codes as a list.

        :param codes: the code(s) of the course(s)
        :type codes: str
        :param project_id: the project id
        :type project_id: SupportsInt
        :return: the list of courses
        :rtype: List[crs.Course]
        """
        if project_id is None:
            project_id = self.get_default_project_id()

        # Fetch from the server
        prefix = f'[project_id={project_id}]'
        courses, codes_not_found = self.server.get_multiple_values(*codes, prefix=prefix)

        # Fetch from the api
        if codes_not_found:

            if self.client.is_expired():
                self.client.renew_token()

            resource_ids = self.get_resource_ids(*codes_not_found, project_id=project_id)
            courses_not_found = ade.response_to_courses(self.client.get_activities(resource_ids, project_id))
            for course in courses_not_found:
                self.server.set_value(prefix+course.code, course, expire_in={'hours': 3})
            courses += courses_not_found

        return courses

    def get_resources(self, project_id: SupportsInt = None) -> pd.DataFrame:
        """
        Returns the resources.

        :param project_id: the project id
        :type project_id: SupportsInt
        :return: the resources
        :rtype: pd.DataFrame
        """
        if project_id is None:
            project_id = self.get_default_project_id()

        key = f'[RESOURCES,project_id={project_id}]'

        if not self.server.exists(key):
            self.update_resources()

        return self.server.get_value(key)

    def update_resources(self):
        """
        Updates the resources contained in the server for all project ids.
        """
        key = f'[PROJECT_IDs]'
        if not self.server.exists(key):
            self.update_project_ids()

        for value in self.server.hgetall(key).values():
            value = value.decode()
            key = f'[RESOURCES,project_id={value}]'

            resources = ade.response_to_resources(self.client.get_resources(value))
            self.server.set_value(key, resources, expire_in={'hours': 25})

    def get_classrooms(self, project_id: SupportsInt = None,
                       search_dict: Dict[str, str] = None, return_json: bool = False):
        if project_id is None:
            project_id = self.get_default_project_id()

        key = f'[CLASSROOMS,project_id={project_id}]'

        if not self.server.exists(key):
            self.update_classrooms()

        classrooms = self.server.get_value(key)

        if search_dict is not None:
            for index, search in search_dict.items():
                contains = classrooms[index].str.contains(search)
                classrooms = classrooms[contains]

        if return_json:
            return list(classrooms.to_dict(orient='index').values())
        else:
            return classrooms

    def update_classrooms(self, drop_empty: List[str] = [rsrc.INDEX.ADDRESS]):
        """
        Updates the classrooms contained in the server for all project ids.
        """
        key = f'[PROJECT_IDs]'
        if not self.server.exists(key):
            self.update_project_ids()

        for value in self.server.hgetall(key).values():
            value = value.decode()
            key = f'[CLASSROOMS,project_id={value}]'

            resources = self.get_resources(project_id=value)

            classrooms_index = resources[rsrc.INDEX.TYPE] == rsrc.TYPES.CLASSROOM
            classrooms = resources[classrooms_index]

            for drop_index in drop_empty:
                not_empty = classrooms[drop_index] != ''
                classrooms = classrooms[not_empty]

            classrooms = clrm.prettify_classrooms(classrooms)

            self.server.set_value(key, classrooms, expire_in={'hours': 25})

    def get_resource_ids(self, *codes: str, project_id: SupportsInt = None) -> Iterator[str]:
        """
        Returns the resource ids of each code.

        :param codes: the code(s) (name(s)) of the resources
        :type codes: str
        :param project_id: the project id
        :type project_id: SupportsInt
        :return: the resource ids
        :rtype: Iterator[str]
        """
        if project_id is None:
            project_id = self.get_default_project_id()

        key = f'[RESOURCE_IDs,project_id={project_id}]'
        if not self.server.exists(key):
            self.update_resource_ids()
        return map(lambda x: x.decode(), filter(None, self.server.hmget(key, codes)))

    def update_resource_ids(self):
        """
        Updates the resource ids contained in the server for all project ids.
        """
        key = f'[PROJECT_IDs]'
        if not self.server.exists(key):
            self.update_project_ids()

        for value in self.server.hgetall(key).values():
            value = value.decode()
            key = f'[RESOURCE_IDs,project_id={value}]'
            resource_ids = ade.response_to_resource_ids(self.client.get_resource_ids(value))
            self.server.set_value(key, resource_ids, expire_in={'hours': 25}, hmap=True)

    def get_project_ids(self, year: Optional[str] = None) -> Union[List[Dict[str, str]], str, None]:
        """
        Returns the project ids. If year is specified, only the project id of this year is returned.

        :param year: the year, '2019-2020' format
        :type year: str
        :return: the list of ids and years or the id of one year or None if no id was found
        :rtype: Union[List[Dict[str, str]], str, None]
        """
        hmap = f'[PROJECT_IDs]'
        if not self.server.exists(hmap):
            self.update_project_ids()
        if year is None:
            return [{'id': value.decode(), 'year': key.decode()}
                    for key, value in self.server.hgetall(hmap).items()]
        value = self.server.get_value(year, hmap=hmap)
        if value:
            return value.decode()
        else:
            value = self.server.hmget(hmap, year)
            if value:
                return value.decode()
            else:
                return None

    def update_project_ids(self):
        """
        Updates the project ids.
        """
        key = f'[PROJECT_IDs]'
        project_ids = ade.response_to_project_ids(self.client.get_project_ids())
        self.server.set_value(key, project_ids, expire_in={'hours': 25}, hmap=True)

    def get_default_project_id(self):
        """
        Returns the default project id.

        :return: the default project id
        :rtype: str
        """
        return self.get_project_ids()[-1]['id']

    def save_schedule(self, user: md.User, schedule: schd.Schedule):
        """
        Saves a schedule binding it to a user into the database.

        :param user: the user
        :type user: md.User
        :param schedule: the schedule
        :type schedule: schd.Schedule
        :return: the scheduler, with its id updated...

        """
        if schedule.id is None:     # this schedule is not yet saved
            schd_db = md.Schedule(data=schedule, user=user)
            schd_db.data.id = schd_db.id
            self.database.session.commit()
            return schd_db.data

        else:                       # this schedule has already been saved
                                    # TODO: control access levels
            schd_db = user.get_schedule(id=schedule.id)
            if schd_db is None:
                raise ScheduleNotOwnedError
            else:
                schd_db.update_data(schedule)
                return schd_db.data

    def get_schedule(self, link):
        query = md.Link.query.filter(md.Link.link == link).first()
        if query:
            return query.schedule.data, query.choice
        else:
            return None, None

    def get_link(self, schedule_id):
        query = md.Schedule.query.filter(md.Schedule.id == schedule_id).first()
        if query:
            return query.link.link
        else:
            return None

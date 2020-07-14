from multiprocessing import Process
from datetime import timedelta
import time

import backend.servers as srv
import backend.ade_api as ade
import backend.models  as md


class ScheduleNotOwnedError(Exception):
    """
    Exception that will occur if a user tries to manipulate a schedule he does not own.
    """
    def __str__(self):
        return 'The schedule you manipulated is not yours.'


class Manager:
    """
    The manager ensures that data is accessible and provides access to it.

    Data can either be found in the server, in the database or from the ADE API.
    At initialization, each source is checked to ensure that they are working properly.

    :param client: the client providing access to ADE API
    :type client: ade_api.Client
    :param server: the server providing temporary memory
    :type server: server.Server
    :param db: the database TODO
    :type db: TODO
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

    def get_courses(self, *codes, project_id=ade.DEFAULT_PROJECT_ID):
        """
        ...
        """
        # Fetch from the server
        prefix = f'[project_id={project_id}]'
        courses, codes_not_found = self.server.get_multiple_values(*codes, prefix=prefix)

        # Fetch from the api
        if codes_not_found:
            resource_ids = self.get_resource_id(*codes_not_found, project_id=project_id)
            courses_not_found = ade.response_to_courses(self.client.get_activities(resource_ids, project_id))
            for course in courses_not_found:
                self.server.set_value(prefix+course.code, course, expire_in={'hours': 3})
            courses += courses_not_found

        return courses

    def get_resource_id(self, *codes, project_id=ade.DEFAULT_PROJECT_ID):
        """
        ...
        """
        hmap = f'[RESOURCE_IDs,project_id={project_id}]'
        if not self.server.exists(hmap):
            self.update_resource_id()
        return map(lambda x: x.decode(), filter(None, self.server.hmget(hmap, codes)))

    def update_resource_id(self):
        """
        ...
        """
        hmap = f'[PROJECT_IDs]'
        if not self.server.exists(hmap):
            self.update_project_id()

        for value in self.server.hgetall(hmap).values():
            value = value.decode()
            hmap = f'[RESOURCE_IDs,project_id={value}]'
            resources = ade.response_to_resource_ids(self.client.get_resource_ids(value))
            self.server.hmset(hmap, resources)
            self.server.expire(hmap, timedelta(hours=25))

    def get_project_id(self, year):
        """
        ...
        """
        hmap = f'[PROJECT_IDs]'
        if not self.server.exists(hmap):
            self.update_project_id()
        value = self.server.hmget(hmap, year)
        if value:
            return value.decode()
        else:
            return None

    def update_project_id(self):
        """
        ...
        """
        hmap = f'[PROJECT_IDs]'
        project_ids = ade.response_to_project_ids(self.client.get_project_ids())
        self.server.hmset(hmap, dict((v, k) for k, v in project_ids))
        self.server.expire(hmap, timedelta(hours=25))

    def save_schedule(self, user, schedule):
        """
        ...
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

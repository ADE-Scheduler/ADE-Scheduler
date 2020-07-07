from multiprocessing import Process
import time

import backend.servers as srv
import backend.ade_api as ade

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
    def __init__(self, client: ade.Client, server: srv.Server):

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

    def get_courses(self, *codes, project_id=ade.DEFAULT_PROJECT_ID):
        # Fetch from the server
        prefix = f'[project_id={project_id}]'
        courses, codes_not_found = self.server.get_multiple_values(*codes, prefix=prefix)

        # Fetch from the api
        resource_ids = self.get_resource_ids(*codes_not_found, project_id=project_id)
        courses_not_found = ade.response_to_courses(self.client.get_activities(resource_ids, project_id))
        for course in courses_not_found:
            self.server.set_value(prefix+course.code, course, expire_in={'hours': 10})

        courses += courses_not_found
        return courses

    def get_resource_ids(self, *codes, project_id=ade.DEFAULT_PROJECT_ID):
        resources = ade.response_to_resource_ids(self.client.get_resource_ids(ade.DEFAULT_PROJECT_ID))
        return [resources.get(code) for code in codes]

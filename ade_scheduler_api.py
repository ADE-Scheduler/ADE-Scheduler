from backend import ade_api, servers
from multiprocessing import Process
import time


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
    def __init__(self, client: ade_api.Client, server: servers.Server, db):

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

        def get_courses(*codes, project_id=ade_api.DEFAULT_PROJECT_ID):
            prefix = f'[project_id={project_id}]'
            courses, codes_not_found = self.server.get_multiple_values(*codes,  prefix=prefix)

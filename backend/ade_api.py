import requests
import time
from lxml import etree
import pandas as pd


class ExpiredTokenError(Exception):

    def __str__(self):
        return 'The token you were using is not expired! Renew the token to proceed normally.'


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
        self.token, self.expiration = Client.get_token(self.credentials)
        self.expiration += time.time()

    @staticmethod
    def get_token(credentials):
        url = credentials['url']
        data = credentials['data']
        authorization = credentials['Authorization']
        header = {'Authorization': authorization}
        r = requests.post(url=url, headers=header, data=data).json()
        return r['access_token'], int(r['expires_in'])

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

    def get_courses(self, resource_ids, project_id):
        return self.request(projectId=project_id, function='getActivities',
                            tree='false', detail=17, resources='|'.join(resource_ids))


class DataParser:

    @staticmethod
    def request_to_string(request):
        return etree.fromstring(request.content)

    @staticmethod
    def request_to_project_ids(request):
        root = DataParser.request_to_string(request)
        ids = root.xpath('//project/@id')
        years = root.xpath('//project/@name')

        return zip(map(int, ids), years)

    @staticmethod
    def request_to_resource_ids(request):
        root = DataParser.request_to_string(request)
        df = pd.DataFrame(data=root.xpath('//resource/@id'), index=map(lambda x: x.upper(),
                                                                       root.xpath('//resource/@name'))
                          , columns=['id'])
        return df.groupby(level=0).apply(lambda x: '|'.join(x.to_dict(orient='list')['id'])).to_dict()


if __name__ == "__main__":

    from backend.credentials import Credentials

    filename = "/home/jerome/ade_api.json"

    Credentials.set_credentials(filename, Credentials.ADE_API_CREDENTIALS)

    credentials = Credentials.get_credentials(Credentials.ADE_API_CREDENTIALS)

    client = Client(credentials)

    request = client.get_project_id()

    ids_years = DataParser.request_to_project_ids(request)

    # On peut l'obtenir de ids_years
    project_id = 9

    request = client.get_resource_ids(project_id)
    
    resources_ids = DataParser.request_to_resource_ids(request)
    print(resources_ids)

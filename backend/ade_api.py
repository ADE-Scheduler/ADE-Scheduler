import requests
import time


class Client:

    def __init__(self, token, expiration):
        self.token = token
        self.expiration = expiration

    def is_expired(self):
        # TODO: verify validity of this relation
        return self.expiration > time.time()

    def renew_token(self, credentials):
        self.token, self.expiration = Client.get_token(credentials)

    @staticmethod
    def get_token(credentials):
        url = credentials['url']
        data = credentials['data']
        authorization = credentials['Authorization']
        header = {'Authorization': authorization}
        r = requests.post(url=url, headers=header, data=data).json()
        return r['access_token'], int(r['expires_in'])


if __name__ == "__main__":

    from backend.credentials import Credentials

    credentials = Credentials.get_credentials(Credentials.ADE_API_CREDENTIALS)

    token, _ = Client.get_token(credentials)

    print(token)

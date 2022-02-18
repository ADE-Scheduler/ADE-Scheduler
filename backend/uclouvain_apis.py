import os

import requests


class API(object):
    BASE_URL = "https://gw.api.uclouvain.be"
    ENDPOINT = ""

    # Combined @classmethod and @property requires Python >= 3.9
    @classmethod
    @property
    def url(cls):
        return os.path.join(cls.BASE_URL, cls.ENDPOINT)

    @classmethod
    def get(cls, url, **kwargs):
        url = os.path.join(cls.url, url)
        return requests.get(url=url, **kwargs)

    @classmethod
    @property
    def token(cls):
        return os.path.join(cls.url, "token")

    TOKEN_URL = token

    @classmethod
    @property
    def authorize(cls):
        return os.path.join(cls.url, "authorize")

    AUTHORIZE_URL = authorize


class ADE(API):
    ENDPOINT = "ade/v0"


class My(API):
    ENDPOINT = "my/v0"


class MyADE(API):
    ENDPOINT = "myADE/v1"

import requests


class API(object):
    BASE_URL = "https://gw.api.uclouvain.be"
    ENDPOINT = ""
    
    @classmethod
    def url(cls):
        return f"{cls.BASE_URL}/{cls.ENDPOINT}"

    @classmethod
    def get(url, **kwargs):
        return requests.get(url=f"{cls.url()}/{url}", **kwargs)


class ADE(API):
    ENDPOINT = "ade/v0"

class My(API):
    ENDPOINT = "my/v0"

class MyADE(API):
    ENDPOINT = "myADE/v1"

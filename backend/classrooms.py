from typing import Iterable, Union
import pandas as pd
import backend.resources as rsrc
from geopy.geocoders import Nominatim
import time


class Address:
    """
    Address object made from informations retrieved via ADE API.

    :param kwargs: dict with minimal entries (can be None):
        - address1
        - address2
        - zipCode
        - city
        - country
    :type kwargs: str

    :Example:

    >>> informations = dict(address1='Rue Rose 42', address2=None, zipCode='1300', city='Wavre', country='Belgique')
    >>> address = Address(**informations)
    """

    def __init__(self, **kwargs: str):
        self.address = kwargs

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        location = '\n'.join(filter(None,
                                    [
                                        self.address[rsrc.INDEX.ADDRESS],
                                        self.address[rsrc.INDEX.ZIP_CODE],
                                        self.address[rsrc.INDEX.CITY],
                                        self.address[rsrc.INDEX.COUNTRY]
                                    ]))

        return location


def prettify_classrooms(classrooms: pd.DataFrame, sleep: float = 0) -> pd.DataFrame:
    """
    Returns the classrooms dataframe in a pretty format, useful when need to display.

    The function will request, for every different address, a geo-localisation, so it can take some times.
    If too many requests are done, Nominatim will not like so prefer to put a time.sleep between each request.

    :param classrooms: the classrooms with fields defined in backend.resources.py
    """

    geolocator = Nominatim(user_agent='ADE_SCHEDULER')
    geo_locations = dict()

    def __pretty__(classroom: pd.Series):
        address = Address(**classroom.to_dict())
        location = str(address).replace('\n', ', ')
        name = classroom[rsrc.INDEX.NAME]
        code = classroom[rsrc.INDEX.CODE]

        response = geolocator.geocode(location, exactly_one=True)
        if response is not None:
            latitude = response.latitude
            longitude = response.longitude
        else:
            latitude = None
            longitude = None

        return pd.Series([name, code, location, latitude, longitude],
                         index=['name', 'code', 'address', 'latitude', 'longitude'])

    def __geoloc__(classroom: pd.Series):
        name = classroom['name']
        code = classroom['code']
        address = classroom['address']

        latitude, longitude = geo_locations[address]

        return pd.Series([name, code, address, latitude, longitude],
                         index=['name', 'code', 'address', 'latitude', 'longitude'])

    classrooms = classrooms.apply(__pretty__, axis=1, result_type='expand')

    for address in classrooms['address'].unique():
        response = geolocator.geocode(address, exactly_one=True)

        if response is not None:
            latitude = response.latitude
            longitude = response.longitude
        else:
            latitude = None
            longitude = None

        time.sleep(sleep)
        geo_locations[address] = (latitude, longitude)

    return classrooms.apply(__geoloc__, axis=1, result_type='expand')


# TODO: fix the fact that activities in Course class cannot be output in a shell (replace('\\', '\\\\') is not defined)
class Classroom:
    """
    Classroom object containing the address (as string or Address object), the name of the classroom and its id.

    :param kwargs: dict with minimal entries:
        - address
        - name
        - id
    :type kwargs: Union[str, Address]

    Its main purpose is be used with :func:`location`.
    """
    def __init__(self, **kwargs: Union[str, Address]):
        self.infos = kwargs

    def __str__(self) -> str:
        return str(self.infos['name']) + '\n' + str(self.infos['address'])

    def __hash__(self):
        return hash(self.infos)

    def __eq__(self, other):
        return self.infos == other.infos

    def __repr__(self) -> str:
        id = self.infos['id']
        name = self.infos['name']
        return f'{id}: {name}'

    def location(self) -> str:
        """
        Returns the location (address) of this classroom.

        :return: the location
        :rtype: str
        """
        return '\n'.join(filter(None, str(self).split('\n')))  # Removes blank lines


def merge_classrooms(classrooms: Iterable[Classroom]) -> Classroom:
    """
    Merges multiple classrooms into one.

    :param classrooms: multiple classrooms
    :type classrooms: Iterable[Classroom]
    :return: the new classroom
    :rtype: Classroom

    :Example:

    >>> c1 = Classroom(address1, 'classA', 1)
    >>> c2 = Classroom(address2, 'classB', 2)
    >>> c3 = merge_classrooms((c1, c2))
    """
    names = ' | '.join(classroom.infos['name'] for classroom in classrooms)
    addresses = '\n'.join(str(classroom.infos['address']) for classroom in classrooms)
    return Classroom(name=names, address=addresses, id=-1)

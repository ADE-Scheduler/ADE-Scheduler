import json
import time
from typing import Dict, Iterable, Union

import pandas as pd
from geopy.geocoders import Nominatim

import backend.resources as rsrc


class Address:
    """
    Address object made from informations retrieved via ADE API.

    :param kwargs: dict with minimal entries (can be None):
        - address1
        - zipCode
        - city
        - country
    :type kwargs: str

    :Example:

    >>> informations = dict(address1='Rue Rose 42', zipCode='1300', city='Wavre', country='Belgique')
    >>> address = Address(**informations)
    """

    def __init__(self, **kwargs: str):
        self.address = kwargs

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        location = "\n".join(
            filter(
                None,
                [
                    self.address[rsrc.INDEX.ADDRESS],
                    self.address[rsrc.INDEX.ZIP_CODE],
                    self.address[rsrc.INDEX.CITY],
                    self.address[rsrc.INDEX.COUNTRY],
                ],
            )
        )

        return location


def get_geo_locations() -> Dict:
    """
    Returns the dictionary mapping each address to its geo-location.

    :return: the geo-locations
    :rtype: Dict
    """
    with open("static/json/geo_locations.json", "r") as f:
        return json.load(f)


def save_geo_locations(geo_locations: Dict):
    """
    Saves the dictionary of geo-locations into a json file with pretty indent.
    This file can be manually edited without causing any problem.

    :param geo_locations: the geo-locations
    :type geo_locations: Dict
    """
    with open("static/json/geo_locations.json", "w") as f:
        json.dump(geo_locations, f, sort_keys=True, indent=4)
        f.write("\n")


def prettify_classrooms(classrooms: pd.DataFrame, sleep: float = 0) -> pd.DataFrame:
    """
    Returns the classrooms dataframe in a pretty format, useful when need to display.

    The function will request, for every different address, a geo-localisation,
    so it can take some times.
    If too many requests are done, Nominatim will not like it so prefer to put a
    time.sleep between each request.

    :param classrooms: the classrooms with fields defined in backend.resources.py
    :type classrooms: pd.DataFrame
    :param sleep: the sleep duration between each address request
    :type sleep: float
    :return: the classrooms in a prettier format and with geo-location information
    :rtype: pd.DataFrame
    """

    geolocator = Nominatim(user_agent="ADE_SCHEDULER")
    geo_locations = get_geo_locations()

    def __pretty__(classroom: pd.Series):
        address = Address(**classroom.to_dict())
        location = str(address).replace("\n", ", ")
        name = classroom[rsrc.INDEX.NAME]
        code = classroom[rsrc.INDEX.CODE]

        return pd.Series([name, code, location], index=["name", "code", "address"])

    def __geoloc__(classroom: pd.Series):
        name = classroom["name"]
        code = classroom["code"]
        address = classroom["address"]

        geo_location = geo_locations[address]

        if geo_location is None:
            latitude = None
            longitude = None
        else:
            latitude = geo_location["lat"]
            longitude = geo_location["lon"]

        return pd.Series(
            [name, code, address, latitude, longitude],
            index=["name", "code", "address", "latitude", "longitude"],
            dtype=object,
        )

    classrooms = classrooms.apply(__pretty__, axis=1, result_type="expand")

    for address in classrooms["address"].unique():
        if address not in geo_locations:
            response = geolocator.geocode(address, exactly_one=True)
            time.sleep(sleep)
            if response is not None:
                geo_locations[address] = response.raw
            else:
                geo_locations[address] = None

    save_geo_locations(geo_locations)

    return classrooms.apply(__geoloc__, axis=1, result_type="expand")


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
        return str(self.infos["name"]) + "\n" + str(self.infos["address"])

    def __hash__(self):
        return hash(self.infos)

    def __eq__(self, other):
        return self.infos == other.infos

    def __repr__(self) -> str:
        id = self.infos["id"]
        name = self.infos["name"]
        return f"{id}: {name}"

    def location(self) -> str:
        """
        Returns the location (address) of this classroom.

        :return: the location
        :rtype: str
        """
        return "\n".join(filter(None, str(self).split("\n")))  # Removes blank lines


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
    names = " | ".join(
        classroom.infos["name"] for classroom in classrooms if classroom.infos["name"]
    )
    addresses = "\n".join(str(classroom.infos["address"]) for classroom in classrooms)
    id = "|".join(
        classroom.infos["id"] for classroom in classrooms if classroom.infos["id"]
    )
    return Classroom(name=names, address=addresses, id=id)

from typing import Iterable, Union


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
        location = ''
        if self.address['address2']:
            location += self.address['address2']
        if self.address['address1']:
            if location and ['address2']:
                location += ' ' + self.address['address1']
            else:
                location += '\n' + self.address['address1']
        if self.address['zipCode']:
            location += '\n' + self.address['zipCode']
        if self.address['city']:
            if location and self.address['zipCode']:
                location += ' ' + self.address['city']
            else:
                location += '\n' + self.address['city']
        if self.address['country']:
            location += '\n' + self.address['country']

        return location


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

from typing import Iterable, Optional


class Professor:
    """
    A professor is one or many people in charge of a given academical event.

    :param name: the name(s)
    :type name: str
    :param email: the email(s)
    :type email: Optional[str]
    """

    def __init__(self, name: str, email: Optional[str] = None):
        self.name = name
        self.email = email

    def __str__(self):
        if self.email is not None and len(self.email) > 0:
            return f"{self.name} ({self.email})"
        else:
            return self.name


def merge_professors(professors: Iterable[Professor]) -> Professor:
    """
    Merges multiple professors into one.

    :param professors: multiple professors
    :type professors: Iterable[Professor]
    :return: the new professor
    :rtype: Professor

    :Example:

    >>> p1 = Professor('Jean Moulin', 'jean.moulin@mail.com')
    >>> p2 = Professor('Marc Potier', 'marc.potier@mail.com')
    >>> p3 = merge_professors((p1, p2))
    """
    name = " & ".join(professor.name for professor in professors)
    email = " & ".join(professor.email for professor in professors if professor.email)
    if len(email) > 0:
        return Professor(name, email)
    else:
        return Professor(name)

from typing import Iterable


class Professor:

    def __init__(self, name: str, email: str = None):
        self.name = name
        self.email = email

    def __str__(self) -> None:
        if self.email:
            return f'{self.name} ({self.email})'
        else:
            return self.name


def merge_professors(professors: Iterable[Professor]) -> Professor:
    name = ' & '.join(professor.name for professor in professors)
    email = ' & '.join(professor.email for professor in professors if professor.email)
    if len(email) > 0:
        return Professor(name, email)
    else:
        return Professor(name)

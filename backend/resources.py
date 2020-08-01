from enum import Enum, auto


class Category(Enum):
    TEACHER = auto()
    CLASSROOM = auto()
    COURSE = auto()
    COURSE_COMBO = auto()
    UNDEFINED = auto()


class Resource:
    """
    A resource is anything that can be requested from ADE API: a teacher, a classroom, an activity...

    :param kwargs: attribute(s) of this resource
    :type kwargs: Any
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return str(self.kwargs)

    def __repr__(self):
        return str(self.kwargs['name'])

    def __hash__(self):
        return hash(self.kwargs)

    def __eq__(self, other):
        return self.kwargs['name'] == other.kwargs['name']

    def get_category(self) -> Category:
        """
        Returns the category of this resource.

        :return: the category
        :rtype: Category
        """
        category = self.kwargs['category']
        if category == 'category5':
            return Category.COURSE
        elif category == 'trainee':
            return Category.COURSE_COMBO
        elif category == 'classroom':
            return Category.CLASSROOM
        elif category == 'instructor':
            return Category.TEACHER
        else:
            return Category.UNDEFINED

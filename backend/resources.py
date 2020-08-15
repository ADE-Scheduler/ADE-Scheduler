class INDEX:
    ID = 'id'
    TYPE = 'category'
    NAME = 'name'
    PATH = 'path'
    IS_GROUP = 'isGroup'
    FACILITY_TYPE = 'type'
    EMAIL = 'email'
    URL = 'url'
    CONSUMER = 'consumer'
    SIZE = 'size'
    LAST_UPDATE = 'lastUpdate'
    CREATION = 'creation'
    LAST_SLOT = 'lastSlot'
    LAST_DAY = 'lastDay'
    LAST_WEEK = 'lastWeek'
    FIRST_SLOT = 'firstSlot'
    FIST_DAY = 'firstDay'
    FIRST_WEEK = 'firstWeek'
    DURATION_IN_MINUTES = 'durationInMinutes'
    NB_EVENTS_PLACES = 'nbEventsPlaced'
    AVAILABLE_QUANTITY = 'availableQuantity'
    NUMBER = 'number'
    FATHER_NAME = 'fatherName'
    FATHER_ID = 'fatherId'
    INFO = 'info'
    CODE_Z = 'codeZ'
    CODE_Y = 'codeY'
    CODE_X = 'codeX'
    MANAGER = 'manager'
    JOB_CATEGORY = 'jobCategory'
    TIMEZONE = 'timezone'
    FAX = 'fax'
    PHONE = 'telephone'
    COUNTRY = 'country'
    CITY = 'city'
    STATE = 'state'
    ZIP_CODE = 'zipCode'
    IP_ADDRESS = 'address2'
    ADDRESS = 'address1'
    CODE = 'code'
    COLOR = 'color'
    LEVEL_ACCESS = 'levelAccess'
    OWNER = 'owner'


class TYPES:
    TEACHER = 'instructor'
    CLASSROOM = 'classroom'
    COURSE = 'category5'
    COURSE_COMBO = 'trainee'


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


from typing import Dict, Iterator, List, Optional, Tuple, Union

import lxml
import pandas as pd
import requests
from flask_babel import gettext
from ics import Calendar

import backend.ade_api as ade
import backend.classrooms as clrm
import backend.courses as crs
import backend.events as evt
import backend.models as md
import backend.resources as rsrc
import backend.schedules as schd
import backend.servers as srv


class ScheduleNotFountError(Exception):
    """
    Exception that will occur if a schedule is marked as saved but is not in the database.
    """

    def __str__(self):
        return gettext("The given schedule is somehow not saved in our database...")


class ExternalCalendarAlreadyExistsError(Exception):
    """
    Exception that will occur if someone tries to create a calendar with a code already taken.
    """

    def __str__(self):
        return gettext("The given calendar code is already taken.")


class Manager:
    """
    The manager ensures that data is accessible and provides access to it.

    Data can either be found in the server, in the database or obtained from the ADE API.
    At initialization, each source is checked to ensure that they are working properly.

    :param client: the client providing access to ADE API
    :type client: ade_api.Client
    :param server: the server providing temporary memory
    :type server: server.Server
    :param database: the database
    :type database: md.SQLAlchemy
    :param ttl: a dictionary mapping keys in server to their default time-to-live value
    :type ttl: Dict
    """

    def __init__(
        self, client: ade.Client, server: srv.Server, database: md.SQLAlchemy, ttl: Dict
    ):
        self.server = server
        self.client = client
        self.database = database
        self.ttl = ttl

    def get_courses(self, *codes: str, project_id: str = None) -> List[crs.Course]:
        """
        Returns the courses with given codes as a list.
        Order of courses is consistent with initial order of the codes.

        :param codes: the code(s) of the course(s)
        :type codes: str
        :param project_id: the project id
        :type project_id: str
        :return: the list of courses
        :rtype: List[crs.Course]
        """
        codes = list(codes)

        if project_id is None:
            project_id = self.get_default_project_id()

        # Fetch from the server
        prefix = f"[project_id={project_id}]"

        courses_expired = self.server.get_multiple_values_expired(
            *codes,
            prefix=prefix,
        )
        courses, codes_not_found = self.server.get_multiple_values(
            *codes, prefix=prefix
        )

        def _fetch_code(code_not_found):
            course_not_found = None
            if code_not_found.startswith("EXT:"):
                extCal = (
                    md.ExternalCalendar.query.filter_by(approved=True)
                    .filter(md.ExternalCalendar.code == code_not_found)
                    .first()
                )
                if extCal is None:  # In case the owner of extCal deleted it
                    return None
                url = extCal.url
                events = Calendar(requests.get(url).text).events
                events = [
                    evt.EventEXTERN.from_event(event, code_not_found[4:])
                    for event in events
                ]
                course_not_found = crs.Course(code_not_found[4:], extCal.name)
                for event in events:
                    course_not_found.add_activity([event])

            else:
                resource_ids = self.get_resource_ids(
                    code_not_found, project_id=project_id
                )
                course_not_found = ade.response_to_courses(
                    self.client.get_activities(resource_ids, project_id)
                )

            return course_not_found

        # Fetch from the api the missing courses
        if codes_not_found:
            for code_not_found in codes_not_found:
                course_not_found = _fetch_code(code_not_found)

                if course_not_found is None:
                    codes.remove(code_not_found)
                    continue

                self.server.set_value(
                    prefix + code_not_found,
                    course_not_found,
                    expire_in=self.ttl["courses"],
                    notify_expire_in=self.ttl["courses_notify"],
                )
                courses[code_not_found] = course_not_found

        # Fetch from the api the courses that have expired
        # those can have errors, we will fetch them later
        for code_expired in [
            key for key, expired in courses_expired.items() if expired is True
        ]:
            try:
                course_expired = _fetch_code(code_expired)

                if course_expired is None:
                    codes.remove(code_expired)
                    continue

                courses[code_expired] = course_expired
                self.server.set_value(
                    prefix + code_expired,
                    course_expired,
                    expire_in=self.ttl["courses"],
                    notify_expire_in=self.ttl["courses_notify"],
                )
            except lxml.etree.XMLSyntaxError as e:
                self.server.set_value(
                    prefix + code_expired,
                    courses[code_expired],  # this already exists
                    expire_in=self.ttl["courses"],
                    notify_expire_in=self.ttl["courses_renotify"],
                )

        ret = list()

        for code in codes:
            course = courses[code]
            if isinstance(course, list):  # Happens if course is a course combo
                ret.extend(course)
            else:
                ret.append(course)

        return ret

    def get_events_in_classroom(
        self, classroom_id: str, project_id: str = None
    ) -> List[evt.AcademicalEvent]:
        if project_id is None:
            project_id = self.get_default_project_id()

        # Fetch from the server
        key = f"[EVENTS_CLASSROOM_ID={classroom_id}, project_id={project_id}]"
        events = self.server.get_value(key)

        if events is not None:
            return events

        def filter_func(event: evt.AcademicalEvent):
            for classroom in event.classrooms:
                if classroom_id == classroom.infos["id"]:
                    return True
            return False

        events = ade.response_to_events(
            self.client.get_activities([classroom_id], project_id), filter_func
        )
        self.server.set_value(key, events, expire_in=self.ttl["events_in_classroom"])
        return events

    def get_resources(self, project_id: str = None) -> pd.DataFrame:
        """
        Returns the resources.

        :param project_id: the project id
        :type project_id: str
        :return: the resources
        :rtype: pd.DataFrame
        """
        if project_id is None:
            project_id = self.get_default_project_id()

        key = f"[RESOURCES,project_id={project_id}]"

        if not self.server.exists(key):
            self.update_resources()

        return self.server.get_value(key)

    def update_resources(self):
        """
        Updates the resources contained in the server for all project ids.
        """
        key = "[PROJECT_IDs]"
        if not self.server.exists(key):
            self.update_project_ids()

        for value in self.server.hgetall(key).values():
            value = value.decode()
            key = f"[RESOURCES,project_id={value}]"

            resources = ade.response_to_resources(self.client.get_resources(value))
            self.server.set_value(key, resources, expire_in=self.ttl["resources"])

    def get_course_resources(self, project_id: str = None) -> pd.DataFrame:
        """
        Returns the course resources.

        :param project_id: the project id
        :type project_id: str
        :return: the courses resources
        :rtype: pd.DataFrame
        """
        if project_id is None:
            project_id = self.get_default_project_id()

        key = f"[COURSE_RESOURCES,project_id={project_id}]"

        if not self.server.exists(key):
            self.update_course_resources()

        return self.server.get_value(key)

    def update_course_resources(self):
        """
        Updates the course resources contained in the server for all project ids.
        """
        key = "[PROJECT_IDs]"
        if not self.server.exists(key):
            self.update_project_ids()

        for value in self.server.hgetall(key).values():
            value = value.decode()
            key = f"[COURSE_RESOURCES,project_id={value}]"

            resources = ade.response_to_course_resources(
                self.client.get_course_resources(project_id=value)
            )
            resource_types = resources[rsrc.INDEX.TYPE]
            index = (resource_types == rsrc.TYPES.COURSE) | (
                resource_types == rsrc.TYPES.COURSE_COMBO
            )
            course_resources = resources[index].copy()
            code = rsrc.INDEX.CODE
            course_resources[code] = course_resources[code].apply(str.upper)
            self.server.set_value(
                key, course_resources, expire_in=self.ttl["course_resources"]
            )

    def get_codes_matching(self, pattern: str, project_id: str = None) -> List[str]:
        # Actually returns names matchings :)
        course_resources = self.get_course_resources(project_id)
        matching_code = course_resources[rsrc.INDEX.NAME].str.contains(
            pattern, case=False, regex=False
        )
        courses_matching = course_resources[matching_code][rsrc.INDEX.NAME].to_list()
        courses_matching.extend(
            map(
                lambda ec: ec.code,
                md.ExternalCalendar.query.filter_by(approved=True)
                .filter(md.ExternalCalendar.code.contains(pattern))
                .all(),
            )
        )
        return courses_matching

    def get_classrooms(
        self,
        project_id: str = None,
        search_dict: Dict[str, str] = None,
        return_json: bool = False,
    ):
        if project_id is None:
            project_id = self.get_default_project_id()

        key = f"[CLASSROOMS,project_id={project_id}]"

        if not self.server.exists(key):
            self.update_classrooms()

        classrooms = self.server.get_value(key)

        if search_dict is not None:
            for index, search in search_dict.items():
                contains = classrooms[index].str.contains(search, regex=False)
                classrooms = classrooms[contains]

        if return_json:
            return list(
                classrooms.reset_index(level=0).to_dict(orient="index").values()
            )
        else:
            return classrooms

    def update_classrooms(self, drop_empty: List[str] = [rsrc.INDEX.ADDRESS]):
        """
        Updates the classrooms contained in the server for all project ids.
        """
        key = "[PROJECT_IDs]"
        if not self.server.exists(key):
            self.update_project_ids()

        for value in self.server.hgetall(key).values():
            value = value.decode()
            key = f"[CLASSROOMS,project_id={value}]"

            resources = self.get_resources(project_id=value)

            classrooms_index = resources[rsrc.INDEX.TYPE] == rsrc.TYPES.CLASSROOM
            classrooms = resources[classrooms_index]

            for drop_index in drop_empty:
                not_empty = classrooms[drop_index] != ""
                classrooms = classrooms[not_empty]

            classrooms = clrm.prettify_classrooms(classrooms)

            self.server.set_value(key, classrooms, expire_in=self.ttl["classrooms"])

    def get_resource_ids(self, *codes: str, project_id: str = None) -> Iterator[str]:
        """
        Returns the resource ids of each code.

        :param codes: the code(s) (name(s)) of the resources
        :type codes: str
        :param project_id: the project id
        :type project_id: str
        :return: the resource ids
        :rtype: Iterator[str]
        """
        if project_id is None:
            project_id = self.get_default_project_id()

        key = f"[RESOURCE_IDs,project_id={project_id}]"
        if not self.server.exists(key):
            self.update_resource_ids()
        return map(lambda x: x.decode(), filter(None, self.server.hmget(key, codes)))

    def update_resource_ids(self):
        """
        Updates the resource ids contained in the server for all project ids.
        """
        key = "[PROJECT_IDs]"
        if not self.server.exists(key):
            self.update_project_ids()

        for value in self.server.hgetall(key).values():
            value = value.decode()
            key = f"[RESOURCE_IDs,project_id={value}]"
            resource_ids = ade.response_to_resource_ids(
                self.client.get_resource_ids(value)
            )
            self.server.set_value(
                key, resource_ids, expire_in=self.ttl["resource_ids"], hmap=True
            )

    def code_exists(self, code, project_id: str = None) -> bool:
        """
        Checks if a given code exists in the database for a given project id
        """
        if code.startswith("EXT:"):
            return (
                md.ExternalCalendar.query.filter_by(approved=True)
                .filter(md.ExternalCalendar.code == code)
                .first()
                is not None
            )
        if project_id is None:
            project_id = self.get_default_project_id()

        hmap = f"[RESOURCE_IDs,project_id={project_id}]"
        if not self.server.contains(hmap):
            self.update_resource_ids()

        return self.server.hexists(hmap, code)

    def get_project_ids(
        self, year: Optional[str] = None
    ) -> Union[List[Dict[str, str]], str, None]:
        """
        Returns the project ids. If year is specified, only the project id of this year is returned.

        :param year: the year, '2019-2020' format
        :type year: str
        :return: the list of ids and years or the id of one year or None if no id was found
        :rtype: Union[List[Dict[str, str]], str, None]
        """
        hmap = "[PROJECT_IDs]"
        if not self.server.exists(hmap):
            self.update_project_ids()
        if year is None:
            return [
                {"id": value.decode(), "year": key.decode()}
                for key, value in self.server.hgetall(hmap).items()
            ]
        value = self.server.get_value(year, hmap=hmap)
        if value[-1] is not None:
            return value[-1].decode()
        else:
            return None

    def update_project_ids(self):
        """
        Updates the project ids.
        """
        key = "[PROJECT_IDs]"
        project_ids = ade.response_to_project_ids(self.client.get_project_ids())
        self.server.set_value(
            key, project_ids, expire_in=self.ttl["project_ids"], hmap=True
        )

    def get_default_project_id(self) -> str:
        """
        Returns the default project id.

        :return: the default project id
        :rtype: str
        """
        return self.get_project_ids()[0]["id"]

    def save_schedule(self, user: md.User, schedule: schd.Schedule, uuid):
        """
        Saves a schedule binding it to a user into the database.

        :param user: the user
        :type user: md.User
        :param schedule: the schedule
        :type schedule: schd.Schedule
        :return: the scheduler, with its id updated...

        """
        if schedule.id is None:  # this schedule is not yet saved
            schd = md.Schedule(data=schedule, user=user)
            schd.data.id = schd.id
            self.database.session.commit()

        else:  # this schedule has already been saved
            schd = md.Schedule.query.filter(md.Schedule.id == schedule.id).first()
            if schd is None:
                raise ScheduleNotFountError
            else:
                schd.update_data(schedule)

            if user is not None:
                user_has_schedule = user.get_schedule(id=schedule.id) is not None
            else:
                user_has_schedule = False

            if not user_has_schedule and user is not None:
                user.add_schedule(schd)

        # Update the last person to modify the schedule
        schd.update_last_modified_by(uuid)
        return schd.data

    def get_schedule(self, link):
        query = md.Link.query.filter(md.Link.link == link).first()
        if query:
            return query.schedule.data, query.choice
        else:
            return None, None

    def get_link(self, schedule_id):
        query = md.Schedule.query.filter(md.Schedule.id == schedule_id).first()
        if query:
            return query.link.link
        else:
            return None

    def get_plots(self) -> List[Tuple[str, dict]]:
        """
        Returns all the (key, plot) pairs stored in the server.
        Plots are json dictionary generated using Plotly.

        :return: the pairs of (key, plot) that were stored in the server
        :rtype: List[Tuple[str, dict]]
        """
        plots = []
        for key in self.server.scan_iter(match="*PLOT*"):
            plots.append({"id": key.decode(), "data": self.server.get_value(key)})

        return plots

    def save_ics_url(
        self,
        code: str,
        name: str,
        url: str,
        description: str,
        user: md.User,
        approved: bool,
    ):
        if not code.startswith("EXT:"):
            code = "EXT:" + code

        extCal = md.ExternalCalendar.query.filter_by(code=code).first()
        if extCal is None:  # this external calendar code is not yet saved
            md.ExternalCalendar(code, name, url, description, user, approved)
        else:  # this external calendar code is already in DB
            raise ExternalCalendarAlreadyExistsError

    def get_external_calendars(self, user: md.User) -> List[md.ExternalCalendar]:
        return md.ExternalCalendar.query.filter(
            md.ExternalCalendar.user_id == user.id
        ).all()

    def delete_external_calendar(self, id: int):
        md.ExternalCalendar.query.filter_by(id=id).delete()
        self.database.session.commit()

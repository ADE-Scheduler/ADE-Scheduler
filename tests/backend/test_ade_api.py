from time import time

import backend.ade_api as ade


class TestDummyClientImplementation:
    @staticmethod
    def test_is_expired(ade_client, app):
        with app.app_context():
            func = ade_client.is_expired
            got = func()
            expected = ade_client.expiration < time()

            assert got == expected

    @staticmethod
    def test_expire_in(ade_client, app):
        with app.app_context():
            func = ade_client.expire_in
            t1 = time()
            got = func()
            expected = max(ade_client.expiration - time(), 0)
            t2 = time()
            dt = t2 - t1

            assert abs(got - expected) < dt

    @staticmethod
    def renew_token(ade_client, app):
        with app.apprenew_token():
            func = ade_client.renew_token
            got, _ = func()

            assert got is not None

    @staticmethod
    def test_request(ade_client, app):
        with app.app_context():
            func = ade_client.request
            got = func(function="projects")

            assert got is not None


def test_get_token(ade_client, app):
    with app.app_context():
        func = ade.get_token

        got, _ = func(ade_client.credentials)

        assert got is not None


def test_all_requests(ade_client, app):
    with app.app_context():
        # 1. Project ids

        resp = ade_client.get_project_ids()

        assert resp is not None

        project_ids = ade.response_to_project_ids(resp)

        assert project_ids is not None

        for value in project_ids.values():
            project_id = value

        # 2. Resources

        if False:  # We avoid getting all resources if this function is not used
            resp = ade_client.get_resources(project_id)

            assert resp is not None

            resources = ade.response_to_resources(resp)

            assert resources is not None

        # 3. Resource ids

        resp = ade_client.get_resource_ids(project_id)

        assert resp is not None

        resource_ids = ade.response_to_resource_ids(resp)

        assert resource_ids is not None

        # 4. Classrooms, root and room to classroom

        resp = ade_client.get_classrooms(project_id)

        assert resp is not None

        classrooms = ade.response_to_classrooms(resp)

        assert classrooms is not None

        root = ade.response_to_root(resp)

        assert root is not None

        rooms = root.xpath("//room")

        classroom = ade.room_to_classroom(rooms[0])

        assert classroom is not None

        # 5. Courses, parsing events and activities

        ids = [
            resource_ids[course]
            for course in ["LEPL1101", "LEPL1102", "LEPL1103", "LEPL1104"]
        ]

        resp = ade_client.get_activities(ids, project_id)

        assert resp is not None

        courses = ade.response_to_courses(resp)

        assert courses is not None

        # TODO: test real filtering

        from backend.events import AcademicalEvent

        def filter_func(e: AcademicalEvent) -> bool:
            return True

        activities = ade.response_to_events(resp, filter_func)

        assert activities is not None

        root = ade.response_to_root(resp)

        activities = root.xpath("//activity")

        activity = ade.parse_activity(activities[0])

        assert activity is not None

        events = list()

        for activity in activities:
            events.extend(activity.xpath(".//event"))

        event = ade.parse_event(events[0], AcademicalEvent, "", "", "")

        assert event is not None

import os
import pytest
import backend.ade_api as ade
import backend.servers as srv


@pytest.fixture(scope="session")
def ade_client():
    return ade.Client(
        dict(
            user=os.environ["ADE_USER"],
            password=os.environ["ADE_PASSWORD"],
            secret_key=os.environ["ADE_SECRET_KEY"],
            url=os.environ["ADE_URL"],
            data=os.environ["ADE_DATA"],
            Authorization=os.environ["ADE_AUTHORIZATION"],
        )
    )


@pytest.fixture
def project_id(ade_client):
    resp = ade_client.get_project_ids()
    project_ids = ade.response_to_project_ids(resp)

    return project_ids.popitem()[1]


""" Until further notice, not used
@pytest.fixture
def resources(ade_client, project_id):
    resp = ade_client.get_resources(project_id)

    return ade.response_to_resources(resp)
"""


@pytest.fixture
def resource_ids(ade_client, project_id):
    resp = ade_client.get_resource_ids(project_id)

    return ade.response_to_resource_ids(resp)


@pytest.fixture
def classrooms(ade_client, project_id):
    resp = ade_client.get_classrooms(project_id)

    return ade.response_to_classrooms(resp)


@pytest.fixture
def courses(ade_client, project_id, resource_ids):
    ids = [
        resource_ids[course]
        for course in ["LEPL1101", "LEPL1102", "LEPL1103", "LEPL1104"]
    ]

    resp = ade_client.get_activities(ids, project_id)

    return ade.response_to_courses(resp)


@pytest.fixture
def server():
    return srv.Server()

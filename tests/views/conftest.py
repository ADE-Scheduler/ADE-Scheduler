import pytest
import backend.models as md

from app import app as ade_scheduler


@pytest.fixture
def app():
    return ade_scheduler


@pytest.fixture
def user():
    test_users = list()
    test_users.append(md.User(email="jyl@scheduler.ade", password="password"))
    # Add schedules, etc. to users for testing purposes
    md.db.session.commit()

    yield test_users

    for user in test_users:
        user.delete()
    md.db.session.commit()

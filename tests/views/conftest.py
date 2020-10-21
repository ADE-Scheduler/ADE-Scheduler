import pytest
import datetime

import backend.models as md
import backend.schedules as schd
import views.utils as utl

from app import app as ade_scheduler
from flask import session
from flask_security import hash_password, login_user, logout_user


@pytest.fixture
def app(scope="session"):
    yield ade_scheduler


@pytest.fixture
def manager(app, scope="session"):
    yield app.config["MANAGER"]


@pytest.fixture
def jyl(app, manager):
    """
    Create a test user.
    JYL has a confirmed account and is logged in.
    """
    user_datastore = app.config["SECURITY_MANAGER"].datastore

    jyl = user_datastore.create_user(
        email="jyl@scheduler.ade",
        password=hash_password("password"),
        confirmed_at=datetime.datetime.now(),
        active=True,
    )
    jyl.set_autosave(True)
    login_user(jyl)
    utl.init_session()

    schedule = md.Schedule(
        schd.Schedule(manager.get_default_project_id(), label="JYL'S SCHEDULE"),
        user=jyl,
    )
    session["current_schedule"] = schedule.data
    md.db.session.add(schedule)
    md.db.session.commit()

    yield jyl

    logout_user()
    md.db.session.delete(schedule)
    md.db.session.delete(jyl)
    md.db.session.commit()


@pytest.fixture
def gerom(app, manager):

    """
    Create a test user.
    Gerom has a confirmed account, but is not logged in.
    """
    user_datastore = app.config["SECURITY_MANAGER"].datastore

    gerom = user_datastore.create_user(
        email="gerom@scheduler.ade",
        password=hash_password("password"),
        confirmed_at=datetime.datetime.now(),
    )

    schedule = md.Schedule(
        schd.Schedule(manager.get_default_project_id(), label="gerom'S SCHEDULE"),
        user=gerom,
    )
    md.db.session.add(schedule)
    md.db.session.commit()

    yield gerom

    md.db.session.delete(schedule)
    md.db.session.delete(gerom)
    md.db.session.commit()


@pytest.fixture
def louwi(manager):
    """
    Create a test user.
    Louwi has no account, but is an active anonymous user.
    """
    utl.init_session()

    session["current_schedule"] = schd.Schedule(
        manager.get_default_project_id(), label="LOUWI'S SCHEDULE"
    )


@pytest.fixture
def user(request):
    return request.getfixturevalue(request.param)

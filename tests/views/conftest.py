import copy
import pytest
import datetime

import backend.models as md
import backend.schedules as schd
import views.utils as utl

from app import app as ade_scheduler
from flask import session
from flask_security import hash_password, AnonymousUser


@pytest.fixture(scope="session")
def app():
    return ade_scheduler


@pytest.fixture(scope="session")
def manager(app):
    return app.config["MANAGER"]


@pytest.fixture(scope="session")
def db(manager):
    return manager.database


@pytest.fixture(scope="session")
def user_ds(app):
    return app.config["SECURITY_MANAGER"].datastore


@pytest.fixture
def jyl(app, manager, user_ds, db):
    """
    Create a test user.
    JYL has a confirmed account and is logged in.
    """
    jyl = user_ds.create_user(
        email="jyl@scheduler.ade",
        password=hash_password("password"),
        confirmed_at=datetime.datetime.now(),
        active=True,
    )

    data = schd.Schedule(manager.get_default_project_id(), label="JYL'S SCHEDULE")
    data.add_course("LEPL1104")
    active_schedule = md.Schedule(data, user=jyl)
    db.session.add(active_schedule)

    old_schedule = md.Schedule(
        schd.Schedule(manager.get_default_project_id(), label="OLD SCHEDULE"), user=jyl
    )
    db.session.add(old_schedule)
    db.session.commit()

    # Login user
    @app.login_manager.request_loader
    def load_user_from_request(request):
        utl.init_session()
        session["current_schedule"] = copy.copy(jyl.get_schedules()[0].data)
        return jyl

    yield jyl

    # Logout & delete user
    @app.login_manager.request_loader
    def load_user_from_request(request):
        return None

    db.session.delete(active_schedule)
    db.session.delete(old_schedule)
    db.session.delete(jyl)
    db.session.commit()


@pytest.fixture
def gerom(app, manager, user_ds, db):

    """
    Create a test user.
    Gerom has a confirmed account, but is not logged in.
    """
    gerom = user_ds.create_user(
        email="gerom@scheduler.ade",
        password=hash_password("password"),
        confirmed_at=datetime.datetime.now(),
        active=True,
    )

    schedule = md.Schedule(
        schd.Schedule(manager.get_default_project_id(), label="GEROM'S SCHEDULE"),
        user=gerom,
    )
    db.session.add(schedule)
    db.session.commit()

    yield gerom

    db.session.delete(schedule)
    db.session.delete(gerom)
    db.session.commit()


@pytest.fixture
def louwi(app, manager):
    """
    Create a test user.
    Louwi has no account, but is an active anonymous user.
    """

    @app.login_manager.request_loader
    def load_user_from_request(request):
        utl.init_session()
        session["current_schedule"] = schd.Schedule(
            manager.get_default_project_id(), label="LOUWI'S SCHEDULE"
        )
        return None

    yield AnonymousUser()

    @app.login_manager.request_loader
    def load_user_from_request(request):
        return None


@pytest.fixture
def user(request):
    return request.getfixturevalue(request.param)

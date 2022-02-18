import copy
import uuid

from flask import session, url_for
from flask_babel import gettext

import views.utils as utl


def test_init_session(app, manager):
    """Test the session initialisation"""

    # Test session initialisation
    with app.app_context():
        utl.init_session()

    assert session["current_schedule"].label == gettext("New schedule")
    assert session["current_schedule"].is_empty()
    assert not session["current_schedule_modified"]

    # Check that "fake" project_ids are correctly replaced
    session["current_schedule"].project_id = 42666
    utl.init_session()

    assert int(session["current_schedule"].project_id) in [
        int(year["id"]) for year in manager.get_project_ids()
    ]


def test_autosave_schedule(client, jyl, db):
    """Test the schedule autosave"""
    schedules = jyl.get_schedules()

    assert "ELME2M" not in schedules[0].data.codes

    # Autosave disabled
    jyl.set_autosave(False)
    rv = client.patch(url_for("calendar.add_code", code="ELME2M"))

    assert "ELME2M" not in schedules[0].data.codes
    assert session["current_schedule_modified"]

    # Auto save enabled
    jyl.set_autosave(True)
    rv = client.patch(url_for("calendar.add_code", code="ELME2M"))

    assert "ELME2M" in schedules[0].data.codes
    assert not session["current_schedule_modified"]


def test_autoload_schedule(client, jyl):
    """Test the schedule autoload"""
    schedules = jyl.get_schedules()

    # Save the current schedule once
    rv = client.post(url_for("calendar.save"))

    assert rv.status_code == 200

    # Simulate a change of device
    session["uuid"] = uuid.uuid4()
    schedule = copy.copy(schedules[0].data)
    schedule.label = "ANOTHER LABEL"
    schedule.codes = ["CODE", "LIST"]
    schedules[0].update_data(schedule)

    assert session["current_schedule"].label == "JYL'S SCHEDULE"
    assert session["current_schedule"].codes == ["LEPL1104"]

    rv = client.get(url_for("calendar.index"))

    assert session["current_schedule"].label == "ANOTHER LABEL"
    assert session["current_schedule"].codes == ["CODE", "LIST"]

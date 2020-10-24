import uuid
import copy
import views.utils as utl

from flask import session, url_for
import backend.models as md


def test_init_session(app, manager):
    """Test the session initialisation"""

    # Test session initialisation
    utl.init_session()

    assert session["current_schedule"].label == "New schedule"
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
    # This is required to ensure the schedule are sorted
    # PostgreSQL does not always return the list in the same order
    schedules = copy.copy(sorted(jyl.schedules, key=lambda e: int(e.id)))

    assert "ELME2M" not in schedules[0].data.codes

    # Autosave disabled
    jyl.set_autosave(False)
    rv = client.patch(url_for("calendar.add_code", code="ELME2M"))

    db.session.commit()  # required or schedules[0].data points to the current_schedule....
    assert "ELME2M" not in schedules[0].data.codes
    assert session["current_schedule_modified"]

    # Auto save enabled
    jyl.set_autosave(True)
    rv = client.patch(url_for("calendar.add_code", code="ELME2M"))

    db.session.commit()
    assert "ELME2M" in schedules[0].data.codes
    assert not session["current_schedule_modified"]


def test_autoload_schedule(client, jyl):
    """Test the schedule autoload"""
    # This is required to ensure the schedule are sorted
    # PostgreSQL does not always return the list in the same order
    schedules = sorted(jyl.schedules, key=lambda e: int(e.id))

    # Save the current schedule once
    rv = client.post(url_for("calendar.save"))

    assert rv.status_code == 200

    # Simulate a change of device
    session["uuid"] = uuid.uuid4()
    schedule = copy.copy(session["current_schedule"])
    schedule.label = "ANOTHER LABEL"
    schedule.codes = ["CODE", "LIST"]
    schedules[0].update_data(schedule)

    assert session["current_schedule"].label == "JYL'S SCHEDULE"

    rv = client.get(url_for("calendar.index"))

    assert session["current_schedule"].label == "ANOTHER LABEL"

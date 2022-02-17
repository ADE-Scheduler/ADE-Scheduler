from flask import session, url_for
from flask_login import current_user


def test_index(client, jyl):
    """Test the index route"""
    rv = client.get(url_for("account.index"))

    assert rv.status_code == 200
    assert b"DOCTYPE html" in rv.data


def test_get_data(client, manager, jyl):
    """Test the get_data route"""
    rv = client.get(url_for("account.get_data"))
    schd = session["current_schedule"]

    assert rv.status_code == 200
    assert rv.json["project_id"] == manager.get_project_ids()
    assert rv.json["unsaved"] == session["current_schedule_modified"]
    assert rv.json["autosave"] == current_user.autosave
    assert rv.json["schedules"] == list(
        map(lambda s: {"id": s.id, "label": s.data.label}, current_user.get_schedules())
    )
    assert rv.json["current_schedule"]["id"] == schd.id
    assert rv.json["current_schedule"]["project_id"] == schd.project_id
    assert rv.json["current_schedule"]["label"] == schd.label
    assert rv.json["current_schedule"]["color_palette"] == schd.color_palette


def test_load_schedule(client, jyl):
    """Test the load_schedule(id) route"""
    schedules = jyl.get_schedules()

    rv = client.get(url_for("account.load_schedule", id=42666))

    assert rv.status_code == 403

    rv = client.get(url_for("account.load_schedule", id=schedules[1].id))

    assert rv.status_code == 200
    assert session["current_schedule"].id == schedules[1].id


def test_delete_schedule(client, jyl):
    """Test the delete_schedule route"""
    schedules = jyl.get_schedules()

    rv = client.delete(url_for("account.delete_schedule", id=42666))

    assert rv.status_code == 403

    # Test delete another schedule
    rv = client.delete(url_for("account.delete_schedule", id=schedules[1].id))

    assert rv.status_code == 200
    assert len(jyl.schedules) == len(schedules) - 1
    assert session["current_schedule"].id == schedules[0].id

    # Test delete current schedule
    rv = client.delete(
        url_for("account.delete_schedule", id=session["current_schedule"].id)
    )

    assert rv.status_code == 200
    assert len(jyl.schedules) == len(schedules) - 2
    assert session["current_schedule"].id == None


def test_update_label(client, jyl):
    """Test the update_label(id) route"""
    schedules = jyl.get_schedules()

    rv = client.patch(
        url_for("account.update_label", id=42666), json=dict(label="LABEL CHANGED")
    )

    assert rv.status_code == 403

    rv = client.patch(
        url_for("account.update_label", id=schedules[0].id),
        json=dict(label="LABEL CHANGED"),
    )

    assert rv.status_code == 200
    assert schedules[0].data.label == "LABEL CHANGED"
    assert session["current_schedule"].label == "LABEL CHANGED"


def test_save(client, jyl):
    """Test the save route"""
    schedules = jyl.get_schedules()

    data = dict(project_id=42, color_palette=["BLACK", "YELLOW", "RED"])
    rv = client.post(url_for("account.save"), json=data)

    schd = schedules[0]
    assert rv.status_code == 200
    assert schd.data.project_id == data["project_id"]
    assert schd.data.color_palette == set(data["color_palette"])
    assert session["current_schedule"].project_id == data["project_id"]
    assert session["current_schedule"].color_palette == set(data["color_palette"])


def test_autosave(client, jyl):
    """Test the autosave route"""
    autosave = not current_user.autosave
    rv = client.post(url_for("account.autosave"), json=dict(autosave=autosave))

    assert rv.status_code == 200
    assert current_user.autosave == autosave


def test_login_required(client):
    """Test if every route is access-restricted to logged in users"""
    rv = client.get(url_for("account.index"))
    assert rv.status_code == 302

    rv = client.get(url_for("account.get_data"))
    assert rv.status_code == 302

    rv = client.get(url_for("account.load_schedule", id=1))
    assert rv.status_code == 302

    rv = client.delete(url_for("account.delete_schedule", id=1))
    assert rv.status_code == 302

    rv = client.patch(url_for("account.update_label", id=1))
    assert rv.status_code == 302

    rv = client.post(url_for("account.save"))
    assert rv.status_code == 302

    rv = client.post(url_for("account.autosave"))
    assert rv.status_code == 302

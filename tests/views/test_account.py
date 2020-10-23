from flask import url_for, session
from flask_security import current_user, login_user

import backend.models as md
import views.utils as utl


def test_get_data(client):
    """Test the get_data route"""
    # TODO
    assert True


def test_load_schedule(client):
    """Test the load_schedule(id) route"""
    # TODO
    assert True


def test_delete_schedule(client):
    """Test the delete_schedule route"""
    # TODO
    assert True


def test_update_label(client, jyl):
    """Test the update_label(id) route"""
    rv = client.patch(
        url_for("account.update_label", id=jyl.schedules[0].id),
        json=dict(label="LABEL CHANGED"),
    )

    assert rv.status_code == 200
    assert jyl.schedules[0].data.label == "LABEL CHANGED"
    assert session["current_schedule"].label == "LABEL CHANGED"


def test_save(client):
    """Test the save route"""
    # TODO
    assert True


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

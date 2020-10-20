from flask import url_for, session
from flask_security import current_user


def test_clear(client):
    """Test the clear route"""
    # TODO
    assert True


def test_get_data(client):
    """Test the get_data route"""
    # TODO
    assert True


def test_load_schedule(client):
    """Test the load_schedule route"""
    # TODO
    assert True


def test_search_code(client):
    """Test the search_code route"""
    # TODO
    assert True


def test_add_code(client):
    """Test the add_code route"""
    # TODO

    rv = client.get(url_for("calendar.add_code", code="ELME2M"))
    assert "ELME2M" in rv.json.get("codes")


def test_remove_code(client):
    """Test the remove_code route"""
    # TODO
    assert True


def test_get_info(client):
    """Test the get_info route"""
    # TODO
    assert True


def test_add_custom_event(client):
    """Test the add_custom_event route"""
    # TODO
    assert True


def test_delete_custom_event(client):
    """Test the delete_custom_event(id) route"""
    # TODO
    assert True


def test_update_custom_event(client):
    """Test the update_custom_event(id) route"""
    # TODO
    assert True


def test_save(client):
    """Test the save route"""
    # TODO
    assert True


def test_download(client):
    """Test the download route"""
    # TODO
    assert True


def test_share(client):
    """Test the share route"""
    # TODO
    assert True


def test_apply_filter(client):
    """Test the apply_filter route"""
    # TODO
    assert True


def test_update_project_id(client):
    """Test the update_poject_id route"""
    # TODO
    assert True


def test_export(client):
    """Test the export route"""
    # TODO
    assert True


def test_get_events(client):
    """Test the get_event route"""
    # TODO
    assert True


def test_compute(client):
    """Test the compute route"""
    # TODO
    assert True


def test_update_color(client):
    """Test the update_color route"""
    # TODO
    assert True


def test_reset_color(client):
    """Test the reset_color route"""
    # TODO
    assert True

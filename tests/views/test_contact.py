from flask import url_for


def test_index(client):
    """Test the index route"""
    rv = client.get(url_for("contact.index"))

    assert rv.status_code == 200
    assert b"DOCTYPE html" in rv.data

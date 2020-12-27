from flask import url_for


def test_index(client):
    """Test the index route"""
    rv = client.get(url_for("classroom.index"))

    assert rv.status_code == 200
    assert b"DOCTYPE html" in rv.data


def test_get_data(client):
    """Test the get_data route"""
    rv = client.get(url_for("classroom.get_data"))

    assert rv.status_code == 200
    assert isinstance(rv.json["classrooms"], list)


def test_get_occupation(client):
    """Test the get_occupation(id) route"""

    # 2321 is the ID for the Sciences 10; maybe use a "more robust" method
    # to obtain a "test" ID ?
    rv = client.get(url_for("classroom.get_occupation", id=2321))

    assert rv.status_code == 200
    assert isinstance(rv.json["events"], list)

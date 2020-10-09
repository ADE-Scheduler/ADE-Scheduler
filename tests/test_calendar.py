from flask import url_for


def test_index(client):
    """Test the main view"""
    rv = client.get('/')
    assert b'ADE Scheduler' in rv.data


def test_clear(client, app):
    """Test the clear route"""
    assert app.config.get('SESSION_TYPE') == 'redis'


def test_get_data(client):
    """Test the get_data route"""
    assert True


def test_load_schedule(client):
    """Test the load_schedule route"""
    assert True


def test_search_code(client):
    """Test the search_code route"""
    assert True


def test_add_code(client):
    """Test the add_code route"""
    rv = client.get(url_for('calendar.add_code', code='ELME2M'))
    assert 'ELME2M' in rv.json.get('codes')

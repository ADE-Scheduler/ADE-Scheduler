import requests
import backend.ade_api as ade


def test_api(ade_client):
    """Test the connexion to the ADE API."""

    token, expiry = ade.get_token(ade_client.credentials)
    assert token != None

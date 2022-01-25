"""
Provides utils to store and retrieve cookies, as well as a secure mechanism to score oauth tokens in cookies.
"""
import json
from flask import request, current_app as app

from typing import Any, Optional


def set_cookie(key: str, value: str, resp, **kwargs: Any):
    resp.set_cookie(key, value, secure=True, **kwargs)
    return resp


def set_oauth_token(token: dict, resp):

    with app.app_context():

        token = json.dumps(token).encode()
        cookie = app.config["FERNET"].encrypt(token).decode()

        return set_cookie("oauth-token", cookie, resp)


def get_cookie(key: str) -> str:
    cookie = request.cookies.get(key)
    return cookie


def get_oauth_token() -> Optional[dict]:
    cookie = get_cookie("oauth-token")
    if cookie:
        try:
            with app.app_context():
                token = app.config["FERNET"].decrypt(cookie.encode()).decode()
                return json.loads(token)
        except:
            return None
    return None

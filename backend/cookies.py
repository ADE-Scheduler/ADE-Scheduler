"""
Provides utils to store and retrieve cookies, as well as a secure mechanism to score oauth tokens in cookies.
"""

import json
from typing import Any, Optional

from flask import current_app as app
from flask import request


def set_cookie(key: str, value: str, resp, **kwargs: Any):
    resp.set_cookie(key, value, secure=True, **kwargs)
    return resp


def set_oauth_token(token: dict, resp):
    token = json.dumps(token).encode()
    cookie = app.config["FERNET"].encrypt(token).decode()

    return set_cookie("uclouvain-token", cookie, resp)


def get_oauth_token() -> Optional[dict]:
    cookie = request.cookies.get("uclouvain-token")
    if cookie:
        try:
            token = app.config["FERNET"].decrypt(cookie.encode()).decode()
            return json.loads(token)
        except:
            return None
    return None

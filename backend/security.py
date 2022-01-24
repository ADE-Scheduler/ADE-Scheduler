from flask_login import current_user
from flask import make_response
import requests
import json

import backend.models as md


def fetch_token(name):
    return json.loads(requests.cookies.get("uclouvain-token"))
    #return current_user.token.to_token()


def update_token(name, token, refresh_token=None, access_token=None):
    old_token = json.loads(requests.cookies.get("uclouvain-token"))
    if refresh_token:
        old_token["refresh_token"] = token
    elif access_token:
        old_token["access_token"] = token
    else:
        return
    resp = make_response()
    resp = redirect(url_for("calendar.index"))
    resp.set_cookie("uclouvain-token", json.dumps(old_token))
    

from flask_login import current_user
from flask import make_response

import backend.models as md
import backend.cookies as cookies


def fetch_token(name):
    return cookies.get_oauth_token()
    #return current_user.token.to_token()


def update_token(name, token, refresh_token=None, access_token=None, resp=make_response()):
    old_token = fetch_token(name)
    if refresh_token:
        old_token["refresh_token"] = token
    elif access_token:
        old_token["access_token"] = token
    else:
        return
    return cookies.set_oauth_token(old_token, resp)
    

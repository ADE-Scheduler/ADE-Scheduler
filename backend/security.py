from functools import wraps

from flask import abort, make_response, render_template
from flask_login import current_user

import backend.models as md
import backend.cookies as cookies


def fetch_token(name):
    print("Fetching token")
    return cookies.get_oauth_token()
    # return current_user.token.to_token()


def update_token(name, token, resp=None, **kwargs):
    print("CALLING UPDATE", name, token, kwargs)
    token = {**token, **kwargs}

    if resp is None:
        resp = make_response()

        resp = cookies.set_cookie("test", "value", resp)
        return render_template("contact.html")
    resp = cookies.set_oauth_token(token, resp)
    return resp


def roles_required(*roles):
    """
    Decorator which specifies that a user must have all the specified roles to access a view.
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            for role in roles:
                if not current_user.has_role(role):
                    abort(403)
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper

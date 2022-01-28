from functools import wraps

from flask import abort, make_response, render_template, g
from flask_login import current_user

import backend.models as md
import backend.cookies as cookies


def fetch_token(name):
    # Fetch token
    token = cookies.get_oauth_token()

    # If None (e.g. user has cleared his cookies), ask for a re-login
    # How to manage this ?
    if token is None:
        pass
    return token


def update_token(name, token, refresh_token=None, access_token=None):
    g.token = token


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

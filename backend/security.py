from functools import wraps

from flask import abort, g, make_response, redirect, request, session, url_for
from flask_login import current_user

import backend.cookies as cookies
import backend.models as md


def fetch_token(name):
    # Fetch token
    token = cookies.get_oauth_token()

    # If None (e.g. user has cleared his cookies), ask for a re-login
    if token is None:
        session["next"] = request.full_path
        abort(make_response(redirect(url_for("security.login"))))

    return token


def update_token(name, token, refresh_token=None, access_token=None):
    # The token update is handled in the `after_request` hook
    # (since we do not have access to the response here).
    # Thus, the token is temporarily stored in Flask's app context `g`.
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

from functools import wraps

from flask import abort
from flask_login import current_user

import backend.models as md


def fetch_token(name):
    return current_user.token.to_token()


def update_token(name, token, refresh_token=None, access_token=None):
    if refresh_token:
        item = md.OAuth2Token.query.filter_by(
            name=name, refresh_token=refresh_token
        ).first()
    elif access_token:
        item = md.OAuth2Token.query.filter_by(
            name=name, access_token=access_token
        ).first()
    else:
        return
    item.update(token)


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

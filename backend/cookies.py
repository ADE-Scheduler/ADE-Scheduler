from authlib.jose import jwt
from flask import request, current_app as app


def set_cookie(key, value, resp, **kwargs):
    resp.set_cookie(key, value, secure=True, **kwargs)
    return resp


def set_oauth_token(token, resp):

    with app.app_context():

        payload = {"oauth-token": token}
        header = {"alg": "HS256"}
        cookie = jwt.encode(header, payload, app.config["SECRET_KEY"]).decode()

        return set_cookie("oauth-token", cookie, resp)


def get_cookie(key):
    cookie = request.cookies.get(key)
    return cookie


def get_oauth_token():
    cookie = get_cookie("oauth-token")
    if cookie:
        try:
            with app.app_context():
                claims = jwt.decode(cookie, app.config["SECRET_KEY"])
                return claims["oauth-token"]
        except:
            return None
    return None

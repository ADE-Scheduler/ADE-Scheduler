import backend.cookies as cookies
from flask import make_response, render_template


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

import backend.cookies as cookies


def fetch_token(name):
    return cookies.get_oauth_token()
    # return current_user.token.to_token()


def update_token(name, token, refresh_token=None, access_token=None, resp=None):
    old_token = fetch_token(name)
    if refresh_token:
        old_token["refresh_token"] = token
    elif access_token:
        old_token["access_token"] = token
    else:
        return

    if resp:
        return cookies.set_oauth_token(old_token, resp)

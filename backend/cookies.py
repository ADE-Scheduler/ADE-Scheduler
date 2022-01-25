import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import requests
from flask import current_app as app


password = app.config["SECRET_KEY"] 
salt = app.config["SALT"]
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=390000,
)
key = base64.urlsafe_b64encode(kdf.derive(password))
f = Fernet(key)


def set_cookie(key, value, resp, **kwargs):
    value = f.encrypt(value)
    resp.set_cookie(key, value, secure=True, **kwargs)
    return resp

def set_oauth_token(token, resp):
    cookie = f.encrypt(json.dumps(token).encode())
    return set_cookie("oauth-token", cookie, resp)

def get_cookie(key):
    cookie = requests.cookies.get(key, None)
    return cookie

def get_oauth_token():
    cookie = get_cookie("oauth-token")
    if cookie:
        try:
            token = json.loads(f.decrypt(cookie).decode())
            return token
        except:
            return None
    return None

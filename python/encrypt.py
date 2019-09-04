from cryptography.fernet import Fernet
import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class LoginAlreadyExistsError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LoginDoesNotExistsError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WrongPasswordError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def get_key(password):
    salt = b'no_salt_plz_dont_hack_us'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def generate_link(username, password):
    key = get_key(password)
    f = Fernet(key)
    return f.encrypt(username.encode()).decode()


def check_id(username, password, link):
    key = get_key(password)
    f = Fernet(key)
    try: return f.decrypt(link.encode()) == username.encode()
    except: return False

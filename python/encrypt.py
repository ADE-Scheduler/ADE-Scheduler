from cryptography.fernet import Fernet
import base64
import os
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logins = set() # {login hashed}
memory = dict() # {links : settings} where links = login encrypted with password

class LoginAlreadyExistsError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class LoginDoesNotExistsError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class WrongPasswordError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def key_from_password(password):
    password_b = password.encode()
    salt = b'salt_'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_b))
    return key

def hashString(string):
    #Le hash est different a chaque session donc faut trouver quelque chose de constant et qui permette juste
    #de rendre le string illisible
    #return hashlib.sha256(string.encode()).hexdigest()
    return string

def getSettings(link):
    return memory[link]

def getLink(login, password):
    login_hashed = hashString(login)

    if login_hashed not in logins:
        raise LoginDoesNotExistsError()
    
    login_b = login.encode()

    key = key_from_password(password)
    f = Fernet(key)

    link = f.encrypt(login_b)

    print('link = ', link)

    if link in memory.keys():
        return link
    else:
        raise WrongPasswordError()

def makeLink(login, password, settings=None):
    login_hashed = hashString(login)

    if login_hashed in logins:
        raise LoginAlreadyExistsError()
    else:
        logins.add(login_hashed)
    
    login_b = login.encode()

    key = key_from_password(password)
    f = Fernet(key)

    link = f.encrypt(login_b)

    memory[link] = settings

    return link

login = 'nom_utilisateur'
password = "mot_de_passe" # le mdp de l'utilisateur
settings = 'Gilles est vraiment beau comme un bateau'
print(login, password, settings)

link = makeLink(login, password, settings)

print('Dicts :\n', logins, '\n', memory)

print('Test 1.')
print('\tlink :', link)
print('\tgetLink(login, password) :', getLink(login, password))
print('\t-->link == getLink(...) :', link == getLink(login, password))

print('Test 2.')
print('\tsettings :', settings)
print('\tmemory[link] :', memory[link])
print('\t-->settings == getSettings(link) :', settings == getSettings(link))

print('Test 3.')
print('\tCalling makeLink(...) with same login but different password')
makeLink(login, 'password_bis', settings)
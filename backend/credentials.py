import os
import json
import warnings


class CredentialsEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, bytes):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class CredentialsDecoder(json.JSONDecoder):

    def decode(self, obj):
        decoded = json.JSONDecoder().decode(obj)

        for key in decoded:
            obj = decoded[key]
            if isinstance(obj, list) and isinstance(obj[0], int):
                decoded[key] = bytes(obj)
        return decoded


class Credentials:
    ADE_API_CREDENTIALS = "ADE_API_CREDENTIALS"
    GMAIL_CREDENTIALS = "GMAIL_CREDENTIALS"

    def __init__(self, **kwargs):
        self.credentials = kwargs

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.credentials, f, cls=CredentialsEncoder)

    @staticmethod
    def set_credentials(filename, credentials_name):
        os.environ[credentials_name] = filename
        venv = os.path.join(os.path.abspath(os.curdir), "venv/bin/activate")
        warnings.warn("\nWarning, Python cannot set environment variables permanently!\n"
                      "In order to make this change persistent, type in a terminal:\n"
                      f"[UNIX]:\n"
                      f"\techo \"export {credentials_name}=\\\"{filename}\\\"\">> ~/.bashrc \n"
                      f"[UNIX + Python in Virtual env. @ /venv]:\n"
                      f"\techo \"export {credentials_name}=\\\"{filename}\\\"\">> {venv} \n"
                      )

    @staticmethod
    def get_credentials(credentials_name):
        with open(os.environ[credentials_name], 'r') as f:
            return json.load(f, cls=CredentialsDecoder)

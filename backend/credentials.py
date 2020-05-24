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
    ENV_VAR_CREDENTIALS = "ADE_API_CREDENTIALS"

    def __init__(self, **kwargs):
        self.credentials = kwargs

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.credentials, f, cls=CredentialsEncoder)

    @staticmethod
    def set_credentials(filename):
        os.environ[Credentials.ENV_VAR_CREDENTIALS] = filename
        venv = os.path.join(os.path.abspath(os.curdir), "venv/bin/activate")
        warnings.warn("\nWarning, Python cannot set environment variables permanently!\n"
                      "In order to make this change persistent, type in a terminal:\n"
                      f"[UNIX]:\n"
                      f"\techo \"export {Credentials.ENV_VAR_CREDENTIALS}=\\\"{filename}\\\"\">> ~/.bashrc \n"
                      f"[UNIX + Python in Virtual env. @ /venv]:\n"
                      f"\techo \"export {Credentials.ENV_VAR_CREDENTIALS}=\\\"{filename}\\\"\">> {venv} \n"
                      )

    @staticmethod
    def get_credentials():
        with open(os.environ[Credentials.ENV_VAR_CREDENTIALS], 'r') as f:
            return json.load(f, cls=CredentialsDecoder)


if __name__ == "__main__":

    test = {
        "key": bytes(10),
        "user": "charles"
    }

    filename = "/home/jerome/ade_api.json"
    Credentials.set_credentials(filename)
    cred = Credentials.get_credentials()
    print(cred)

    c = Credentials(**test)
    c.save("/home/jerome/Desktop/mdr.json")

    #print(CredentialsEncoder().encode(bytes(10)))

    #print(json.loads("{1: [1]}", cls=CredentialsDecoder))

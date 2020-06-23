import os
import json
import warnings
from typing import Any

ADE_API_CREDENTIALS = "ADE_API_CREDENTIALS"
GMAIL_CREDENTIALS = "GMAIL_CREDENTIALS"


class CredentialsEncoder(json.JSONEncoder):

    def default(self, obj: Any) -> Any:
        if isinstance(obj, bytes):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class CredentialsDecoder(json.JSONDecoder):

    def decode(self, obj: Any, w: Any = None) -> str:
        decoded = json.JSONDecoder().decode(obj)

        for key in decoded:
            obj = decoded[key]
            if isinstance(obj, list) and isinstance(obj[0], int):
                decoded[key] = bytes(obj)
        return decoded


def set_credentials(filename: str, credentials_name: str):
    """
    Set a environment variable to link toward credentials file.
    :param filename: path with .json extension
    :param credentials_name: the environment variable as a string
    :return: /
    """
    os.environ[credentials_name] = filename
    venv = "venv/bin/activate"
    warnings.warn("\nWarning, Python cannot set environment variables permanently!\n"
                  "In order to make this change persistent, type in a terminal:\n"
                  f"[UNIX]:\n"
                  f"\techo \"export {credentials_name}=\\\"{filename}\\\"\">> ~/.bashrc \n"
                  f"[UNIX + Python in Virtual env. @ /venv]:\n"
                  f"\techo \"export {credentials_name}=\\\"{filename}\\\"\">> {venv} \n"
                  )


def get_credentials(credentials_name: str) -> 'Credentials':
    """
    Reads a credentials file from environment variable and returns the credentials in it.
    lists of ints are converted into lists of bytes.
    :param credentials_name: the environment variable as a string
    :return: a dict of credentials
    """
    with open(os.environ[credentials_name], 'r') as f:
        return Credentials(**json.load(f, cls=CredentialsDecoder))


class Credentials:

    def __init__(self, **kwargs: Any):
        """
        Class which stores credentials.
        :param kwargs: dict of credentials
        """
        self.credentials = kwargs

    def save(self, filename: str) -> None:
        """
        Save current credentials into a json file.
        bytes are converted into list of ints.
        :param filename: path with .json extension
        :return: /
        """
        with open(filename, 'w') as f:
            json.dump(self.credentials, f, cls=CredentialsEncoder)

    def __str__(self) -> str:
        return f"Credentials: {self.credentials}"

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, item: str) -> Any:
        return self.credentials[item]


if __name__ == "__main__":

    # How to use credentials :

    # First put the two files anywhere but in this repo
    # Second, link the environment variables once per run

    filename = "/home/jerome/ade_api.json"

    set_credentials(filename, ADE_API_CREDENTIALS)

    filename = "/home/jerome/as_gmail.json"

    set_credentials(filename, GMAIL_CREDENTIALS)

    # Call this function any time you want to retrieve the credentials

    credentials = get_credentials(ADE_API_CREDENTIALS)


    print(credentials)

    print(credentials["secret_key"])
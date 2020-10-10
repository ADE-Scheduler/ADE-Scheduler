import os
import sys
import pytest
from dotenv import load_dotenv, find_dotenv

sys.path.append(os.getcwd())
load_dotenv(find_dotenv(".flaskenv"))

from app import app as ade_scheduler
import backend.ade_api as ade


@pytest.fixture
def app():
    return ade_scheduler


@pytest.fixture
def ade_client():
    return ade.Client(
        dict(
            user=os.environ["ADE_USER"],
            password=os.environ["ADE_PASSWORD"],
            secret_key=os.environ["ADE_SECRET_KEY"],
            url=os.environ["ADE_URL"],
            data=os.environ["ADE_DATA"],
            Authorization=os.environ["ADE_AUTHORIZATION"],
        )
    )

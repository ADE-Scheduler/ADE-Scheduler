import pytest
from app import app as ade_scheduler


@pytest.fixture
def app():
    return ade_scheduler

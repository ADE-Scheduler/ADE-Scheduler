from datetime import datetime

from backend.events import TZ, EventCM
from backend.professors import Professor


def make_event(professor: str, note: str) -> EventCM:
    return EventCM(
        name="LEPL1101",
        begin=TZ.localize(datetime(2024, 9, 16, 8, 30)),
        end=TZ.localize(datetime(2024, 9, 16, 10, 30)),
        professor=Professor(professor),
        code="LEPL1101",
        event_code="LEPL1101-Q1",
        note=note,
    )


def test_json_professor_and_note():
    event = make_event("Doe John", "Room change").json()

    assert event["professor"] == "Doe John"
    assert event["note"] == "Room change"


def test_json_note_without_professor():
    event = make_event("", "Room change").json()

    # The description drops the empty professor line: the note takes its place
    assert event["description"].splitlines()[2] == "Room change"
    assert event["professor"] == ""
    assert event["note"] == "Room change"


def test_json_event_cached_before_professor():
    event = make_event("Doe John", "")
    del event.professor  # As unpickled from a cache older than the attribute

    assert event.json()["professor"] == ""

"""
To initialise the database's tables:

>>> from app import app
>>> from backend.models import db
>>> with app.app_context(): db.create_all()
"""


from backend.models import db, User, Schedule, Link, Property


def get_user_from_mail(email):
    return User.query.filter(User.email == email).first()


def create_schedule(user_id, data):
    """
    Set a schedule with creator rights.
    """
    schedule = Schedule(data=data)
    db.session.add(schedule)
    db.session.commit()

    ownership = Property(user_id=user_id, schedule_id=schedule.id, level=0)  # TODO definir les level d'ownership
    db.session.add(ownership)
    db.session.commit()


def update_schedule(id, data):
    """
    Modifies this schedule's data
    """
    Schedule.query.filter(Schedule.id == id).update(dict(data=data))
    db.session.commit()


def get_schedule(user_id=None, schedule_id=None):
    """
    Get a schedule.
    user_id specified => return all of this user's schedules
    schedule_id specified => return this schedule
    """
    if user_id:
        return Property.query.filter(Property.user_id == user_id).all()
    if schedule_id:
        return Schedule.query.filter(Schedule.id == schedule_id).all()
    return list()

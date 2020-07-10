"""
To initialise the database's tables:

>>> from app import app
>>> from backend.models import db
>>> with app.app_context(): db.create_all()
"""


from backend.models import db, User, Schedule, Link, Property


def get_user_from_mail(email):
    return User.query.filter(User.email == email).first()

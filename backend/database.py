"""
To initialise the database's tables:

>>> from app import app
>>> from backend.models import db
>>> with app.app_context(): db.create_all()
"""


import backend.models as md


def get_user_from_mail(email):
    return md.User.query.filter(md.User.email == email).all()

import secrets

from copy import copy
from flask_sqlalchemy import SQLAlchemy
from flask_security.models import fsqla_v2 as fsqla

db = SQLAlchemy()
fsqla.FsModels.set_db_info(db)

# TODO: @Louis faut vérifier que tout marche bien et puis bien commenter la docstring :)

class ScheduleDoNotMatchError(Exception):
    """
    Exception that will occur if a user tries to update a schedule's data with a non-matching ID.
    """
    def __str__(self):
        return 'The schedule ID does not match the given data\'s ID'


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    schedules = db.relationship('Schedule', secondary='property')

    def add_schedule(self, schedule, level=0):
        if schedule not in self.schedules:
            property = Property(user_id=self.id, schedule_id=schedule.id, level=level)
            self.property.append(property)
            self.schedules.append(schedule)
            db.session.commit()

    def remove_schedule(self, schedule):
        if schedule in self.schedules:
            self.schedules.remove(schedule)
            db.session.commit()

    def get_schedule(self, id=None, level=None):
        if id is not None:          # Return the schedule matching the requested ID (if any)
            for schedule in self.schedules:
                if schedule.id == id:
                    return schedule
            return None

        elif level is not None:     # Return the schedules matching the ownership level
            return list(map(lambda y: y.schedule, filter(lambda x: x.level == level, self.property)))

        else:
            return self.schedules   # Return all of this user's schedules


class Schedule(db.Model):
    """
    Table used to store Schedules in the database.
    """
    __tablename__ = 'schedule'
    id = db.Column(db.Integer(), primary_key=True)
    data = db.Column(db.PickleType())
    users = db.relationship('User', secondary='property')
    link = db.relationship('Link', uselist=False, backref='schedule')

    def __init__(self, data, user=None):
        """
        Creates a schedule, binds it to its creator if any.
        """
        # Schedule creation, update id
        if user is not None:
            self.users = [user]
        db.session.add(self)
        db.session.flush()
        data.id = self.id
        self.data = data

        # Automatic link creation
        Link(self)
        db.session.commit()

    def update_data(self, data):
        """
        Warning: the address of data must be different that of self.data
        For example:
        >>> data = schedule.data
        >>> data.label = "new_label"
        >>> schedule.update(data)
        ... does not work ! Instead, do:
        >>> data = copy(schedule.data)
        >>> data.label = "new_label"
        >>> schedule.update(data)
        For more information, see: https://docs.sqlalchemy.org/en/13/orm/extensions/mutable.html
        """
        if data.id is not self.id:
            raise ScheduleDoNotMatchError
        self.data = data
        db.session.commit()

    def update_label(self, label):
        data = copy(self.data)
        data.label = label
        self.data = data
        db.session.commit()

    def get_link(self):
        if self.link is None:
            Link(self)
        return self.link


class Link(db.Model):
    __tablename__ = 'link'
    id = db.Column(db.Integer(), primary_key=True)
    schedule_id = db.Column(db.Integer(), db.ForeignKey('schedule.id'))
    link = db.Column(db.String(100), unique=True, index=True)
    choice = db.Column(db.Integer(), default=0)

    def __init__(self, schedule):
        """
        Creates a link, binds it to a schedule
        """
        generated_link = secrets.token_urlsafe(32)
        while Link.query.filter(Link.link == generated_link).first():
            generated_link = secrets.token_urlsafe(32)
        self.link = generated_link
        self.schedule = schedule
        db.session.add(self)
        db.session.commit()


class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    schedule_id = db.Column(db.Integer(), db.ForeignKey('schedule.id'))
    level = db.Column(db.Integer(), default=0)

    user = db.relationship('User', backref=db.backref('property', cascade="all, delete-orphan"))
    schedule = db.relationship('Schedule', backref=db.backref('property', cascade="all, delete-orphan"))

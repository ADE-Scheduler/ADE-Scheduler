import secrets

from copy import copy
from flask_sqlalchemy import SQLAlchemy
from flask_security.models import fsqla_v2 as fsqla

OWNER_LEVEL = 0
EDITOR_LEVEL = 1
VIEWER_LEVEL = 2

db = SQLAlchemy()
fsqla.FsModels.set_db_info(db)


class LevelAccessDenied(Exception):

    def __str__(self):
        return 'The level access you used is not permitted for this function.'


class ScheduleDoNotMatchError(Exception):
    """
    Exception that will occur if a user tries to update a schedule's data with a non-matching ID.
    """

    def __init__(self, database_id, data_id):
        self.database_id = database_id
        self.data_id = data_id

    def __str__(self):
        return f'The schedule ID\'s do not match: database ID is {self.database_id} and given data ID is {self.data_id}.'


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    schedules = db.relationship('Schedule', secondary='property')

    def add_schedule(self, schedule, level=OWNER_LEVEL):
        if schedule not in self.schedules:
            self.schedules.append(schedule)
            if level is not OWNER_LEVEL:
                schedule.property[-1].level = level
            db.session.commit()

    def remove_schedule(self, schedule: 'Schedule'):
        """
        Removes a schedule from the schedules list.
        If user owns this schedule, deletes the schedule for all users.

        :param schedule: the schedule
        :type schedule: Schedule
        """
        if schedule in self.schedules:
            self.schedules.remove(schedule)
            db.session.commit()

    def share_schedule_with_emails(self, schedule, *emails: str, level=EDITOR_LEVEL):

        if level == OWNER_LEVEL:
            raise LevelAccessDenied

        emails = [email for email in emails if email != self.email]  # You should not add yourself as editor or viewer
        users = User.query.filter(User.email.in_(emails)).all()

        for user in users:
            user.add_schedule(schedule, level=level)

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
        if int(data.id) != int(self.id):
            raise ScheduleDoNotMatchError(self.id, data.id)
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
    level = db.Column(db.Integer(), default=OWNER_LEVEL)

    user = db.relationship('User', backref=db.backref('property', cascade="all, delete-orphan"))
    schedule = db.relationship('Schedule', backref=db.backref('property', cascade="all, delete-orphan"))


class Usage(db.Model):
    __tablename__ = 'flask_usage'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512))
    ua_browser = db.Column(db.String(16))
    ua_language = db.Column(db.String(16))
    ua_platform = db.Column(db.String(16))
    ua_version = db.Column(db.String(16))
    blueprint = db.Column(db.String(16))
    view_args = db.Column(db.String(64))
    status = db.Column(db.Integer)
    remote_addr = db.Column(db.String(24))
    xforwardedfor = db.Column(db.String(64))
    authorization = db.Column(db.Boolean)
    ip_info = db.Column(db.String(1024))
    path = db.Column(db.String(256))
    speed = db.Column(db.Float)
    datetime = db.Column(db.DateTime)
    username = db.Column(db.String(128))
    track_var = db.Column(db.String(256))

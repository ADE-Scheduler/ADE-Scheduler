from flask_sqlalchemy import SQLAlchemy
from flask_security.models import fsqla_v2 as fsqla

db = SQLAlchemy()
fsqla.FsModels.set_db_info(db)


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

    def __init__(self, data, user):
        """
        Creates a schedule, binds it to its creator.
        """
        self.users = [user]
        db.session.add(self)
        db.session.flush()

        data.id = self.id
        self.data = data
        db.session.commit()

    def update_data(self, data):
        if data.id is not self.id:
            raise ScheduleDoNotMatchError
        self.data = data
        db.session.commit()

    def get_link():
        if self.link is None:
            Link(self)
        return self.link


class Link(db.Model):
    __tablename__ = 'link'
    id = db.Column(db.Integer(), primary_key=True)
    schedule_id = db.Column(db.Integer(), db.ForeignKey('schedule.id'))
    link = db.Column(db.String(100), unique=True, index=True)  # TODO: change the length of the link ?

    def __init__(self, schedule):
        """
        Creates a link, binds it to a schedule
        """
        self.link = 'link-generator.ade-scheduler.me'   # TODO: a link generator
        self.schedule = schedule
        db.session.add(self)
        db.session.commit()

    def get_schedule():
        return self.schedule


class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    schedule_id = db.Column(db.Integer(), db.ForeignKey('schedule.id'))
    level = db.Column(db.Integer(), default=0)

    user = db.relationship('User', backref=db.backref('property', cascade="all, delete-orphan"))
    schedule = db.relationship('Schedule', backref=db.backref('property', cascade="all, delete-orphan"))

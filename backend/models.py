from flask_sqlalchemy import SQLAlchemy
from flask_security.models import fsqla_v2 as fsqla
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()
fsqla.FsModels.set_db_info(db)



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

    def get_schedules(self, level=None):
        if level is not None:
            return list(map(lambda y: y.schedule, filter(lambda x: x.level == level, self.property)))
        else:
            return self.schedules


class Schedule(db.Model):
    """
    Schedule data format:
    {
    code_list: [LMECA2660, LELEC2760, etc],             // requested course codes
    filtered_subcodes: [LELEC2760_Q1, LMECA2660_Q2],    // unselected subcodes
    computed_subcode: [[code1, code2], ..., [code2, code4]]   // filtered subcodes, week by week
    custom_events: [{event1}, {event2}],                // custom user events
    priority_levels: {code1: 5, code2: 1, subcode1: 3}, // priority level of the various code & subcodes
    project_id: id,
    schedule_id: id,
    }
    """
    __tablename__ = 'schedule'
    id = db.Column(db.Integer(), primary_key=True)
    data = db.Column(db.JSON())
    label = db.Column(db.String(100))
    users = db.relationship('User', secondary='property')
    link = db.relationship('Link', uselist=False, backref='schedule')

    def __init__(self, label, data, user):
        """
        Creates a schedule, binds it to its creator.
        """
        self.label = label
        self.data = data
        self.users = [user]
        db.session.add(self)
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

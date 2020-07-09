from flask_sqlalchemy import SQLAlchemy
from flask_security.models import fsqla_v2 as fsqla

db = SQLAlchemy()
fsqla.FsModels.set_db_info(db)



class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    pass


class Schedule(db.Model):
    """
    Schedule data format:
    {
        code_list: [LMECA2660, LELEC2760, etc],             // requested course codes
        filtered_subcodes: [LELEC2760_Q1, LMECA2660_Q2],    // unselected subcodes
        custom_events: [{event1: ...}, {event2: ...}],      // custom user events
        priority_levels: {code1: 5, code2: 1, subcode1: 3}, // priority level of the various code & subcodes
        project_id: id,
        schedule_id: id,
    }
    """
    __tablename__ = 'schedule'
    id = db.Column(db.Integer(), primary_key=True)
    data = db.Column(db.JSON())


class Link(db.Model):
    __tablename__ = 'link'
    id = db.Column(db.Integer(), db.ForeignKey('schedule.id'), primary_key=True)
    link = db.Column(db.String(100), unique=True, index=True)  # TODO: change the length of the link ?


class Property(db.Model):
    __tablename__ = 'property'
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
    schedule_id = db.Column(db.Integer(), db.ForeignKey('schedule.id'), primary_key=True)
    level = db.Column(db.Integer())  # TODO: constrain the values (0 -> 2)

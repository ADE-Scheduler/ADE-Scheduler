from backend.database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, JSON


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    email = Column(String(120), index=True, unique=True)
    password = Column(String(128))
    active = Column(Boolean())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Schedule(UserMixin, Base):
    __tablename__ = 'schedule'
    id = Column(Integer(), primary_key=True)
    data = Column(JSON())
    link = Column(String(100))  # TODO: change the length of the link ?


class Property(UserMixin, Base):
    __tablename__ = 'property'
    user_id = Column(Integer(), ForeignKey('user.id'), primary_key=True)
    schedule_id = Column(Integer(), ForeignKey('schedule.id'), primary_key=True)
    level = Column(Integer())  # TODO: constrain the values (0 -> 2)
    
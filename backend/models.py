from backend.database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, String, ForeignKey, JSON


# Dummy tables for Flask-Security
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


# User table
class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(255))
    password = Column(String(255))
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255))
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return '<User {}>'.format(self.email)


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer(), primary_key=True)
    data = Column(JSON())


class Link(Base):
    __tablename__ = 'link'
    id = Column(Integer(), ForeignKey('schedule.id'), primary_key=True)
    link = Column(String(100), unique=True, index=True)  # TODO: change the length of the link ?


class Property(Base):
    __tablename__ = 'property'
    user_id = Column(Integer(), ForeignKey('user.id'), primary_key=True)
    schedule_id = Column(Integer(), ForeignKey('schedule.id'), primary_key=True)
    level = Column(Integer())  # TODO: constrain the values (0 -> 2)


######################
# API for the models #
######################

def get_user_from_email(email: String) -> List[User]:
    return User.query.filter(User.email == email).one()

def get_schedule_from_link(link):
    pass
import datetime
import json
import secrets
import time
import uuid
from copy import copy
from typing import Any, Union

import pandas as pd
import sqlalchemy as sa
from flask_sqlalchemy import BaseQuery, SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy.types import CHAR, TypeDecorator

import backend.mixins as mxn

OWNER_LEVEL = 0
EDITOR_LEVEL = 1
VIEWER_LEVEL = 2

db = SQLAlchemy()


def query_to_dataframe(query: BaseQuery, *args: Any, **kwargs: Any) -> pd.DataFrame:
    """
    Parses a SQL query from the database into a dataframe.

    :param query: the query to be read
    :type query: BaseQuery
    :param args: positional arguments to be passed to :func:`pandas.read_sql`
    :type args: Any
    :param kwargs: keyword arguments to be passed to :func:`pandas.read_sql`
    :type kwargs: Any
    :return: a dataframe of table
    :rtype: pd.DataFrame
    """
    return pd.read_sql(query.statement, query.session.bind, *args, **kwargs)


def table_to_dataframe(table: db.Model, *args: Any, **kwargs: Any) -> pd.DataFrame:
    """
    Parses a table from the database into a dataframe.

    :param table: the table to be parsed
    :type table: db.Model
    :param args: positional arguments to be passed to :func:`pandas.read_sql`
    :type args: Any
    :param kwargs: keyword arguments to be passed to :func:`pandas.read_sql`
    :type kwargs: Any
    :return: a dataframe of table
    :rtype: pd.DataFrame
    """
    return pd.read_sql(table.__tablename__, table.query.session.bind, *args, **kwargs)


def reformat_status_in_dataframe(df: pd.DataFrame):
    """
    Modifies in-place a dataframe in order to replace status (int) to
    status (str) with format 2XX, 4XX, 5XX, etc.

    :param df: the dataframe containing a status column
    :type df: pd.DataFrame
    """
    df.status = df.status.astype(str).str.replace(
        r"([0-9])[0-9][0-9]", r"\1XX", regex=True
    )


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(
        self, value: Union[None, uuid.UUID, str], dialect
    ) -> Union[None, str]:
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(value)
            else:
                # hexstring
                return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class LevelAccessDenied(Exception):
    def __str__(self):
        return "The level access you used is not permitted for this function."


class ScheduleDoNotMatchError(Exception):
    """
    Exception that will occur if a user tries to update a schedule's data with a non-matching ID.
    """

    def __init__(self, database_id, data_id):
        self.database_id = database_id
        self.data_id = data_id

    def __str__(self):
        return f"The schedule ID's do not match: database ID is {self.database_id} and given data ID is {self.data_id}."


# Roles <-> Users m2m relationship
roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


# Schedules <-> Users m2m relationship
schedules_users = db.Table(
    "schedules_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("schedule_id", db.Integer(), db.ForeignKey("schedule.id")),
)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


class User(mxn.UserMixin, db.Model):
    __tablename__ = "user"
    # Basic user info
    id = db.Column(db.Integer, primary_key=True)
    fgs = db.Column(db.String(8), unique=True, nullable=False)  # The user identifier
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))

    # Track login
    created_at = db.Column(db.DateTime())
    last_seen_at = db.Column(db.DateTime())

    # Schedules
    autosave = db.Column(
        db.Boolean(),
        nullable=False,
        default=True,
        server_default=sa.sql.expression.literal(True),
    )
    last_schedule_id = db.Column(db.Integer(), nullable=True)
    schedules = db.relationship(
        "Schedule",
        secondary=schedules_users,
        backref=db.backref("users"),
    )

    # Roles
    roles = db.relationship(
        "Role",
        secondary=roles_users,
        backref=db.backref("users"),
    )

    def get_id(self):
        """Returns the user's identification attribute"""
        return self.fgs

    def add_schedule(self, schedule, level=OWNER_LEVEL):
        if schedule not in self.schedules:
            self.schedules.append(schedule)
            if level is not OWNER_LEVEL:
                schedule.property[-1].level = level
            db.session.commit()

    def remove_schedule(self, schedule: "Schedule"):
        """
        Removes a schedule from the schedules list.
        If user owns this schedule, deletes the schedule for all users.

        :param schedule: the schedule
        """
        if schedule in self.schedules:
            self.schedules.remove(schedule)
            db.session.commit()

    def share_schedule_with_emails(self, schedule, *emails: str, level=EDITOR_LEVEL):
        if level == OWNER_LEVEL:
            raise LevelAccessDenied

        emails = [
            email for email in emails if email != self.email
        ]  # You should not add yourself as editor or viewer
        users = User.query.filter(User.email.in_(emails)).all()

        for user in users:
            user.add_schedule(schedule, level=level)

    def get_schedule(self, id):
        """
        Return the schedule in this user's schedule list matching the given ID.
        None if no match is found.
        """
        if id is not None:
            for schedule in self.schedules:
                if int(schedule.id) == int(id):
                    return schedule
            return None
        else:
            return None

    def get_schedules(self):
        """
        Equivalent to User.schedules, but sorts the schedules according to their IDs
        to ensure similar behavior throughout the SQL databases.
        """
        return sorted(self.schedules, key=lambda e: int(e.id))

    def set_autosave(self, autosave):
        self.autosave = autosave
        db.session.commit()

    def set_last_schedule_id(self, schedule_id):
        self.last_schedule_id = schedule_id
        db.session.commit()

    @classmethod
    def get_emails(cls):
        return table_to_dataframe(cls, columns=["email"]).tolist()


class Schedule(db.Model):
    """
    Table used to store Schedules in the database.
    """

    __tablename__ = "schedule"
    id = db.Column(db.Integer(), primary_key=True)
    last_modified_by = db.Column(GUID(), nullable=True)
    data = db.Column(db.PickleType())
    link = db.relationship("Link", uselist=False, backref="schedule")

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
        self.data = copy(data)
        db.session.commit()

    def update_label(self, label):
        self.data.label = label
        self.update_data(self.data)
        db.session.commit()

    def get_link(self):
        if self.link is None:
            Link(self)
        return self.link

    def update_last_modified_by(self, uuid):
        self.last_modified_by = uuid
        db.session.commit()


class Link(db.Model):
    __tablename__ = "link"
    id = db.Column(db.Integer(), primary_key=True)
    schedule_id = db.Column(db.Integer(), db.ForeignKey("schedule.id"))
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


class Usage(db.Model):
    __tablename__ = "flask_usage"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512))
    ua_browser = db.Column(db.String(16))
    ua_language = db.Column(db.String(16))
    ua_platform = db.Column(db.String(16))
    ua_version = db.Column(db.String(16))
    blueprint = db.Column(db.String(16))
    path = db.Column(db.String(256))
    endpoint = db.Column(db.String(64))
    view_args = db.Column(db.String(64))
    url_args = db.Column(db.String(512))
    status = db.Column(db.Integer)
    remote_addr = db.Column(db.String(24))
    speed = db.Column(db.Float)
    datetime = db.Column(db.DateTime)
    username = db.Column(db.String(128))
    track_var = db.Column(db.String(256))

    def __init__(self, data):
        user_agent = data["user_agent"]

        self.url = data["url"]
        self.ua_browser = user_agent.browser
        self.ua_language = user_agent.language
        self.ua_platform = user_agent.platform
        self.ua_version = user_agent.version
        self.blueprint = data["blueprint"]
        self.path = data["path"]
        self.endpoint = data["endpoint"]
        self.view_args = json.dumps(data["view_args"], ensure_ascii=False)[:64]
        self.url_args = json.dumps(data["url_args"], ensure_ascii=False)[:512]
        self.status = data["status"]
        self.remote_addr = data["remote_addr"]
        self.speed = data["speed"]
        self.datetime = data["datetime"]
        self.username = data["username"]
        self.track_var = json.dumps(data["track_var"], ensure_ascii=False)

        db.session.add(self)
        db.session.commit()  # For some obscures reason, this make the tests fail...

    @validates("url", "ua_browser", "ua_language", "ua_platform", "ua_version")
    def truncate_string(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


class ApiUsage(db.Model):
    __tablename__ = "api_usage"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))
    speed = db.Column(db.Float)
    status = db.Column(db.Integer)
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, url, response):
        """
        Logs one request made to the API.
        """
        self.url = url
        self.speed = response.elapsed.total_seconds()
        self.status = response.status_code
        db.session.add(self)
        db.session.commit()


"""
This old user class is just there to handle migration from the old login system
to the new one, ensuring old account data can be trasnferred to the new accounts.
"""
old_schedules_users = db.Table(
    "old_schedules_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("old_user.id")),
    db.Column("schedule_id", db.Integer(), db.ForeignKey("schedule.id")),
)


class OldUser(mxn.UserMixin, db.Model):
    __tablename__ = "old_user"
    # FLASK-SECUIRTY'S ATTRIBUTES (we only need those, the others can be dropped)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    confirmed_at = db.Column(db.DateTime())

    # ADE-SCHEDULER ATTRIBUTES
    autosave = db.Column(
        db.Boolean(),
        nullable=False,
        default=False,
        server_default=sa.sql.expression.literal(False),
    )
    last_schedule_id = db.Column(db.Integer(), nullable=True)
    schedules = db.relationship(
        "Schedule",
        secondary=old_schedules_users,
        backref=db.backref("old_users"),
    )

    @property
    def is_active(self):
        return self.confirmed_at is not None

    @classmethod
    def get_emails(cls):
        df = table_to_dataframe(cls, columns=["confirmed_at", "email"])
        df.dropna(subset=["confirmed_at"], inplace=True)

        return df.email.values.tolist()


class ExternalCalendar(db.Model):
    __tablename__ = "external_calendar"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128))
    name = db.Column(db.String(128))
    url = db.Column(db.String(512))
    description = db.Column(db.String(4096))
    user_id = db.Column(db.Integer())
    approved = db.Column(db.Boolean())

    def __init__(self, code, name, url, description, user, approved=False):
        self.code = code
        self.name = name
        self.url = url
        self.description = description
        self.user_id = user.id
        self.approved = approved

        db.session.add(self)
        db.session.commit()

    def update_url(self, url):
        raise NotImplementedError

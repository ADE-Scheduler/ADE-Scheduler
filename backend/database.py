import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# TODO: Remove this (replaced in class Database)
engine = create_engine(os.environ['ADE_DB_PATH'], convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import backend.models
    Base.metadata.create_all(bind=engine)


# DEFINITION OF A SCHEDULE
"""
{
    code_list: [LMECA2660, LELEC2760, etc],             // requested course codes
    filtered_subcodes: [LELEC2760_Q1, LMECA2660_Q2],    // unselected subcodes
    custom_events: [{event1: ...}, {event2: ...}],      // custom user events
    priority_levels: {code1: 5, code2: 1, subcode1: 3}, // priority level of the various code & subcodes
    project_id: id,
    schedule_id: id,
}
"""

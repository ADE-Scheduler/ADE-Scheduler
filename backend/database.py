import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# TODO: Remove this (replaced in class Database)
engine = create_engine(os.environ['ADE_DB_PATH'], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import backend.models
    Base.metadata.create_all(bind=engine)

"""
class Database(declarative_base()):

    def __init__(self, name):
        self.engine = create_engine(f'sqlite:////tmp/{name}.db', convert_unicode=True)
        self.db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=self.engine))
        self.base = declarative_base()
        self.base.query = self.db_session.query_property()
        self.base.metadata.create_all(bind=self.engine)

        # Pas sur
        super().__init__()
"""

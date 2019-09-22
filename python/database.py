import pickle
import sqlite3
import os
import sqlalchemy as sql


current_folder = os.path.dirname(__file__)
db_type = 'sqlite:///'
db_name = 'database.db'
db_path = db_type + current_folder + '/' + db_name
db_engine = sql.create_engine(db_path)

metadata = sql.MetaData()
links = sql.Table('links', metadata,
                  sql.Column('id', sql.Integer, autoincrement=True, primary_key=True),
                  sql.Column('link', sql.String, unique=True, nullable=False),
                  sql.Column('username', sql.String, unique=True),
                  sql.Column('settings', sql.Binary))
ins = links.insert()
up = links.update()
sel = links.select()


def dropTables(test=False):
    """
    Removes both tables from the database.
    """
    if test:
        db = sqlite3.connect(os.path.join(current_folder, 'database_test.db'))
    else:
        db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.executescript("""
                        DROP TABLE IF EXISTS links;
                        """)
    db.commit()
    db.close()


def init():
    """
    Inits the database, creating it and the two tables if they don't already exist.
    """
    metadata.create_all(db_engine)


def getSettingsFromLink(link):
    """
    Fetch the settings corresponding to this link from the database
    :param link: str
    :return: settings (dict)
    """
    conn = db_engine.connect()
    resp = conn.execute(sel.where(links.c.link == link)).fetchone()
    conn.close()
    if resp:
        return pickle.loads(resp['settings'])
    else:
        return None


def isLinkPresent(link):
    """
    Check if this link is present in the database
    :param link: str
    :return: /
    """
    conn = db_engine.connect()
    resp = conn.execute(sel.where(links.c.link == link)).fetchone()
    conn.close()
    if resp:
        return True
    else:
        return False


def setLink(link, username=None, settings=None):
    """
    Adds an entry in the "links" table in the database
    :param link: str
    :param username: str
    :param settings: settings (dict)
    :return: /
    """
    conn = db_engine.connect()
    conn.execute(ins, link=link, username=username, settings=pickle.dumps(settings, -1))
    conn.close()


def updateSettingsFromLink(link, settings=None):
    """
    Updates the settings associated to this link
    :param link: str
    :param settings: settings (dict)
    :return: /
    """
    conn = db_engine.connect()
    conn.execute(up.where(links.c.link == link), settings=pickle.dumps(settings, -1))
    conn.close()


def deleteLink(link):
    """
    Delete the link with the settings from links table
    Parameters:
    -----------
    link: string
        the link to be deleted, with the settings
    Returns:
    --------
    None
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM links WHERE link=?", (link,))
    finally:
        db.commit()
        db.close()


def isUsernamePresent(username):
    """
    Checks if username is present in the database
    :param username: str
    :return: boolean
    """
    conn = db_engine.connect()
    resp = conn.execute(sel.where(links.c.username == username)).fetchone()
    conn.close()
    if resp:
        return True
    else:
        return False


def getLinkFromUsername(username):
    """
    Returns the link associated to this username in the database
    :param username: str
    :return: str, or None if username does not exist
    """
    conn = db_engine.connect()
    resp = conn.execute(sel.where(links.c.username == username)).fetchone()
    conn.close()
    if resp:
        return resp['link']
    else:
        return None

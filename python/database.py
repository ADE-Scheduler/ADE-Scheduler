import _pickle
import sqlite3
import os

current_folder = os.path.dirname(__file__)
db_path = os.path.join(current_folder, 'database.db')  # database is stored in the same folder as this file

"""
database.db : sqlite3 database containing
    - table link:
"""


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


def init(test=False):
    """
    Inits the database, creating it and the two tables if they don't already exist.
    """
    global db_path
    if test:
        db_path = os.path.join(current_folder, 'database_test.db')
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.executescript("""
                        CREATE TABLE IF NOT EXISTS links(
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        link TEXT UNIQUE NOT NULL,
                        username TEXT UNIQUE,
                        settings TEXT
                    );""")
    db.commit()
    db.close()


def getSettingsFromLink(link):
    """
    Get settings from the links table with the corresponding link (unique per settings).
    Parameters:
    -----------
    link : string
        The key needed to get the settings back.
    Returns:
    --------
    s : iterable of str or None
        None if settings not found. Otherwise, the settings previously saved.
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT settings FROM links WHERE link=?", (link,))
    resp = cursor.fetchone()
    if resp:
        s, = resp
        db.close()
    else:
        db.close()
        return None
    return _pickle.loads(s)


def isLinkPresent(link):
    """
    Tell if the link link is present in links table
    Parameters:
    -----------
    link : string
        The link to be in the table
    Returns:
    --------
    True if the link is in the table, False elsewhere
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM links WHERE link=?", (link,))
    resp = cursor.fetchall()
    if resp:
        db.close()
        return True
    else:
        db.close()
        return False


def setLink(link, username=None, settings=None):
    """
    Set link with the setting into the links table
    Parameters:
    -----------
    link : string
        the link of the calendar
    username: string
        the username of the link
    settings: dict
        the settings of the calendar
    Returns:
    --------
    None
    """
    s = _pickle.dumps(settings, -1)
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute('''INSERT INTO links(link,username,settings) 
        VALUES(?,?,?);''', (link, username, s))
    db.commit()
    db.close()


def updateSettingsFromLink(link, settings=None):
    """
    Update the settings from links table with the corresponding link
    Parameters:
    -----------
    link : string
        the link of the calendar
    settings: dict
        the settings of the calendar
    Returns:
    --------
    None
    """
    s = _pickle.dumps(settings, -1)
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("UPDATE OR IGNORE links SET settings=? WHERE link=?", (s, link))
    db.commit()
    db.close()
    return None


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
    Tell if login is in the links table
    Parameters:
    -----------
    login : text
        the login
    Returns:
    --------
    True if the login is present, False elsewhere
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT username FROM links WHERE username=?", (username,))
    resp = cursor.fetchone()
    if resp:
        log = True
    else:
        log = False
    db.close()
    return log


def getLinkFromUsername(username):
    """
    Get link from the links table at a given username
    Parameters:
    -----------
    username: text
        the username to retrive the information
    Returns:
    --------
    The link associated to the username, None if not present
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT link FROM links WHERE username=?", (username,))
    resp = cursor.fetchone()
    if resp:
        link, = resp
    else:
        return None
    db.close()
    return link

import _pickle
import sqlite3
import os
from time import time

current_folder = os.path.dirname(__file__)
db_path = os.path.join(current_folder, 'database.db')  # database is stored in the same folder as this file
max_delay = 26 * 60 * 60  # One day in seconds

"""
database.db : sqlite3 database containing
    - table "courses" containing Course objects that can be retrieved using their Course.code.
    Only returns something if the Course objet is not outdated (defined by max_delay).
    - table "settings" containing informations to reconstruct a course.
    When adding a setting to the database, returns the id to needed to get it back later.
"""


def dropTables():
    """
    Removes both tables from the database.
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.executescript("""
                        DROP TABLE courses;
                        DROP TABLE settings
                        DROP TABLE links""")
    db.commit()
    db.close()


def init():
    """
    Inits the database, creating it and the two tables if they don't already exist.
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.executescript("""CREATE TABLE IF NOT EXISTS courses(
                        code TEXT,
                        course TEXT,
                        date REAL
                    );

                        CREATE TABLE IF NOT EXISTS settings(
                        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        s TEXT
                    );
                    
                        CREATE TABLE IF NOT EXISTS links(
                        username TEXT PRIMARY KEY UNIQUE,
                        link TEXT UNIQUE,
                        s TEXT""")
    db.commit()
    db.close()


def addSettings(settings):
    """
    Add settings to the settings table.
    Parameters:
    -----------
    settings : structure with same format as event.getSettingsFromEvents
        The settings used to filter events you want to keep.
    Returns:
    --------
    id : int
        The key needed to get the settings back using getSettings(id).
    """
    s = _pickle.dumps(settings, -1)
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("INSERT INTO settings(s) VALUES(?)", (s,))
    id = cursor.lastrowid
    db.commit()
    db.close()
    return id


def addCourse(course):
    """
    Add course to the courses table only if last version is outdated.
    Parameters:
    -----------
    course : Course
        An intance of course.Course class.
    Returns:
    --------
    added : bool
        Whether or not the course has been added.
    """
    s = _pickle.dumps(course, -1)
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT date FROM courses WHERE code=?", (course.code,))
    resp = cursor.fetchone()
    if resp:  # If course already in table
        date, = resp
        if date + max_delay < time():  # If outdated
            cursor.execute("DELETE from courses where code=?", (course.code,))
            db.commit()
        else:  # If still valid
            return False
    cursor.execute("""INSERT INTO courses(
                        code, course, date) VALUES(?, ?, ?)""",
                   (course.code, s, time()))
    db.commit()
    db.close()
    return True


def getSettings(id):
    """
    Get settings from the settings table with the corresponding id (unique per settings).
    Parameters:
    -----------
    id : int
        The key needed to get the settings back.
    Returns:
    --------
    s : iterable of str or None
        None if settings not found. Otherwise, the settings previously saved.
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT s FROM settings WHERE id=?", (id,))
    resp = cursor.fetchone()
    if resp:
        s, = resp
    else:
        return None
    db.close()
    return _pickle.loads(s)


def getCourse(code):
    """
    Get course from the courses table with the corresponding code (unique per course).
    Parameters:
    -----------
    code : str
        The code from Course.code.
    Returns:
    --------
    course : Course
        None if course not found or outdated (deleted in this case). Otherwise, the course previously saved.
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("SELECT course, date FROM courses WHERE code=?", (code,))
    resp = cursor.fetchone()
    if resp:
        course, date = resp
    else:
        return None
    if date + max_delay < time():
        cursor.execute("DELETE from courses where code=?", (code,))
        db.commit()
        return None
    db.close()
    return _pickle.loads(course)


def updateSettings(id, settings):
    """
    Update settings to the settings table at given id.
    Parameters:
    -----------
    id : int
        The id of the settings you want to update (remplaces old with new settings).
    settings : iterable of str
        The settings used to filter events you want to keep.
    """
    s = _pickle.dumps(settings, -1)
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("UPDATE settings SET s=? where id=?", (s, id))
    db.commit()
    db.close()

# At the moment, the name is not correct, because of above
def getSettingsLink(link):
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
    cursor.execute("SELECT s FROM links WHERE link=?", (link,))
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
    cursor.execute("SELECT link FROM links WHERE link=?", (hash,))
    resp = cursor.fetchone()
    if resp:
        db.close()
        return True
    else:
        db.close()
        return False

def setLink(link, settings=None):
    """
    Set link with the setting into the links table
    Parameters:
    -----------
    link : string
        the link of the calendar
    settings: string
        the settings of the calendar
    Returns:
    --------
    None
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("INSERT OR IGNORE INTO links(link,settings) VALUES (%s, %s)" % (link, settings))
    db.close()

def updateSettings(link, settings=None):
    """
    Update the settings from links table with the corresponding link
    Parameters:
    -----------
    link : string
        the link of the calendar
    settings: string
        the settings of the calendar
    Returns:
    --------
    None
    """
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    cursor.execute("UPDATE OR IGNORE links SET s=? WHERE link=?", (settings, link))
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
        cursor.execute("DELETE FROM links WHERE link=?", link)
    finally:
        db.close()

def isLoginPresent(login):
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
    cursor.execute("SELECT login FROM links WHERE login=?", login)
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
    cursor.execute("SELECT s FROM links WHERE username=?", (username,))
    resp = cursor.fetchone()
    if resp:
        link, = resp
    else:
        return None
    db.close()
    return _pickle.loads(link)
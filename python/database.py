import _pickle
import sqlite3
import os
from time import time

current_folder = os.path.dirname(__file__)
db_path = os.path.join(current_folder, 'database.db') # database is stored in the same folder as this file
max_delay = 26 * 60 * 60 # One day in seconds

"""
database.db : sqlite3 database containing
    - table "courses" containing Course objects that can be retrieved using their Course.code.
    Only returns something if the Course objet is not outdated (defined by max_delay).
    - table "settings" containing iterable of CustomEvent.getId()-like strings.
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
                        DROP TABLE settings""")
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
                    );""")
    db.commit()
    db.close()

def addSettings(settings):
    """
    Add settings to the settings table.
    Parameters:
    -----------
    settings : iterable of str
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
    if resp: # If course already in table
        date, = resp
        if date + max_delay < time(): # If outdated
            cursor.execute("DELETE from courses where code=?", (course.code,))
            db.commit()
        else: # If still valid
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
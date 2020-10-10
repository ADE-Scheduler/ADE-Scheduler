activate_this = "/path/to/venv/bin/activate_this.py"
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Set path
import sys
import os

sys.path.insert(0, "/path/to/repo")

# Import env variables
import dotenv

dotenv.load_dotenv("/path/to/.flaskenv")


from app import app as application

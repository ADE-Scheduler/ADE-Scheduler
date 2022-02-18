import os
import sys

import pytest
from dotenv import find_dotenv, load_dotenv

sys.path.append(os.getcwd())
load_dotenv(find_dotenv(".flaskenv"))

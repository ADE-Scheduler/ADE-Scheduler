import os
import sys
import pytest
from dotenv import load_dotenv, find_dotenv

sys.path.append(os.getcwd())
load_dotenv(find_dotenv(".flaskenv"))

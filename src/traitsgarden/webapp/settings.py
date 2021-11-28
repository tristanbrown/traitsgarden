"""
This is the config file, containing various parameters the user may
wish to modify.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    SECRET_KEY = 'mysecretkey'

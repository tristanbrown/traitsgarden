"""
This is the config file, containing various parameters the user may
wish to modify.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class AppConfig():
    SECRET_KEY = 'mysecretkey'

class DBConfig():
    NAME = 'garden'
    TESTNAME = 'garden_test'
    HOST = 'postgres'
    USER = 'postgres'
    PW = os.getenv('POSTGRES_PASSWORD') ## Set in docker-compose.yml

    TZ = os.getenv('TIMEZONE') or 'UTC'

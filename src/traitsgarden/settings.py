"""
This is the config file, containing various parameters the user may
wish to modify.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config():

    TZ = os.getenv('TIMEZONE') or 'UTC'

    ## DB Config

    DB_NAME = 'garden'
    DB_HOST = 'postgres'
    DB_USER = 'postgres'
    DB_PW = os.getenv('POSTGRES_PASSWORD') ## Set in docker-compose.yml

    ## App Config
    SECRET_KEY = 'mysecretkey'

    @property
    def DATABASE_URI(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PW}@{self.DB_HOST}/{self.DB_NAME}"


class TestConfig(Config):

    DB_NAME = 'garden_test'
    TESTING = True

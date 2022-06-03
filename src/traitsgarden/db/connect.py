"""Connection to Postgres"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from traitsgarden.settings import Config, TestConfig

Base = declarative_base()
Session = sessionmaker()

sqlengines = {
    'default': create_engine(Config().DATABASE_URI),
    'test': create_engine(TestConfig().DATABASE_URI),
}

def connect_db(enginekey='default'):
    enginekey = os.getenv('APP_ENV') or enginekey
    engine = sqlengines[enginekey]
    Base.metadata.bind = engine
    Session.configure(bind=engine)
    db_name = str(engine.url).split('/')[-1]
    print(f"Connected DB: {db_name}")

connect_db()

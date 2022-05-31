"""Connection to Postgres"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from traitsgarden.settings import DBConfig

Base = declarative_base()
Session = sessionmaker()

def get_engine(db_name):
    db_url = f"postgresql://{DBConfig.USER}:{DBConfig.PW}@{DBConfig.HOST}/{db_name}"
    return create_engine(db_url)

sqlengines = {
    'default': get_engine(DBConfig.NAME),
    'test': get_engine(DBConfig.TESTNAME),
}

def connect_db(engine='default'):
    engine = sqlengines[engine]
    Base.metadata.bind = engine
    Session.configure(bind=engine)
    db_name = str(engine.url).split('/')[-1]
    print(f"Connected DB: {db_name}")

connect_db()

"""Connection to Postgres"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

LOCALTZ = os.getenv('TIMEZONE', 'US/Pacific')

db_url = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD')}@postgres/garden"
sqlengine = create_engine(db_url)

Session = sessionmaker(bind=sqlengine)
sqlsession = Session()

Base = declarative_base(bind=sqlengine)

"""
Connect to the DB
"""
from .connect import connect_db, test_db, drop_test

mongoclient, db = connect_db()

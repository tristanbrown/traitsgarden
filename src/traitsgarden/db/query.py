"""Query Functions for the MongoDB"""

import pandas as pd
from sqlalchemy import select

from traitsgarden.db.connect import sqlsession

def query_as_df(collection, queryargs=None):
    """Query the collection as a dataframe.

    Usage:
    query_as_df('seeds', [{"$match": {'category': 'tomato'} }])
    """
    queryargs = queryargs or []
    df = pdm.read_mongo(
        collection=collection, query=queryargs, db=db, index_col='_id')
    return df

def query_as_obj(model, **fieldvals):
    """Find the existing entry(ies) in the database, matching the fieldvals.
    """
    stmt = select(model).filter_by(**fieldvals)
    result = sqlsession.execute(stmt)
    return result.scalars().all()

def query_existing(entity, fields):
    """Find the existing entry(ies) in the database matching the given fields
    on the given object.
    """
    fieldvals = {field: getattr(entity, field) for field in fields}
    result = query_as_obj(entity.__class__, **fieldvals)
    return result

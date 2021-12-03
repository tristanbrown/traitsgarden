"""Query Functions for the MongoDB"""

import pdmongo as pdm

from traitsgarden.db import db

def query_as_df(collection, queryargs=None):
    """Query the collection as a dataframe.

    Usage:
    query_as_df('seeds', [{"$match": {'category': 'tomato'} }])
    """
    queryargs = queryargs or []
    df = pdm.read_mongo(
        collection=collection, query=queryargs, db=db, index_col='_id')
    return df

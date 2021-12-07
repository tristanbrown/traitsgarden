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

def get_existing(entity, fields):
    """Find the existing entry(ies) in the database matching the given fields
    on the given object.
    """
    model = entity.__class__
    if not isinstance(fields, list):
        fields = [fields]
    keyfields = {field: getattr(entity, field) for field in fields}
    return model.objects(**keyfields)

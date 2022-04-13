"""Query Functions for the MongoDB"""

import pandas as pd
from sqlalchemy import select

from traitsgarden.db.connect import sqlsession

def query_as_df(query):
    """Query the table as a dataframe.

    The query can be a SQL SELECT statement, or a table name.
    """
    return pd.read_sql(query, sqlsession.bind)

def query_as_obj(model, **fieldvals):
    """Find the existing entry(ies) in the database, matching the fieldvals.
    Use '__' to match attributes on a child object.
    Example:
    query_as_obj(Seeds, seeds_id='21A', cultivar__name='Pinocchio Orange Micro')
    """
    ## Set up WHERE conditions
    conds = []
    for field, val in fieldvals.items():
        if '__' in field:
            ## Attribute on a child object
            relation, subfield = field.split('__')
            subfieldvals = {subfield: val}
            conds.append(getattr(model, relation).has(**subfieldvals))
        else:
            ## Ordinary attribute
            conds.append(getattr(model, field) == val)

    ## Run the query
    stmt = select(model).where(*conds)
    result = sqlsession.execute(stmt)
    return result.scalars().all()

def query_existing(entity, fields):
    """Find the existing entry(ies) in the database matching the given fields
    on the given object.
    Example:
    query_existing(seeds1, ['cultivar__name', 'cultivar__category', 'year', 'variant'])
    """
    fieldvals = {}
    for field in fields:
        if '__' in field:
            ## Attribute on a child object
            relation, subfield = field.split('__')
            fieldvals[field] = getattr(getattr(entity, relation), subfield)
        else:
            ## Ordinary attribute
            fieldvals[field] = getattr(entity, field)

    result = query_as_obj(entity.__class__, **fieldvals)
    return result

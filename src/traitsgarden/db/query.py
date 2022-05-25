"""Query Functions for the MongoDB"""

import pandas as pd
from sqlalchemy import select

from traitsgarden.db.connect import Session

def query_as_df(query):
    """Query the table as a dataframe.

    The query can be a SQL SELECT statement, or a table name.
    """
    with Session() as session:
        df = pd.read_sql(query, session.bind)
    return df

def query_as_obj(model, session=None, **fieldvals):
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
    result = session.execute(stmt)
    obj = result.scalars().all()
    return obj

def query_one_obj(model, session=None, **fieldvals):
    """Return the first result from query_as_obj."""
    existing = query_as_obj(model, session, **fieldvals)
    if existing:
        return existing[0]

def query_existing(entity, fields, session=None):
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

    result = query_as_obj(entity.__class__, session=session, **fieldvals)
    return result

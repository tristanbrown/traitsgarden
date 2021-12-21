"""Data Entry into Postgresql"""

from traitsgarden.db.connect import sqlsession

def obj_from_df(df, model):
    """Load a list of documents from a table."""
    records = df.to_dict(orient='records')
    return [model(**row) for row in records]

def bulk_insert(entities):
    """Add all of the ORM objects to the database."""
    sqlsession.add_all(entities)
    sqlsession.commit()

def upsert(entity, del_vals=False):
    """Create or update a mongoengine entity, matching on keyfields.

    Set 'del_vals' to True to also sync null values.
    """
    try:
        entity.save()
        entity.reload()
        return entity
    except NotUniqueError:
        existobj = entity.db_obj
        newvals = entity.to_mongo().to_dict()
        try:
            del newvals['_id']
        except KeyError:
            pass
        for k, v in newvals.items():
            setattr(existobj, k, v)
        if del_vals:
            existvals = existobj.to_mongo().to_dict()
            del existvals['_id']
            missing_fields = set(existvals.keys()) - set(newvals.keys())
            for field in missing_fields:
                delattr(existobj, field)
        existobj.save()
        existobj.reload()
        return existobj
    except ValidationError:
        print(entity.to_mongo().to_dict())
        raise

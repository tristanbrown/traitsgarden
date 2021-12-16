"""Data Entry into MongoDB"""

from mongoengine import NotUniqueError

def docs_from_df(df, model):
    """Load a list of documents from a table."""
    return [model.from_json(row.to_json(date_format='iso')) for _,row in df.iterrows()]

def upsert(entity):
    """Create or update a mongoengine entity, matching on keyfields.
    """
    try:
        entity.save()
        return entity
    except NotUniqueError:
        entity.clean()
        entity.validate()
        existobj = entity.db_obj
        kwargs = entity.to_mongo().to_dict()
        try:
            del kwargs['_id']
        except KeyError:
            pass
        existobj.update(**kwargs)
        existobj.save()
        return existobj

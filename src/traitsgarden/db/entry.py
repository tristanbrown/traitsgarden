"""Data Entry into MongoDB"""

from pymongo import UpdateOne
# from pymongo.errors import DuplicateKeyError
from mongoengine import Document, ValidationError, NotUniqueError
from bson.objectid import ObjectId

from traitsgarden.db.query import get_existing

def docs_from_df(df, model):
    """Load a list of documents from a table."""
    return [model.from_json(row.to_json()) for _,row in df.iterrows()]

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

# def bulk_upsert(entities):
#     #TODO: DOESN'T VALIDATE PROPERLY
#     """Create or update multiple mongoengine entities"""
#     bulk_operations = []
#     if not isinstance(entities, list):
#         entities = [entities]
#     model = entities[0].__class__
#     for entity in entities:
#         try:
#             entity.clean()
#             entity.validate()
#             if entity.id is None:
#                 entity.id = ObjectId()
#             bulk_operations.append(
#                 UpdateOne(
#                     {'_id': entity.id},
#                     {'$set': entity.to_mongo().to_dict()},
#                     upsert=True))

#         except ValidationError:
#             pass

#     if bulk_operations:
#         collection = model._get_collection() \
#             .bulk_write(bulk_operations, ordered=False)

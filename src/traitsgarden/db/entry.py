"""Data Entry into Postgresql"""
import numpy as np
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from traitsgarden.db.connect import Session

def obj_from_df(df, model):
    """Load a list of documents from a table."""
    df = df.replace({np.NaN: None})
    records = df.to_dict(orient='records')
    return [model(**row) for row in records]

def bulk_insert(entities):
    """Add all of the ORM objects to the database."""
    with Session.begin() as session:
        session.add_all(entities)

def upsert(entity, del_vals=False):
    """Create or update a sqlalchemy entity, matching on keyfields.

    Set 'del_vals' to True to also sync null values.
    """
    with Session() as session:
        try:
            session.add(entity)
            session.commit()
            return entity
        except IntegrityError as ex:
            assert isinstance(ex.orig, UniqueViolation)
            session.rollback()

            existobj = entity.db_obj
            newvals = entity.__dict__.copy()
            del newvals['_sa_instance_state']
            for k, v in newvals.items():
                setattr(existobj, k, v)

            if del_vals:
                existvals = existobj.__dict__.copy()
                del existvals['_id']
                missing_fields = set(existvals.keys()) - set(newvals.keys())
                for field in missing_fields:
                    delattr(existobj, field)

            session.commit()
            return existobj

        except ValidationError:
            print(entity.__dict__)
            raise

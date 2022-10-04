"""Database models"""
import arrow
import numpy as np
import pandas as pd

from sqlalchemy import (Column, ForeignKey, asc, desc, Computed, UniqueConstraint,
    ForeignKeyConstraint, cast, func, select, inspect
)
from sqlalchemy.types import (Integer, TIMESTAMP, Numeric, String, Date,
    Boolean
)
from sqlalchemy.sql import sqltypes
from sqlalchemy.orm import validates, relationship, column_property, close_all_sessions
from sqlalchemy.ext.associationproxy import association_proxy

from traitsgarden.db.connect import Base, Session
from traitsgarden.db.query import query_existing, query_one_obj, query_as_df
from traitsgarden.db import util

class DBObjMixin():

    @classmethod
    def get(cls, session, id):
        return query_one_obj(session, cls, id=id)

    def delete(self, session):
        session.delete(self)

    @classmethod
    def columns(cls):
        return inspect(Plant).c

    @classmethod
    def types(cls):
        coldata = [[col.name, col.type] for col in cls.columns()]
        return pd.DataFrame(coldata, columns=['name', 'type'])

    @classmethod
    def datecols(cls):
        coltypes = cls.types()
        datetypes = coltypes[coltypes['type'].apply(isinstance, args=[sqltypes.Date])]
        return list(datetypes['name'])

class Cultivar(DBObjMixin, Base):
    __tablename__ = 'cultivar'

    ## ID Fields
    id = Column(Integer, primary_key=True)
    name = Column(String(length=120), nullable=False)
    category = Column(String(length=120), nullable=False)

    __table_args__ = (
        UniqueConstraint('name', 'category', name='_cultivar_uc'),
    )

    ## Info Fields
    species = Column(String(length=120))
    hybrid = Column(Boolean(), default=False)
    description = Column(String())

    def __repr__(self, recursion=False):
        return f"<Cultivar: {self.name} - {self.category}>"

    @classmethod
    def query(cls, session, name, category):
        return query_one_obj(session, cls, name=name, category=category)

    @classmethod
    def add(cls, session, name, category):
        obj = cls(name=name, category=category)
        session.add(obj)
        return obj

    @staticmethod
    def table():
        query = """SELECT *
            FROM cultivar
            """
        return query_as_df(query).set_index('id').sort_index()

class Seeds(DBObjMixin, Base):
    __tablename__ = 'seeds'

    ## ID Fields
    id = Column(Integer, primary_key=True)
    cultivar_id = Column(Integer, ForeignKey('cultivar.id'), nullable=False)
    cultivar = relationship("Cultivar")
    name = association_proxy('cultivar', 'name')
    category = association_proxy('cultivar', 'category')
    pkt_id = Column(String(length=4), nullable=False)
    year = Column(Integer(), nullable=False)

    __table_args__ = (
        UniqueConstraint('cultivar_id', 'pkt_id', name='_seeds_uc'),
                     )

    ## Parent/Child Relationships
    # TODO: Convert to Many to Many Fields with 'mother' bool flag in ref table
    mother_id = Column(Integer, ForeignKey('plant.id'))
    father_id = Column(Integer, ForeignKey('plant.id'))
    mother = relationship("Plant", foreign_keys=[mother_id], post_update=True)
    father = relationship("Plant", foreign_keys=[father_id], post_update=True)

    ## Seeds Data
    source = Column(String(length=120))
    last_count = Column(Integer())
    generation = Column(String(length=2), default='1')
    germination = Column(Numeric(2, 2))

    def __repr__(self, recursion=False):
        return f"<Seeds: {self.name} - {self.category} - {self.pkt_id}>"

    @classmethod
    def query(cls, session, name, category, pkt_id):
        return query_one_obj(session, cls, name=name, category=category, pkt_id=pkt_id)

    @classmethod
    def add(cls, session, name, category, pkt_id, **kwargs):
        year = f"20{pkt_id[0:2]}"
        variant = pkt_id[-1]
        cultivar = Cultivar.query(session, name, category)
        if cultivar is None:
            cultivar = Cultivar.add(session, name, category)
        obj = cls(cultivar=cultivar, year=year, variant=variant, **kwargs)
        session.add(obj)
        return obj

    @staticmethod
    def table():
        query = """SELECT b.name, b.category, a.*
            FROM seeds a
            JOIN cultivar b
            ON a.cultivar_id = b.id
            """
        df = query_as_df(query)
        df = df.set_index(
            ['id', 'cultivar_id', 'category', 'name', 'pkt_id']).reset_index()
        return df.set_index('id').sort_index()

    def add_parent(self, session, plant_id, parent=None, name=None, category=None):
        """Defaults to the same name/category,
        but others can be specified for crossbreeds.

        Default parent is both. Can be specified to 'mother' or 'father'.
        """
        if name is None:
            name = self.name
        if category is None:
            category = self.category
        parent_obj = Plant.query(session, name, category, plant_id)
        self.add_parent_obj(session, parent_obj, parent)

    def add_parent_obj(self, session, parent_obj, parent=None):
        """Default parent is both. Can be specified to 'mother' or 'father'."""
        if parent is None:
            for _parent in ('mother', 'father'):
                setattr(self, _parent, parent_obj)
        else:
            setattr(self, parent, parent_obj)

class Plant(DBObjMixin, Base):
    __tablename__ = 'plant'

    ## ID Fields
    id = Column(Integer, primary_key=True)
    seeds_id = Column(Integer)
    seeds = relationship('Seeds', #foreign_keys=[seeds_id],
        primaryjoin="foreign(Plant.seeds_id)==Seeds.id"
        )
    ForeignKeyConstraint(
        ['seeds_id'], ['seeds.id'],
        name='fk_plant_seeds_id', use_alter=True
    )
    name = association_proxy('seeds', 'name')
    category = association_proxy('seeds', 'category')
    cultivar = association_proxy('seeds', 'cultivar')
    plant_id = Column(String(length=6), nullable=False)

    ## Plant Data
    start_date = Column(Date())
    germ_date = Column(Date())
    flower_date = Column(Date())
    fruit_date = Column(Date())
    conditions = Column(String())
    growth = Column(String())
    height = Column(Numeric())  ## In inches
    fruit_yield = Column(String(length=120))
    fruit_desc = Column(String())
    flavor = Column(String())
    variant_notes = Column(String())
    active = Column(Boolean(), default=False)

    __table_args__ = (
        UniqueConstraint('plant_id', name='_plant_id_uc'),
                     )

    def __repr__(self, recursion=False):
        return f"<Plant: {self.name} - {self.category} - {self.plant_id}>"

    @classmethod
    def query(cls, session, name, category, plant_id):
        return query_one_obj(session, cls, name=name, category=category, plant_id=plant_id)

    @classmethod
    def add(cls, session, name, category, plant_id, **kwargs):
        pkt_id = plant_id[:-2]
        individual = plant_id[-2:]
        seedparent = Seeds.query(session, name, category, pkt_id)
        if seedparent is None:
            seedparent = Seeds.add(session, name, category, pkt_id)
        obj = cls(seeds=seedparent, individual=individual, **kwargs)
        session.add(obj)
        return obj

    @classmethod
    def table(cls):
        query = """SELECT b.cultivar_id, c.name, c.category, b.pkt_id, a.*
            FROM plant a
            JOIN seeds b
            ON a.seeds_id = b.id
            JOIN cultivar c
            ON b.cultivar_id = c.id
            """
        datecols = cls.datecols()
        df = query_as_df(query, datecols)
        for col in datecols:
            df[col] = df[col].dt.date
        df = df.set_index(
            ['id', 'cultivar_id', 'category', 'name', 'seeds_id', 'pkt_id', 'plant_id']
        ).reset_index()
        return df.set_index('id').sort_index()

    @validates('height')
    def validate_height(self, key, height):
        if isinstance(height, str):
            return util.convert_to_inches(height)
        return height

    @validates('individual')
    def validate_individual(self, key, individual):
        try:
            return int(individual)
        except ValueError:
            indiv_id = ord(individual) - 96
            if (indiv_id >= 1) and (indiv_id <= 26):
                return int(indiv_id)
            else:
                raise
        except TypeError:
            return 1

    @property
    def parent_seeds(self):
        """"""
        parent = Seeds.objects(
            name=self.name,
            category=self.category,
            **Seeds.parse_id(self.parent_id)
        )
        try:
            return parent.get()
        except DoesNotExist:
            return

def create_all():
    Base.metadata.create_all()
    print("Created all tables.")

def drop_all():
    close_all_sessions()
    Base.metadata.drop_all()
    print("Dropped all tables.")

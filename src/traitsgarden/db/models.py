"""Database models"""
import arrow
import numpy as np
import pandas as pd

from sqlalchemy import (Column, ForeignKey, asc, desc, Computed, UniqueConstraint,
    ForeignKeyConstraint, cast, func, select
)
from sqlalchemy.types import (Integer, TIMESTAMP, Numeric, String, Date,
    Boolean
)
from sqlalchemy.orm import validates, relationship, column_property, close_all_sessions
from sqlalchemy.ext.associationproxy import association_proxy

from traitsgarden.db.connect import Base, Session
from traitsgarden.db.query import query_existing, query_one_obj
from traitsgarden.db import util

class Cultivar(Base):
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
    def query(cls, bind, name, category):
        return query_one_obj(cls, bind, name=name, category=category)

    @classmethod
    def add(cls, bind, name, category):
        obj = cls(name=name, category=category)
        bind.add(obj)
        return obj

class Seeds(Base):
    __tablename__ = 'seeds'

    ## ID Fields
    id = Column(Integer, primary_key=True)
    cultivar_id = Column(Integer, ForeignKey('cultivar.id'), nullable=False)
    cultivar = relationship("Cultivar")
    name = association_proxy('cultivar', 'name')
    category = association_proxy('cultivar', 'category')
    year = Column(Integer(), nullable=False)
    variant = Column(String(length=2), nullable=False)
    pkt_id = column_property(
        func.substr(cast(year, String), 3, 5) + variant)

    __table_args__ = (
        UniqueConstraint('cultivar_id', 'year', 'variant', name='_seeds_uc'),
                     )

    ## Parent/Child Relationships
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
    def query(cls, bind, name, category, pkt_id):
        return query_one_obj(cls, bind, name=name, category=category, pkt_id=pkt_id)

    @classmethod
    def add(cls, bind, name, category, year, variant, **kwargs):
        ## TODO: Consider using pkt_id
        cultivar = Cultivar.query(bind, name, category)
        if cultivar is None:
            cultivar = Cultivar.add(bind, name, category)
        obj = cls(cultivar=cultivar, year=year, variant=variant, **kwargs)
        bind.add(obj)
        return obj

class Plant(Base):
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
    individual = Column(Integer(), nullable=False, default=1)
    plant_id = column_property(
        select(Seeds.pkt_id
            ).where(Seeds.id == seeds_id
            ).scalar_subquery() \
            + func.lpad(cast(individual, String), 2, '0'))

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
    done = Column(Boolean(), default=False)

    __table_args__ = (
        UniqueConstraint('seeds_id', 'individual', name='_plant_id_uc'),
                     )

    def __repr__(self, recursion=False):
        return f"<Plant: {self.name} - {self.category} - {self.plant_id}>"

    def db_obj(self, bind):
        existing = query_existing(self, ['pkt_id', 'individual'], bind=bind)
        if existing:
            return existing[0]

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

"""Database models"""
import arrow
import numpy as np
import pandas as pd

from sqlalchemy import (Column, ForeignKey, asc, desc, Computed, UniqueConstraint,
    ForeignKeyConstraint, cast, func
)
from sqlalchemy.types import (Integer, TIMESTAMP, Numeric, String, Date,
    Boolean
)
from sqlalchemy.orm import validates, relationship, column_property

from traitsgarden.db.connect import Base, sqlsession
from traitsgarden.db.query import query_existing
from traitsgarden.db import util

class Cultivar(Base):
    __tablename__ = 'cultivar'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=120), nullable=False)
    category = Column(String(length=120), nullable=False)
    species = Column(String(length=120))
    hybrid = Column(Boolean(), default=False)
    description = Column(String())

    __table_args__ = (
        UniqueConstraint('name', 'category', name='_cultivar_uc'),
    )

class Plant(Base):
    __tablename__ = 'plant'

    id = Column(Integer, primary_key=True)
    seeds_id = Column(Integer)
    seeds = relationship('Seeds', #foreign_keys=[seeds_id],
        primaryjoin="foreign(Plant.seeds_id)==Seeds.id"
        )
    # seed_id = Column(String(length=4), nullable=False)
    individual = Column(Integer(), nullable=False, default=1)
    ForeignKeyConstraint(
        ['seeds_id'], ['seeds.id'],
        name='fk_plant_seeds_id', use_alter=True
    )

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

    # def __repr__(self, recursion=False):
    #     try:
    #         return f"<{self.name} - {self.category} - {self.plant_id}>"
    #     except:
    #         if recursion:
    #             raise
    #         self.clean()
    #         return self.__repr__(recursion=True)

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
    def plant_id(self):
        return f"{self.parent_id}{str(self.individual).zfill(2)}"

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

    @property
    def db_obj(self):
        existing = query_existing(self, ['name', 'category', 'parent_id', 'individual'])
        if existing:
            return existing[0]

class Seeds(Base):
    __tablename__ = 'seeds'

    id = Column(Integer, primary_key=True)
    cultivar_id = Column(Integer, ForeignKey('cultivar.id'), nullable=False)
    cultivar = relationship("Cultivar")
    year = Column(Integer(), nullable=False)
    variant = Column(String(length=2), nullable=False)
    seeds_id = column_property(
        func.substr(cast(year, String), 3, 5) + variant)

    mother_id = Column(Integer, ForeignKey('plant.id'))
    father_id = Column(Integer, ForeignKey('plant.id'))
    mother = relationship("Plant", foreign_keys=[mother_id], post_update=True)
    father = relationship("Plant", foreign_keys=[father_id], post_update=True)

    source = Column(String(length=120))
    last_count = Column(Integer())
    generation = Column(String(length=2), default='1')
    germination = Column(Numeric(2, 2))

    __table_args__ = (
        UniqueConstraint('cultivar_id', 'year', 'variant', name='_seeds_id_uc'),
                     )

    # def __repr__(self, recursion=False):
    #     try:
    #         return f"<{self.name} - {self.category} - {self.seeds_id}>"
    #     except:
    #         if recursion:
    #             raise
    #         self.clean()
    #         return self.__repr__(recursion=True)

    @property
    def db_obj(self):
        existing = query_existing(self, ['name', 'category', 'year', 'variant'])
        if existing:
            return existing[0]

def create_all():
    Base.metadata.create_all()
    print("Created all tables.")

def drop_all():
    sqlsession.close_all()
    Base.metadata.drop_all()
    print("Dropped all tables.")

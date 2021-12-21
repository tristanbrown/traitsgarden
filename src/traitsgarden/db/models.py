"""Database models"""
import arrow
import numpy as np
import pandas as pd

from sqlalchemy import Column, asc, desc, Computed, UniqueConstraint
from sqlalchemy.types import (Integer, TIMESTAMP, Numeric, String, Date,
    Boolean
)
from sqlalchemy.orm import validates

from traitsgarden.db.connect import Base
from traitsgarden.db.query import get_existing
from traitsgarden.db import util

class Plant(Base):
    __tablename__ = 'plant'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=120), nullable=False)
    category = Column(String(length=120), nullable=False)
    species = Column(String(length=120))
    parent_id = Column(String(length=4), nullable=False)
    individual = Column(Integer(), nullable=False, default=1)
    year = Column(Integer())
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
        UniqueConstraint('name', 'category', 'parent_id', 'individual', name='_plant_id_uc'),
                     )

    def __repr__(self, recursion=False):
        try:
            return f"<{self.name} - {self.category} - {self.plant_id}>"
        except:
            if recursion:
                raise
            self.clean()
            return self.__repr__(recursion=True)

    @validates('height')
    def validate_height(self, key, height):
        if isinstance(height, str):
            return util.convert_to_inches(height)
        return height

    @validates('individual')
    def validate_individual(self, key, individual):
        try:
            indiv_id = ord(individual) - 96
            if (indiv_id >= 1) and (indiv_id <= 26):
                return indiv_id
        except TypeError:
            pass
        return individual

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
        existing = get_existing(self, ['name', 'category', 'parent_id', 'individual'])
        if existing:
            return existing.get()

class Seeds(Base):
    __tablename__ = 'seeds'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=120), nullable=False)
    category = Column(String(length=120), nullable=False)
    species = Column(String(length=120))
    source = Column(String(length=120))
    # parent_plants = ListField(LazyReferenceField('Plant'))
    variant = Column(String(length=2), nullable=False)
    year = Column(Integer(), nullable=False)
    last_count = Column(Integer())
    generation = Column(String(length=2), default='1')
    germination = Column(Numeric(2, 2))
    parent_description = Column(String())

    __table_args__ = (
        UniqueConstraint('name', 'category', 'year', 'variant', name='_seeds_id_uc'),
                     )

    def __repr__(self, recursion=False):
        try:
            return f"<{self.name} - {self.category} - {self.seeds_id}>"
        except:
            if recursion:
                raise
            self.clean()
            return self.__repr__(recursion=True)

    def clean(self):
        self.generation = str(self.generation)

    @validates('generation')
    def validate_generation(self, key, generation):
        return str(generation)

    @property
    def seeds_id(self):
        return f"{str(self.year)[-2:]}{self.variant}"

    @staticmethod
    def parse_id(seeds_id):
        year = f"20{seeds_id[:2]}"
        variant = seeds_id[2:]
        return {'year': year, 'variant': variant}

    @property
    def db_obj(self):
        existing = get_existing(self, ['name', 'category', 'year', 'variant'])
        if existing:
            return existing.get()

def create_all():
    Base.metadata.create_all()
    print("Created all tables.")

def drop_all():
    Base.metadata.drop_all()
    print("Dropped all tables.")

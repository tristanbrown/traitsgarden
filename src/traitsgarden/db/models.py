"""Database models"""
import arrow
import numpy as np
import pandas as pd

from sqlalchemy import Column, asc, desc, Computed
from sqlalchemy.types import Integer, TIMESTAMP, Numeric, String, Date

from .connect import Base, LOCALTZ

class Plant(Base):
    # __tablename__ = 'plant'  ## Only necessary if different from class name

    record = Column(Integer, primary_key=True)
    name = Column(String(length=120), nullable=False)
    species = Column(String(length=120), nullable=False)
    seed = Column(String(length=4), nullable=False)
    individual = Column(String(length=2), nullable=False)
    year = Column(String(length=4), nullable=True)
    start_date = Column(Date, nullable=True)

    # __table_args__ = {'schema': 'garden'}  ## Only necessary with higher-level organization

    def __repr__(self):
        return f"<{self.name} - {self.species} - {self.plant_id}>"

    @property
    def plant_id(self):
        return f"{self.seed}{self.individual.zfill(2)}"

class Seed(Base):

    record = Column(Integer, primary_key=True)
    name = Column(String(length=120), nullable=False)
    species = Column(String(length=120), nullable=False)
    source = Column(String(length=120), nullable=True)
    parent = Column(String(length=10), nullable=True)
    variant = Column(String(length=2), nullable=True)
    year = Column(String(length=4), nullable=True)

    def __repr__(self):
        return f"<{self.name} - {self.species} - {self.seed_id}>"

    @property
    def seed_id(self):
        return f"{self.year[-2:]}{variant}"

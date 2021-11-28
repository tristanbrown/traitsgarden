"""Database models"""
import arrow
import numpy as np
import pandas as pd

from sqlalchemy import Column, asc, desc, Computed
from sqlalchemy.types import Integer, TIMESTAMP, Numeric

from .connect import Base, LOCALTZ

def Now():
    return arrow.now(LOCALTZ).datetime.replace(microsecond=0)

class Plant(Base):
    __tablename__ = 'plant'

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        TIMESTAMP(timezone=True), nullable=False, index=True, unique=True,
        default=Now())

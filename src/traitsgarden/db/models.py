"""Database models"""
import arrow
import numpy as np
import pandas as pd

from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    DateField, DictField, EmbeddedDocumentField,
    EmbeddedDocumentListField, IntField, FileField,
    ListField, MapField, ReferenceField, StringField,
    BooleanField, BinaryField, GridFSProxy,
)
from pymongo.errors import InvalidDocument
from mongoengine import signals
from bson.dbref import DBRef

class Plant(Document):

    name = StringField(max_length=120, required=True)
    species = StringField(max_length=120, required=True)
    fromseeds = ReferenceField('Seeds', required=True)
    individual = StringField(max_length=2, required=True)
    year = StringField(max_length=4)
    start_date = DateField()

    meta = {
        'strict': False,
        'allow_inheritance': True,
        }

    def __repr__(self):
        return f"<{self.name} - {self.species} - {self.plant_id}>"

    @property
    def plant_id(self):
        return f"{self.fromseeds.seeds_id}{self.individual.zfill(2)}"

class Seeds(Document):

    name = StringField(max_length=120, required=True)
    species = StringField(max_length=120, required=True)
    source = StringField(max_length=120)
    parent = ListField(ReferenceField('Plant'))
    variant = StringField(max_length=2, required=True)
    year = StringField(max_length=4)

    def __repr__(self):
        return f"<{self.name} - {self.species} - {self.seeds_id}>"

    @property
    def seeds_id(self):
        return f"{self.year[-2:]}{self.variant}"

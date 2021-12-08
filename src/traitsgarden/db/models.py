"""Database models"""
import arrow
import numpy as np
import pandas as pd

from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    DateField, DictField, EmbeddedDocumentField,
    EmbeddedDocumentListField, IntField, FileField,
    ListField, MapField, ReferenceField, StringField,
    BooleanField, BinaryField, DecimalField, GridFSProxy,
)
from pymongo.errors import InvalidDocument
from mongoengine import signals
from bson.dbref import DBRef

from traitsgarden.db.query import get_existing

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

    def clean(self):
        self.year = str(self.year)

    @property
    def plant_id(self):
        return f"{self.fromseeds.seeds_id}{self.individual.zfill(2)}"

class Seeds(Document):

    name = StringField(max_length=120, required=True)
    category = StringField(max_length=120, required=True)
    species = StringField(max_length=120)
    source = StringField(max_length=120)
    parent = ListField(ReferenceField('Plant'))
    variant = StringField(max_length=2, required=True)
    year = StringField(max_length=4)
    last_count = IntField()
    generation = StringField(max_length=2, default='1')
    germination = DecimalField()
    parent_description = StringField()
    tags = ListField(StringField())

    meta = {
        'indexes': [
            {
                'fields': ('name', 'category', 'year', 'variant'),
                'unique': True
            }
        ]
    }

    def __repr__(self, recursion=False):
        try:
            return f"<{self.name} - {self.category} - {self.seeds_id}>"
        except:
            if recursion:
                raise
            self.clean()
            return self.__repr__(recursion=True)

    def clean(self):
        self.year = str(self.year)
        self.generation = str(self.generation)

    @property
    def seeds_id(self):
        return f"{self.year[-2:]}{self.variant}"

    @property
    def db_obj(self):
        existing = get_existing(self, ['name', 'category', 'year', 'variant'])
        if existing:
            return existing.get()

"""Database models"""
import arrow
import numpy as np
import pandas as pd

from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    DateField, DictField, EmbeddedDocumentField,
    EmbeddedDocumentListField, IntField, FileField,
    ListField, MapField, LazyReferenceField, StringField,
    BooleanField, BinaryField, DecimalField, GridFSProxy,
    FloatField,
)
from pymongo.errors import InvalidDocument
from mongoengine.errors import DoesNotExist
from mongoengine import signals
from bson.dbref import DBRef

from traitsgarden.db.query import get_existing
from traitsgarden.db import util

class Plant(Document):

    name = StringField(max_length=120, required=True)
    category = StringField(max_length=120, required=True)
    species = StringField(max_length=120)
    parent_id = StringField(max_length=4, required=True)
    individual = IntField(required=True, default=1)
    year = IntField()
    start_date = DateField()
    germ_date = DateField()
    flower_date = DateField()
    fruit_date = DateField()
    conditions = StringField()
    growth = StringField()
    height = FloatField()  ## In inches
    fruit_yield = StringField(max_length=120)
    fruit_desc = StringField()
    flavor = StringField()
    variant_notes = StringField()
    tags = ListField(StringField())

    done = BooleanField(default=False)

    meta = {
        'indexes': [
            {
                'fields': ('name', 'category', 'parent_id', 'individual'),
                'unique': True
            }
        ]
    }

    def __repr__(self, recursion=False):
        try:
            return f"<{self.name} - {self.category} - {self.plant_id}>"
        except:
            if recursion:
                raise
            self.clean()
            return self.__repr__(recursion=True)

    def clean(self):
        try:
            indiv_id = ord(self.individual) - 96
            print(indiv_id)
            if (indiv_id >= 1) and (indiv_id <= 26):
                self.individual = indiv_id
        except TypeError:
            pass
        if isinstance(self.height, str):
            self.height = util.convert_to_inches(self.height)

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

class Seeds(Document):

    name = StringField(max_length=120, required=True)
    category = StringField(max_length=120, required=True)
    species = StringField(max_length=120)
    source = StringField(max_length=120)
    parent_plants = ListField(LazyReferenceField('Plant'))
    variant = StringField(max_length=2, required=True)
    year = IntField(required=True)
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
        self.generation = str(self.generation)

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

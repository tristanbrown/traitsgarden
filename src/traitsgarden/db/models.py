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
    parent_seeds = ReferenceField('Seeds', required=True)
    _parent_id = StringField(max_length=4)
    individual = StringField(max_length=2, required=True, default='1')
    year = StringField(max_length=4)
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
                'fields': ('parent_seeds', 'individual'),
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
        self.year = str(self.year)
        self.individual = str(self.individual)
        try:
            self.parent_seeds = self.get_parent_seeds(self._parent_id)
            del self._parent_id
        except DoesNotExist:
            self.parent_seeds = self.create_parent(self._parent_id)
            del self._parent_id
        except (AttributeError, TypeError):
            pass
        if isinstance(self.height, str):
            self.height = util.convert_to_inches(self.height)

    @property
    def plant_id(self):
        return f"{self.parent_seeds.seeds_id}{self.individual.zfill(2)}"

    def get_parent_seeds(self, seeds_id):
        """"""
        parent = Seeds.objects(
            name=self.name,
            category=self.category,
            **Seeds.parse_id(seeds_id)
        )
        return parent.get()

    def create_parent(self, seeds_id):
        """"""
        new_seeds = Seeds(
            name=self.name,
            category=self.category,
            **Seeds.parse_id(seeds_id)
        )
        new_seeds.save()
        return new_seeds

    @property
    def db_obj(self):
        existing = get_existing(self, ['parent_seeds', 'individual'])
        if existing:
            return existing.get()

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

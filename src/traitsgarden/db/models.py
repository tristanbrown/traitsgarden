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
    def add(cls, session, name, category, **kwargs):
        obj = cls(name=name, category=category, **kwargs)
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
    parentage = relationship('SeedParent', lazy='subquery')
    parents = association_proxy('parentage', 'plant')
    is_mother = association_proxy('parentage', 'mother')

    ## Seeds Data
    source = Column(String(length=120))
    last_count = Column(Integer())
    generation = Column(String(length=4), default='1')
    germination = Column(Numeric(2, 2))
    variant_notes = Column(String())

    def __repr__(self, recursion=False):
        return f"<Seeds: {self.name} - {self.category} - {self.pkt_id}>"

    @classmethod
    def query(cls, session, name, category, pkt_id):
        return query_one_obj(session, cls, name=name, category=category, pkt_id=pkt_id)

    @classmethod
    def add(cls, session, name, category, pkt_id=None, **kwargs):
        cultivar = Cultivar.query(session, name, category)
        if cultivar is None:
            cultivar = Cultivar.add(session, name, category)
        if not pkt_id:
            pkt_id = cls.next_pkt_id(session, cultivar)
        year = f"20{pkt_id[0:2]}"
        obj = cls(cultivar=cultivar, pkt_id=pkt_id, year=year, **kwargs)
        session.add(obj)
        return obj

    @classmethod
    def next_pkt_id(cls, session, cultivar):
        """Check the existing pkt_ids and get the next
        incremented pkt_id for a particular cultivar.
        Examples:
        22A -> 22B
        22BZ -> 22CA
        """
        year_label = str(arrow.now().year)[-2:]
        stmt = select(cls.pkt_id).where(
            cls.pkt_id.ilike(f'{year_label}%'),
            cls.name == cultivar.name,
            cls.category == cultivar.category
        ).distinct()
        result = session.execute(stmt)
        pkt_ids = result.scalars().all()
        pkt_ids = util.sort_incremented(pkt_ids)
        if not pkt_ids:
            next_letter = 'A'
        else:
            last_id = pkt_ids[-1]
            next_letter = util.increment_str(last_id[2:])
        return f"{year_label}{next_letter}"

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

    def add_parent(self, session, plant_id, name=None, mother=True):
        """Defaults to the same name/category,
        but others can be specified for crossbreeds.

        Default parent is mother.
        """
        if isinstance(plant_id, int):
            parent_obj = Plant.get(session, plant_id)
        else:
            category = self.category
            if name is None:
                name = self.name
            parent_obj = Plant.query(session, name, category, plant_id)
        self.add_parent_obj(session, parent_obj, mother)

    def add_parent_obj(self, session, parent_plant, mother=True):
        """Default parent is mother."""
        if parent_plant not in self.parents:
            parent_assoc = SeedParent(
                seeds=self, plant=parent_plant, mother=mother)
            session.add(parent_assoc)

    def del_parent(self, session, parent_id):
        parent_ids = [plant.id for plant in self.parents]
        try:
            obj_idx = parent_ids.index(parent_id)
        except ValueError:
            return
        del_obj = self.parentage[obj_idx]
        del_obj.delete(session)

    def update_parents(self, session, parent_ids):
        """Update the parents to only be the given parent_ids.

        parent_ids (dict): {'mothers': [id1, id2], 'fathers': [id3, id4]}
        """
        current_parent_ids = [plant.id for plant in self.parents]
        all_new_parent_ids = parent_ids['mothers'] + parent_ids['fathers']
        ids_to_del = set(current_parent_ids) - set(all_new_parent_ids)
        mothers_to_add = set(parent_ids['mothers']) - set(current_parent_ids)
        fathers_to_add = set(parent_ids['fathers']) - set(current_parent_ids)

        for obj_id in mothers_to_add:
            self.add_parent(session, obj_id, mother=True)
        for obj_id in fathers_to_add:
            self.add_parent(session, obj_id, mother=False)
        for obj_id in ids_to_del:
            self.del_parent(session, obj_id)

    ## Additional attributes

    def get_parents(self, session):
        all_parents = self.parents
        all_types = self.is_mother
        return {
            'mothers': [parent for parent, ismother in zip(all_parents, all_types) if ismother],
            'fathers': [parent for parent, ismother in zip(all_parents, all_types) if not ismother]
        }

class Plant(DBObjMixin, Base):
    __tablename__ = 'plant'

    ## ID Fields
    id = Column(Integer, primary_key=True)
    cultivar_id = Column(Integer, ForeignKey('cultivar.id'), nullable=False)
    cultivar = relationship("Cultivar")
    name = association_proxy('cultivar', 'name')
    category = association_proxy('cultivar', 'category')
    plant_id = Column(String(length=6), nullable=False)
    seeds_id = Column(Integer)
    seeds = relationship('Seeds', #foreign_keys=[seeds_id],
        primaryjoin="foreign(Plant.seeds_id)==Seeds.id"
        )
    ForeignKeyConstraint(
        ['seeds_id'], ['seeds.id'],
        name='fk_plant_seeds_id', use_alter=True
    )

    ## Plant Data
    start_date = Column(Date())
    germ_date = Column(Date())
    pot_up_date = Column(Date())
    final_pot_date = Column(Date())
    flower_date = Column(Date())
    fruit_date = Column(Date())
    died = Column(Date())
    conditions = Column(String())
    growth = Column(String())
    health = Column(String())
    height = Column(Numeric())  ## In inches
    width = Column(Numeric())  ## In inches
    staked = Column(Boolean(), default=False)
    seeds_collected = Column(Boolean(), default=False)
    fruit_yield = Column(String(length=120))
    fruit_desc = Column(String())
    flavor = Column(String())
    brix_sg = Column(Numeric())
    variant_notes = Column(String())
    pros = Column(String())
    cons = Column(String())
    flavor_rating = Column(Integer())
    growth_rating = Column(Integer())
    health_rating = Column(Integer())
    powdery_mildew = Column(String(length=4))
    active = Column(Boolean(), default=False)

    __table_args__ = (
        UniqueConstraint('cultivar_id', 'plant_id', name='_plant_id_uc'),
                     )

    def __repr__(self, recursion=False):
        return f"<Plant: {self.name} - {self.category} - {self.plant_id}>"

    @classmethod
    def query(cls, session, name, category, plant_id):
        return query_one_obj(session, cls, name=name, category=category, plant_id=plant_id)

    @classmethod
    def add(cls, session, name, category, plant_id, **kwargs):
        cultivar = Cultivar.query(session, name, category)
        if cultivar is None:
            cultivar = Cultivar.add(session, name, category)
        pkt_id = plant_id[:3]
        seedparent = Seeds.query(session, name, category, pkt_id)
        obj = cls(cultivar=cultivar, plant_id=plant_id, seeds=seedparent, **kwargs)
        session.add(obj)
        return obj

    @classmethod
    def table(cls):
        query = """SELECT b.name, b.category, c.pkt_id, a.*
            FROM plant a
            JOIN cultivar b
            ON a.cultivar_id = b.id
            LEFT JOIN seeds c
            ON a.seeds_id = c.id
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

class SeedParent(Base, DBObjMixin):
    __tablename__ = 'seedparent'

    ## ID Fields
    seeds_id = Column(Integer, ForeignKey('seeds.id'), primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id'), primary_key=True)

    ## Relationships
    seeds = relationship('Seeds', back_populates='parentage')
    plant = relationship('Plant')

    ## Extra Flags
    mother = Column(Boolean(), default=True, nullable=False)

    @staticmethod
    def table():
        query = """SELECT c1.category, c1.name seeds_name, s.pkt_id,
                c2.name parent_name, p.plant_id, sp.mother
            FROM seeds s
            JOIN cultivar c1
            ON s.cultivar_id = c1.id
            JOIN seedparent sp
            ON s.id = sp.seeds_id
            JOIN plant p
            ON sp.plant_id = p.id
            JOIN cultivar c2
            ON p.cultivar_id = c2.id
            """
        df = query_as_df(query)
        return df

def create_all():
    Base.metadata.create_all()
    print("Created all tables.")

def drop_all():
    close_all_sessions()
    Base.metadata.drop_all()
    print("Dropped all tables.")

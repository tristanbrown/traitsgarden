"""Uploading data to the DB."""

from traitsgarden.db.connect import Session
from traitsgarden.db.models import Cultivar, Seeds, Plant

class LibraryLoader():
    """Upload SeedsLibrary data to the DB."""

    def __init__(self, library=None, parentsmatch=None):
        self.library = library
        self.parentsmatch = parentsmatch

    def upload_table(self, table, model):
        records = table.to_dict(orient='records')
        with Session.begin() as session:
            for record in records:
                model.add(session, **record)

    def upload_cultivars(self):
        self.upload_table(self.library.cultivars, Cultivar)

    def upload_seeds(self):
        table = self.library.seeds.drop('parent', axis=1)
        self.upload_table(table, Seeds)

    def upload_plants(self):
        self.upload_table(self.library.plants, Plant)

    def upload_seedparents(self):
        records = self.parentsmatch.matched_ids.to_dict('records')
        with Session.begin() as session:
            for record in records:
                seedsobj = Seeds.query(session, name=record['seeds_name'], category=record['category'], pkt_id=record['pkt_id'])
                seedsobj.add_parent(session, record['plant_id'], name=record['parent_name'], mother=record['mother'])
                print(seedsobj, seedsobj.parents)

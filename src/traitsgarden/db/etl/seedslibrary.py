"""ETL for getting seeds and cultivars from the Seeds Library spreadsheet."""

import numpy as np
import pandas as pd

class SeedLibrary():
    """Reads and processes the Seed Library data from a spreadsheet."""

    def __init__(self, path):
        self.seeds = self.get_seeds_table(path)
        self.cultivars = self.get_cultivars()

    ## Seeds

    def read_seeds(self, path):
        seed_library = pd.read_excel(path, sheet_name='seed_library')
        return seed_library.dropna(axis=1, how='all')

    def fix_names(self, seed_library):
        """"""
        seed_library = seed_library.copy()
        seed_library['generation'] = seed_library['generation'].fillna('1').astype(str)
        hybrid_subset = seed_library[seed_library['generation'].str.contains('F')]
        unnamed_hybrids = hybrid_subset[~hybrid_subset.apply(lambda x: x['generation'] in x['name'], axis=1)]
        seed_library.loc[unnamed_hybrids.index, 'name'] = seed_library['name'] + ' ' + seed_library['generation']
        return seed_library

    def get_seeds_table(self, path):
        """"""
        seeds_table = self.read_seeds(path)
        seeds_table = self.fix_names(seeds_table)
        seeds_table = seeds_table.drop(['variant', 'parent', 'year'], axis=1
                              ).rename({'id': 'pkt_id', 'parent_description': 'variant_notes'}, axis=1)
        return seeds_table.replace({np.NaN: None})

    ## Cultivars

    def get_cultivars(self):
        """"""
        cult_table = self.seeds[['name', 'category', 'generation', 'variant_notes']].drop_duplicates()
        cult_table.loc[cult_table['generation'].str.contains('F'), 'hybrid'] = True
        cult_table['hybrid'] = cult_table['hybrid'].fillna(False)
        cult_table = cult_table.drop('generation', axis=1).rename({'variant_notes': 'description'}, axis=1).drop_duplicates()
        
        ## Handle duplicates
        dupes = cult_table[cult_table.duplicated(subset=['name', 'category'], keep=False)].sort_values(['name', 'description'])
        dupes_keep = dupes.dropna(subset='description')
        dupes2 = dupes_keep[dupes_keep.duplicated(subset=['name', 'category'], keep=False)].sort_values(['name', 'description'])
        dupes_keep = dupes_keep.drop([36, 37, 34, 161, 43, 73, 12, 14, 17, 13, 145, 146, 152, 54, 55, 158, 79, 128], axis=0)
        dupes_drop = dupes.loc[~dupes.index.isin(dupes_keep.index),:]
        cult_table = cult_table.loc[~cult_table.index.isin(dupes_drop.index),:]

        return cult_table

"""ETL for getting seeds and cultivars from the Seeds Library spreadsheet."""

import numpy as np
import pandas as pd

class SeedLibrary():
    """Reads and processes the Seed Library data from a spreadsheet."""

    def __init__(self, path):
        self.seeds = self.get_seeds_table(path)
        self.cultivars = self.get_cultivars()
        self.plants = self.get_plants_table(path)

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
        seeds_table = seeds_table.drop(['variant', 'year'], axis=1
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

    ## Plants

    def get_plants_table(self, path):
        """"""
        plant_library1 = self.read_plants1(path)
        plant_library2 = self.read_plants2(path)
        print(f"Extra cols 1: {set(plant_library1.columns) - set(plant_library2.columns)}")
        print(f"Extra cols 2: {set(plant_library2.columns) - set(plant_library1.columns)}")
        all_plants = pd.concat([plant_library1, plant_library2], ignore_index=True)
        plants_table = self.fix_plant_names(all_plants)

        ## Clean up columns
        plants_table['active'] = ~(plants_table['done'].fillna(0).astype(bool))
        plants_table = plants_table.drop(['individual', 'parent_id', 'done', 'brix_%'], axis=1
                                      ).rename({'id': 'plant_id'}, axis=1)
        plants_table = plants_table.replace({np.NaN: None})
        return plants_table

    def read_plants1(self, path):
        """"""
        plant_library1 = pd.read_excel(path, sheet_name='2021_plants')
        plant_library1 = plant_library1.dropna(axis=1, how='all')
        plant_library1 = plant_library1.rename(
            {'diseases': 'health'},
            axis=1)
        plant_library1 = plant_library1.drop(['fruit_yield', 'root_depth_in'], axis=1)
        return plant_library1

    def read_plants2(self, path):
        """"""
        plant_library2 = pd.read_excel(path, sheet_name='2022_plants')
        plant_library3 = pd.read_excel(path, sheet_name='2023_plants')
        plant_library2 = pd.concat([plant_library2, plant_library3])
        plant_library2 = plant_library2.dropna(axis=1, how='all')
        plant_library2 = plant_library2.drop(['similar_varieties'], axis=1)
        return plant_library2

    def fix_plant_names(self, all_plants):
        """"""
        all_plants = all_plants.copy()
        cultivars = self.cultivars
        missing_plants = set(all_plants['name']) - set(cultivars['name'])
        plant_names = all_plants['name'].unique()
        cult_names = cultivars['name'].unique()
        name_options = {
            plant_name: [cult_name for cult_name in cult_names if plant_name in cult_name]
            for plant_name in missing_plants
        }
        name_map = {
            'Mango Grape': 'Mango grape',
            'Honey Plus Hybrid': 'Honey Plus Hybrid F1',
            'Dusky Pink Cherry': 'Dusky pink cherry',
            "Burpee's Best Hybrid": "Burpee's Best Hybrid F1",
            'Baby Vilma': 'Baby Vilma F1',
            'Sweetheart of the Patio': 'Sweetheart of the Patio F1',
            'Golden Goose Hybrid': 'Golden Goose Hybrid F1',
            'Cocoa Micro': 'Cocoa Micro F1',
            'Orange Oxheart': 'Orange oxheart',
            'Vilmalos': 'Vilmalos F1',
            'Baby Joke': 'Baby Joke F1',
            'Sun Gold': 'Sun Gold F1',
            'Sunchocola': 'Sunchocola F1'
        }
        all_plants = all_plants.replace(name_map)
        missing_plants = set(all_plants['name']) - set(cultivars['name'])
        print(f"Plants without seeds: {missing_plants}")
        return all_plants

"""ETL for matching parent plants to seeds."""

import re
import pandas as pd

from traitsgarden.db.models import Plant

class ParentsMatch():
    """Match parent descriptions to plants in the database."""

    match_cols = ['category', 'seeds_name', 'pkt_id', 'parent_name', 'plant_id', 'mother']
    
    def __init__(self, library):
        self.library = library[['name', 'category', 'parent', 'id']].rename({'id': 'pkt_id'}, axis=1).copy()
        self.library = self.library.dropna(subset=['parent'])
        self.matches = self.get_all_matches()
        self.matches['parent_name'] = self.rename_parents(self.matches['parent_name'])
        self.matches = self.append_ids(self.matches)

    @property
    def raw_parents(self):
        return self.library['parent'].unique()

    @property
    def unparsed(self):
        matched_seeds = self.matches[['seeds_name', 'category', 'pkt_id']].drop_duplicates()
        matched_seeds['matched'] = True
        seeds_df = pd.merge(
            how='left',
            left=self.library,
            right=matched_seeds.rename({'seeds_name': 'name'}, axis=1),
            on=['category', 'name', 'pkt_id']
        )
        unmatched = seeds_df[seeds_df['matched'].isna()].copy()
        return unmatched.drop('matched', axis=1)

    @property
    def unmatched(self):
        return self.matches[self.matches['parent_id'].isna()]

    @property
    def matched_ids(self):
        return self.matches[~self.matches['parent_id'].isna()]

    ## Process Matches

    def get_all_matches(self):
        """Process all seeds in the library into their parent matches df."""
        all_parents = []
        for record in self.library.to_dict('records'):
            row = self.parse_parents(**record)
            all_parents.append(row)
        return pd.concat(all_parents, ignore_index=True)

    def parse_parents(self, name, category, parent, pkt_id):
        """Parse a parent entry into normal plant IDs.

        Returns a dataframe of all parents for the seed entry.
        """
        parent_rows = []
        if parent_id := single_id(parent):
            parent_rows.append([category, name, pkt_id, prev_gen(name), parent_id[0], True])
        elif parent_ids := find_plant_ids(parent):
            mother = True
            for parent_id in parent_ids:
                parent_rows.append([category, name, pkt_id, parent_id[0], parent_id[1], mother])
                mother=False
        elif '; ' in parent:
            for parent_group in parent.split('; '):
                for parent_id in parse_letter_plantid(parent_group):
                    parent_rows.append([category, name, pkt_id, prev_gen(name), parent_id, True])
        elif parent_ids := parse_letter_plantid(parent):
            for parent_id in parent_ids:
                parent_rows.append([category, name, pkt_id, prev_gen(name), parent_id, True])
        return pd.DataFrame(parent_rows, columns=self.match_cols)

    ## Match Parent Names to Plant IDs

    def rename_parents(self, parent_col):
        micros = ['Vilma', 'Jochalos', 'Baby', 'Rosy Finch', 'Yellow Balcony']
        renames = {
            'Dusky Pink': 'Dusky pink cherry',
            'Pinocchio': 'Pinocchio Orange Micro',
            'Sunchocola': 'Sunchocola F1',
            'Sun Gold': 'Sun Gold F1',
            'Mango Grape': 'Mango grape',
        }
        for name in micros:
            renames[name] = f"{name} Micro"
        return parent_col.replace(renames)

    def append_ids(self, matches):
        """Find the Plant ID integer corresponding to each parent's info."""
        matched = pd.merge(
            how='left',
            left=matches,
            right=Plant.table()[['name', 'category', 'plant_id']].reset_index().rename({'name': 'parent_name'}, axis=1),
            on=['parent_name', 'category', 'plant_id']
        ).rename({'id': 'parent_id'}, axis=1)
        return matched

## Individuals and Hybrids

def single_id(plant_ids):
    regex = r"^[0-9][0-9][A-Z][0-9][0-9]$"
    plant_id = re.findall(regex, plant_ids)
    return plant_id

def prev_gen(seeds_name):
    result = re.match(r"(.*) F([2-9])$", seeds_name)
    if result:
        name, gen = result.groups()
        return f"{name} F{int(gen) - 1}"
    else:
        return seeds_name

def find_plant_ids(parents_line):
    """Find the plant name and ids from a string"""
    try:
        pieces = re.split(', ', parents_line)
    except TypeError:
        return []
    new_parents = []
    for entry in pieces:
        regex = r"[0-9][0-9][A-Z][0-9][0-9]"
        plant_id = re.findall(regex, entry)
        if plant_id:
            plant_id = plant_id[0]
        else:
            continue
        plant_name = entry.rstrip(plant_id).rstrip(' ') or None
        new_parents.append((plant_name, plant_id))
    return new_parents

## letter IDs

def letter_to_num(letter):
    return ord(letter) - 96

def numberize_plant_id(pkt_id, indiv_id):
    return f"{pkt_id}{str(letter_to_num(indiv_id)).zfill(2)}"

def parse_letter_plantid(plant_id):
    regex1 = r"^([0-9][0-9][A-Z])([a-z])"
    regex2 = r",([a-z]*)"
    matches1 = re.match(regex1, plant_id)
    if not matches1:
        return
    pkt_id, first_letter = matches1.groups()
    groups2 = re.findall(regex2, plant_id)
    rest_letters = [letter for letter in groups2 if len(letter) == 1]
    all_letters = [first_letter] + rest_letters
    return [numberize_plant_id(pkt_id, letter) for letter in all_letters]

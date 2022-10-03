import pandas as pd
from datetime import date
from dash import dcc, html, callback, register_page, dash_table
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.query import query_as_df
from traitsgarden.db.models import Plant, Seeds, Cultivar

register_page(__name__, path='/traitsgarden/table')

def layout(name=None):
    table = TableConfig(name)
    return html.Div([
        dcc.Store(id='table-name', data=name),
        html.Br(),
        dash_table.DataTable(
            id='data-table',
            editable=True,
            hidden_columns=table.hidden,
            filter_action='native',
            filter_options={'case': 'insensitive'},
            sort_action='native',
            markdown_options={'link_target': '_self'},
        ),
    ])

@callback(
    Output('data-table', 'data'),
    Output('data-table', 'columns'),
    Input('data-table', 'data_timestamp'),
    State('data-table', 'data'),
    State('table-name', 'data'),
    )
def update_content(timestamp, rows, tablename):
    table = TableConfig(tablename)
    return (
        table.data.to_dict('records'),
        table.columns
    )

class TableConfig():

    def __init__(self, name):
        self._data = pd.DataFrame()
        if name == 'cultivar':
            self.datafunc = get_cultivar_data
            self.hidden = []
            self.linkcols = ['name']
        elif name == 'seeds':
            self.datafunc = get_seeds_data
            self.hidden = ['cultivar_id']
            self.linkcols = ['name', 'pkt_id']
        elif name == 'plant':
            self.datafunc = get_plant_data
            self.hidden = ['cultivar_id', 'seeds_id']
            self.linkcols = ['name', 'pkt_id', 'plant_id']
        else:
            self.datafunc = None
            self.hidden = []
            self.linkcols = []

    @property
    def data(self):
        if (self._data.empty) and (self.datafunc is not None):
            self._data = self.datafunc()
        return self._data

    @property
    def columns(self):
        cols = [{"name": i, "id": i, 'hideable': True} for i in self.data.columns]
        for col in cols:
            if col['name'] in self.linkcols:
                col['presentation'] = 'markdown'
        return cols

def get_cultivar_data():
    df = Cultivar.table().reset_index()
    df['name'] = df.apply(lambda row: f"[{row['name']}](details?cultivarid={row['id']})", axis=1)
    return df

def get_seeds_data():
    df = Seeds.table().reset_index()
    df['name'] = df.apply(lambda row: f"[{row['name']}](details?cultivarid={row['cultivar_id']})", axis=1)
    df['pkt_id'] = df.apply(lambda row: f"[{row['pkt_id']}](details?seedsid={row['id']})", axis=1)
    return df

def get_plant_data():
    df = Plant.table().reset_index()
    df['name'] = df.apply(lambda row: f"[{row['name']}](details?cultivarid={row['cultivar_id']})", axis=1)
    df['pkt_id'] = df.apply(lambda row: f"[{row['pkt_id']}](details?seedsid={row['seeds_id']})", axis=1)
    df['plant_id'] = df.apply(lambda row: f"[{row['plant_id']}](details?plantid={row['id']})", axis=1)
    return df

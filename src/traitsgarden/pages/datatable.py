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
    table = select_table(name)
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
    table = select_table(tablename)
    return (
        table.data.to_dict('records'),
        table.columns
    )

def select_table(name):
    selector = {
        'cultivar': TableCultivar,
        'seeds': TableSeeds,
        'plant': TablePlant,
    }
    return selector.get(name, TableBase)()

class TableBase():

    typemap = {
        int: 'numeric',
        float: 'numeric',
        'object': 'text',
        bool: 'any',
        'datetime64[ns]': 'datetime',
    }

    def __init__(self):
        self.data = self.get_data().fillna('')
        self.hidden = []
        self.linkcols = []

    def get_data(self):
        return pd.DataFrame()

    @property
    def columns(self):
        coltypes = self.data.dtypes.replace(self.typemap)
        cols = [{"name": i, "id": i, 'type': coltypes.loc[i],
            'hideable': True} for i in self.data.columns]
        for col in cols:
            if col['name'] in self.linkcols:
                col['presentation'] = 'markdown'
        return cols

class TableCultivar(TableBase):

    def __init__(self):
        super().__init__()
        self.hidden = []
        self.linkcols = ['name']

    def get_data(self):
        df = Cultivar.table().reset_index()
        df['name'] = df.apply(lambda row: f"[{row['name']}](details?cultivarid={row['id']})", axis=1)
        return df

class TableSeeds(TableBase):

    def __init__(self):
        super().__init__()
        self.hidden = ['cultivar_id']
        self.linkcols = ['name', 'pkt_id']

    def get_data(self):
        df = Seeds.table().reset_index()
        df['name'] = df.apply(lambda row: f"[{row['name']}](details?cultivarid={row['cultivar_id']})", axis=1)
        df['pkt_id'] = df.apply(lambda row: f"[{row['pkt_id']}](details?seedsid={row['id']})", axis=1)
        return df

class TablePlant(TableBase):

    def __init__(self):
        super().__init__()
        self.hidden = ['cultivar_id', 'seeds_id']
        self.linkcols = ['name', 'pkt_id', 'plant_id']

    def get_data(self):
        df = Plant.table().reset_index()
        df['name'] = df.apply(lambda row: f"[{row['name']}](details?cultivarid={row['cultivar_id']})", axis=1)
        df['pkt_id'] = df.apply(lambda row: f"[{row['pkt_id']}](details?seedsid={row['seeds_id']})", axis=1)
        df['plant_id'] = df.apply(lambda row: f"[{row['plant_id']}](details?plantid={row['id']})", axis=1)
        return df

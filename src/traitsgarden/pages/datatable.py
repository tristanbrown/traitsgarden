from datetime import date
from dash import dcc, html, callback, register_page, dash_table
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.query import query_as_df
from traitsgarden.db.models import Plant, Seeds, Cultivar

register_page(__name__, path='/traitsgarden/table')

def layout(name=None):
    if name == 'seeds':
        default_hidden = ['cultivar_id']
    else:
        default_hidden = []

    return html.Div([
        dcc.Store(id='table-name', data=name),
        html.Br(),
        dash_table.DataTable(
            id='data-table',
            editable=True,
            hidden_columns=default_hidden,
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
    if tablename == 'seeds':
        df = get_seeds_data()
        linkcols = ['id', 'name']
    else:
        df = None
        linkcols = []

    if df is None:
        return [{}], []
    cols = [{"name": i, "id": i, 'hideable': True} for i in df.columns]
    for col in cols:
        if col['name'] in linkcols:
            col['presentation'] = 'markdown'
    return (
        df.to_dict('records'),
        cols
    )

def get_seeds_data():
    with Session.begin() as session:
        query = """SELECT b.name, b.category, a.*
            FROM seeds a
            JOIN cultivar b
            ON a.cultivar_id = b.id
            """
        df = query_as_df(query)
    df = df.set_index(['id', 'cultivar_id']).reset_index()
    df['name'] = df.apply(lambda row: f"[{row['name']}](details?cultivarid={row['cultivar_id']})", axis=1)
    df['id'] = df.apply(lambda row: f"[{row['id']}](details?seedsid={row['id']})", axis=1)
    return df

from datetime import date
from dash import dcc, html, callback, register_page, dash_table
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.query import query_as_df
from traitsgarden.db.models import Plant, Seeds, Cultivar

register_page(__name__, path='/traitsgarden/seedstable')

def layout(**kwargs):
    return html.Div([
        html.Br(),
        dash_table.DataTable(
            id='seeds-table',
            editable=True,
        ),
    ])

@callback(
    Output('seeds-table', 'data'),
    Output('seeds-table', 'columns'),
    Input('seeds-table', 'data_timestamp'),
    State('seeds-table', 'data'))
def update_content(timestamp, rows):
    df = get_seeds_data()

    if df is None:
        return [{}], []
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]

def get_seeds_data():
    with Session.begin() as session:
        return query_as_df('seeds')

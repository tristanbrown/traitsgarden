from datetime import date
from dash import dcc, html, callback, register_page, dash_table
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar

register_page(__name__, path='/traitsgarden/seedstable')

layout = html.Div([
    html.Br(),
    dash_table.DataTable(
        id='computed-table',
        columns=[
            {'name': 'Input Data', 'id': 'input-data'},
            {'name': 'Input Squared', 'id': 'output-data'}
        ],
        data=[{'input-data': i} for i in range(11)],
        editable=True,
    ),
])

@callback(
    Output('computed-table', 'data'),
    Input('computed-table', 'data_timestamp'),
    State('computed-table', 'data'))
def update_columns(timestamp, rows):
    for row in rows:
        try:
            row['output-data'] = float(row['input-data']) ** 2
        except:
            row['output-data'] = 'NA'
    return rows

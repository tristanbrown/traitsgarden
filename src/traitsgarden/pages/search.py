from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant

options = [
    {"label": "New York City", "value": "NYC"},
    {"label": "Montreal", "value": "MTL"},
    {"label": "San Francisco", "value": "SF"},
]

layout = html.Div([
    html.Div([
        "Category",
        dcc.Dropdown(id="category-dropdown")
    ]),
    html.Div([
        "Name",
        dcc.Dropdown(id="name-dropdown")
    ]),
    html.Div([
        "Seeds ID",
        dcc.Dropdown(id="pkt-id-dropdown")
    ]),
    html.Button(id='button-search', n_clicks=0, children='Search'),
    html.Div(id='dd-output-container'),
])

@callback(
    Output("category-dropdown", "options"),
    Input("category-dropdown", "search_value")
)
def update_options(search_value):
    if not search_value:
        search_value = ''
    return [o for o in options if search_value in o["label"]]

@callback(
    Output('dd-output-container', 'children'),
    Input('button-search', 'n_clicks'),
    State('category-dropdown', 'value')
)
def update_output(n_clicks, value):
    return f'You have selected {value}'

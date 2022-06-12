from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant
from traitsgarden.db.query import query_as_df

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
    html.Div(id='dd-output-container'),
])

@callback(
    Output("category-dropdown", "options"),
    Input("category-dropdown", "search_value")
)
def update_options(search_value):
    if not search_value:
        search_value = ''
    query = f"""SELECT category
        FROM cultivar
        WHERE LOWER(category) LIKE LOWER('%%{search_value}%%')"""
    result = query_as_df(query)
    return list(result['category'].unique())

@callback(
    Output("name-dropdown", "options"),
    Input("name-dropdown", "search_value"),
    Input("category-dropdown", "value"),
)
def update_options(search_value, category):
    if not search_value:
        search_value = ''
    query = f"""SELECT name
        FROM cultivar
        WHERE LOWER(name) LIKE LOWER('%%{search_value}%%')
        """
    if category:
        query += f"""AND LOWER(category) = LOWER('{category}')"""
    result = query_as_df(query)
    return list(result['name'].unique())

@callback(
    Output('dd-output-container', 'children'),
    Input('category-dropdown', 'value'),
    Input('name-dropdown', 'value'),
    Input('pkt-id-dropdown', 'value'),
)
def update_output(category, name, pkt_id):
    return f'You have selected {category}, {name}, {pkt_id}'

from sqlalchemy import select
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds
from traitsgarden.db.query import query_as_df, query_orm

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
        dcc.Dropdown(id="seedsid-dropdown")
    ]),
    html.Div(id='dd-output-container'),
])

@callback(
    Output("category-dropdown", "options"),
    Input("category-dropdown", "search_value")
)
def update_category(search_value):
    if not search_value:
        search_value = ''
    query = f"""SELECT category
        FROM cultivar
        WHERE category ILIKE '%%{search_value}%%'"""
    result = query_as_df(query)
    return list(result['category'].unique())

@callback(
    Output("name-dropdown", "options"),
    Input("name-dropdown", "search_value"),
    Input("category-dropdown", "value"),
)
def update_name(search_value, category):
    if not search_value:
        search_value = ''
    query = f"""SELECT name
        FROM cultivar
        WHERE name ILIKE '%%{search_value}%%'
        """
    if category:
        query += f"""AND category ILIKE '{category}'"""
    result = query_as_df(query)
    return list(result['name'].unique())

@callback(
    Output("seedsid-dropdown", "options"),
    Input("seedsid-dropdown", "search_value"),
    Input("name-dropdown", "value"),
    Input("category-dropdown", "value"),
)
def update_seedsid(search_value, name, category):
    if not search_value:
        search_value = ''
    stmt = select(Seeds).where(
        Seeds.pkt_id.ilike(f'{search_value}%')
    )
    if name:
        stmt = stmt.where(
            Seeds.name.ilike(name)
        )
    if category:
        stmt = stmt.where(
            Seeds.category.ilike(category)
        )
    with Session.begin() as session:
        result = query_orm(session, stmt)
        pkt_ids = {obj.pkt_id for obj in result}
    return list(pkt_ids)

@callback(
    Output('dd-output-container', 'children'),
    Input('category-dropdown', 'value'),
    Input('name-dropdown', 'value'),
    Input('seedsid-dropdown', 'value'),
)
def update_output(category, name, seedsid):
    return f'You have selected {category}, {name}, {seedsid}'

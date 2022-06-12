from sqlalchemy import select
from dash import dcc, html, callback, ctx, register_page
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_as_df, query_orm

register_page(__name__, path="/traitsgarden/search")

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
    html.Div([
        "Plant ID",
        dcc.Dropdown(id="plantid-dropdown")
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
    stmt = select(Cultivar).where(
        Cultivar.category.ilike(f'%{search_value}%')
    )
    with Session.begin() as session:
        result = query_orm(session, stmt)
        cats = {obj.category for obj in result}
    return list(cats)

@callback(
    Output("name-dropdown", "options"),
    Input("name-dropdown", "search_value"),
    Input("category-dropdown", "value"),
)
def update_name(search_value, category):
    if not search_value:
        search_value = ''
    stmt = select(Cultivar).where(
        Cultivar.name.ilike(f'%{search_value}%')
    )
    if category:
        stmt = stmt.where(Cultivar.category == category)
    with Session.begin() as session:
        result = query_orm(session, stmt)
        names = {obj.name for obj in result}
    return list(names)

@callback(
    Output("seedsid-dropdown", "options"),
    Input("seedsid-dropdown", "search_value"),
    Input("name-dropdown", "value"),
    Input("category-dropdown", "value"),
)
def update_seedsid(search_value, name, category):
    if not name:
        return []
    if not search_value:
        search_value = ''
    stmt = select(Seeds).where(
        Seeds.pkt_id.ilike(f'{search_value}%')
    )
    if name:
        stmt = stmt.where(Seeds.name == name)
    if category:
        stmt = stmt.where(Seeds.category == category)
    with Session.begin() as session:
        result = query_orm(session, stmt)
        pkt_ids = {obj.pkt_id for obj in result}
    return list(pkt_ids)

@callback(
    Output("plantid-dropdown", "options"),
    Input("plantid-dropdown", "search_value"),
    Input("name-dropdown", "value"),
    Input("category-dropdown", "value"),
)
def update_plantid(search_value, name, category):
    if not name:
        return []
    if not search_value:
        search_value = ''
    stmt = select(Plant).where(
        Plant.plant_id.ilike(f'{search_value}%')
    )
    if name:
        stmt = stmt.where(Plant.name == name)
    if category:
        stmt = stmt.where(Plant.category == category)
    with Session.begin() as session:
        result = query_orm(session, stmt)
        plant_ids = {obj.plant_id for obj in result}
    return list(plant_ids)

@callback(
    Output("seedsid-dropdown", "value"),
    Output("plantid-dropdown", "value"),
    Input("seedsid-dropdown", "value"),
    Input("plantid-dropdown", "value"),
)
def seedsid_plantid_exclusive(seedsid, plantid):
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if trigger_id == 'seedsid-dropdown':
        result = (seedsid, None)
    elif trigger_id == 'plantid-dropdown':
        result = (None, plantid)
    else:
        raise PreventUpdate
    return result

@callback(
    Output('dd-output-container', 'children'),
    Input('category-dropdown', 'value'),
    Input('name-dropdown', 'value'),
    Input('seedsid-dropdown', 'value'),
    Input('plantid-dropdown', 'value'),
)
def update_output(category, name, seedsid, plantid):
    return f'You have selected {category}, {name}, {seedsid}, {plantid}'

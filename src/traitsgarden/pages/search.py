from sqlalchemy import select
from dash import dcc, html, callback, ctx, register_page
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm

register_page(__name__, path='/traitsgarden/search')

layout = html.Div([
    html.Div([
        "Cultivar",
        dcc.Dropdown(id="cultivar-dropdown")
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
    html.Br(),
    dcc.Link(
        html.Button('Search'),
        id='search-link',
        href='',
        )
])

@callback(
    Output("cultivar-dropdown", "options"),
    Input("cultivar-dropdown", "search_value"),
)
def update_cultivar(search_value):
    if not search_value:
        search_value = ''
    stmt = select(Cultivar).where(
        Cultivar.name.ilike(f'%{search_value}%') |\
        Cultivar.category.ilike(f'%{search_value}%')
    )
    with Session.begin() as session:
        result = query_orm(session, stmt)
        cultivars = {
            f"{obj.category} | {obj.name}": f"{obj.name} ({obj.category})" for obj in result}
    return cultivars

@callback(
    Output("seedsid-dropdown", "options"),
    Input("seedsid-dropdown", "search_value"),
    Input("cultivar-dropdown", "value"),
)
def update_seedsid(search_value, cultivar):
    if not cultivar:
        return []
    if not search_value:
        search_value = ''
    stmt = select(Seeds).where(
        Seeds.pkt_id.ilike(f'{search_value}%')
    )
    if cultivar:
        category, name = parse_cultivar(cultivar)
        stmt = stmt.where(
            Seeds.name == name, Seeds.category == category)
    with Session.begin() as session:
        result = query_orm(session, stmt)
        pkt_ids = {obj.pkt_id for obj in result}
    return list(pkt_ids)

@callback(
    Output("plantid-dropdown", "options"),
    Input("plantid-dropdown", "search_value"),
    Input("cultivar-dropdown", "value"),
)
def update_plantid(search_value, cultivar):
    if not cultivar:
        return []
    if not search_value:
        search_value = ''
    stmt = select(Plant).where(
        Plant.plant_id.ilike(f'{search_value}%')
    )
    if cultivar:
        category, name = parse_cultivar(cultivar)
        stmt = stmt.where(
            Plant.name == name, Plant.category == category)
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
    Input('cultivar-dropdown', 'value'),
    Input('seedsid-dropdown', 'value'),
    Input('plantid-dropdown', 'value'),
)
def update_output(cultivar, seedsid, plantid):
    category, name = parse_cultivar(cultivar)
    return f'You have selected {category}, {name}, {seedsid}, {plantid}'

@callback(
    Output('search-link', 'href'),
    Input('cultivar-dropdown', 'value'),
    Input('seedsid-dropdown', 'value'),
    Input('plantid-dropdown', 'value'),
)
def search_go(cultivar, seedsid, plantid):
    category, name = parse_cultivar(cultivar)
    with Session.begin() as session:
        if plantid:
            obj = Plant.query(session, name, category, plantid)
            itemtype = 'plant'
        elif seedsid:
            obj = Seeds.query(session, name, category, seedsid)
            itemtype = 'seeds'
        else:
            obj = Cultivar.query(session, name, category)
            itemtype = 'cultivar'
        if obj:
                return f"/traitsgarden/details?{itemtype}id={obj.id}"
    raise PreventUpdate

def parse_cultivar(label):
    try:
        category, name = label.split(' | ')
    except AttributeError:
        category = name = None
    return category, name

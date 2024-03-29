import json
from sqlalchemy import select
from dash import dcc, html, callback, ctx
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm

search_bar = dbc.Row([
    dbc.Col(dcc.Dropdown(id={'type': 'cultivar-select', 'index': 'search'}, placeholder="Cultivar",), width=3),
    dbc.Col(dcc.Dropdown(id={'type': 'seedsid-dropdown', 'index': 'search'}, placeholder="Seeds ID",), width=3),
    dbc.Col(dcc.Dropdown(id={'type': 'plantid-dropdown', 'index': 'search'}, placeholder="Plant ID",), width=3),
    dbc.Col(dcc.Link(
        dbc.Button('Search'),
        id='search-link',
        href='',
        ))
    ],
    className="flex-grow-1 flex-wrap",
    align="right",
)

search_col = dbc.Row([
    dbc.Col(dcc.Dropdown(id={'type': 'cultivar-select', 'index': 'search'}, placeholder="Cultivar",), width=12),
    dbc.Col(dcc.Dropdown(id={'type': 'seedsid-dropdown', 'index': 'search'}, placeholder="Seeds ID",), width=12),
    dbc.Col(dcc.Dropdown(id={'type': 'plantid-dropdown', 'index': 'search'}, placeholder="Plant ID",), width=12),
    dbc.Col(dcc.Link(
        dbc.Button('Search', id='search-button', n_clicks=0),
        id='search-link',
        href='',
        ))
    ],
    className="flex-grow-1 flex-wrap",
    align="center",
)

@callback(
    Output({'type': 'seedsid-dropdown', 'index': MATCH}, "options"),
    Input({'type': 'seedsid-dropdown', 'index': MATCH}, "search_value"),
    Input({'type': 'cultivar-select', 'index': MATCH}, "value"),
)
def update_seedsid(search_value, cultivar):
    return update_search_ids(search_value, cultivar, Seeds)

@callback(
    Output({'type': 'plantid-dropdown', 'index': MATCH}, "options"),
    Input({'type': 'plantid-dropdown', 'index': MATCH}, "search_value"),
    Input({'type': 'cultivar-select', 'index': MATCH}, "value"),
)
def update_plantid(search_value, cultivar):
    return update_search_ids(search_value, cultivar, Plant)

def update_search_ids(search_value, cultivar, model):
    id_type = {
        Seeds: 'pkt_id',
        Plant: 'plant_id'
    }
    model_id = id_type[model]

    if not cultivar:
        return []
    if not search_value:
        search_value = ''
    stmt = select(model).where(
        getattr(model, model_id).ilike(f'{search_value}%')
    )
    if cultivar:
        category, name = parse_cultivar(cultivar)
        stmt = stmt.where(
            model.name == name, model.category == category)
    with Session.begin() as session:
        result = query_orm(session, stmt)
        obj_ids = {getattr(obj, model_id) for obj in result}
    return sorted(list(obj_ids))

@callback(
    Output({'type': 'seedsid-dropdown', 'index': 'search'}, "value"),
    Output({'type': 'plantid-dropdown', 'index': 'search'}, "value"),
    Input({'type': 'seedsid-dropdown', 'index': 'search'}, "value"),
    Input({'type': 'plantid-dropdown', 'index': 'search'}, "value"),
)
def seedsid_plantid_exclusive(seedsid, plantid):
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if not trigger_id:
        raise PreventUpdate
    trigger_label = json.loads(trigger_id)['type']
    if trigger_label == 'seedsid-dropdown':
        result = (seedsid, None)
    elif trigger_label == 'plantid-dropdown':
        result = (None, plantid)
    return result

@callback(
    Output('dd-output-container', 'children'),
    Input({'type': 'cultivar-select', 'index': 'search'}, 'value'),
    Input({'type': 'seedsid-dropdown', 'index': 'search'}, 'value'),
    Input({'type': 'plantid-dropdown', 'index': 'search'}, 'value'),
)
def update_output(cultivar, seedsid, plantid):
    category, name = parse_cultivar(cultivar)
    return f'You have selected {category}, {name}, {seedsid}, {plantid}'

@callback(
    Output('search-link', 'href'),
    Input({'type': 'cultivar-select', 'index': 'search'}, 'value'),
    Input({'type': 'seedsid-dropdown', 'index': 'search'}, 'value'),
    Input({'type': 'plantid-dropdown', 'index': 'search'}, 'value'),
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
                return f"details?{itemtype}id={obj.id}"
    raise PreventUpdate

def parse_cultivar(label):
    try:
        name, category = label.split('|')
    except AttributeError:
        category = name = None
    return category, name

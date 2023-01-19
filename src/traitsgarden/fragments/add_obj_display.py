from sqlalchemy import select
from dash import dcc, html, callback, callback_context, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.shared import dropdown_options_input

def add_display_modal(objname, name=None, category=None):
    index = f"add-{objname}"
    if name and category:
        cultivar = f"{name}|{category}"
    else:
        cultivar = None
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(f"Add {objname.capitalize()}", id='dialogue-title')),
        dbc.ModalBody([
            dcc.Dropdown(id={'type': 'cultivar_select', 'index': index},
                placeholder="Cultivar", value=cultivar),
            dbc.Input(id={'type': 'basic-input', 'index': index},
                placeholder=f'{objname.capitalize()} ID (optional)')
            ]),
        dbc.ModalFooter([
                dcc.Location(id={'type': 'save-redirect', 'index': index}, refresh=True),
                dbc.Button("Save", id={'type': 'save-dialogue', 'index': index}),
                ])
    ], id={'type': 'dialogue', 'index': index})

@callback(
    Output({'type': 'dialogue', 'index': MATCH}, "is_open"),
    [Input({'type': 'open-dialogue', 'index': MATCH}, "n_clicks"),
    Input({'type': 'save-dialogue', 'index': MATCH}, "n_clicks")],
    [State({'type': 'dialogue', 'index': MATCH}, "is_open")],
)
def toggle_dialogue(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

@callback(
    Output({'type': 'cultivar_select', 'index': MATCH}, "options"),
    Input({'type': 'cultivar_select', 'index': MATCH}, "search_value"),
    Input({'type': 'cultivar_select', 'index': MATCH}, "value"),
)
def update_cultivar_options(search_value, input_value):
    if not search_value:
        search_value = ''
    stmt = select(Cultivar.name, Cultivar.category).where(
        Cultivar.name.ilike(f'%{search_value}%')
    ).distinct().order_by(Cultivar.name)
    with Session.begin() as session:
        result = session.execute(stmt)
    return [{'label': f"{name} ({cat})", 'value': f"{name}|{cat}"} \
        for name, cat in result]

@callback(
    Output({'type': 'cultivar_select', 'index': MATCH}, 'value'),
    Output({'type': 'basic-input', 'index': MATCH}, 'value'),
    Output({'type': 'save-redirect', 'index': MATCH}, 'href'),
    Input({'type': 'save-dialogue', 'index': MATCH}, 'n_clicks'),
    State({'type': 'save-dialogue', 'index': MATCH}, 'id'),
    State({'type': 'basic-input', 'index': MATCH}, 'value'),
    State({'type': 'cultivar_select', 'index': MATCH}, 'value'),
    prevent_initial_call=True,
)
def save_changes(n_clicks, index, obj_id, cultivar):
    objtype = index['index'].split('-')[-1]
    models = {'seeds': Seeds, 'plant': Plant}
    model = models[objtype]
    name, category = cultivar.split('|')
    with Session.begin() as session:
        obj = model.add(session, name, category, obj_id)
        if objtype == 'seeds':
            obj_id = obj.pkt_id
        elif objtype == 'plant':
            obj_id = obj.plant_id
    with Session.begin() as session:
        obj = model.query(session, name, category, obj_id)
        if obj:
            return None, None, f"/traitsgarden/details?{objtype}id={obj.id}"
    return None, None, ''

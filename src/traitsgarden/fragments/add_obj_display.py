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
            dcc.Dropdown(id={'type': 'cultivar-select', 'index': index},
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

def get_objsave_inputs(index):
    return [
        Output({'type': 'cultivar-select', 'index': index}, 'value'),
        Output({'type': 'basic-input', 'index': index}, 'value'),
        Output({'type': 'save-redirect', 'index': index}, 'href'),
        Input({'type': 'save-dialogue', 'index': index}, 'n_clicks'),
        State({'type': 'basic-input', 'index': index}, 'value'),
        State({'type': 'cultivar-select', 'index': index}, 'value'),
    ]

@callback(
    *get_objsave_inputs('add-seeds'),
    prevent_initial_call=True,
)
def save_seeds_changes(n_clicks, obj_id, cultivar):
    name, category = cultivar.split('|')
    with Session.begin() as session:
        obj = Seeds.add(session, name, category, obj_id)
        obj_id = obj.pkt_id
    with Session.begin() as session:
        obj = Seeds.query(session, name, category, obj_id)
        if obj:
            return None, None, f"details?seedsid={obj.id}"
    return None, None, ''

@callback(
    *get_objsave_inputs('add-plant'),
    prevent_initial_call=True,
)
def save_plant_changes(n_clicks, obj_id, cultivar):
    name, category = cultivar.split('|')
    with Session.begin() as session:
        obj = Plant.add(session, name, category, obj_id)
        obj_id = obj.plant_id
    with Session.begin() as session:
        obj = Plant.query(session, name, category, obj_id)
        if obj:
            return None, None, f"details?plantid={obj.id}"
    return None, None, ''

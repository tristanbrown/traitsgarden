from sqlalchemy import select
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.shared import dropdown_options_input

cultivar_dropdown = dcc.Dropdown(id="add-obj-cultivar", placeholder="Cultivar")

seeds_add_display = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add Seeds")),
        dbc.ModalBody([
            cultivar_dropdown,
            dbc.Input(id="add-seeds-input", placeholder='Seeds ID (optional)')
            ]),
        dbc.ModalFooter([
                dcc.Location(id='add-seeds-link', refresh=True),
                dbc.Button("Save", id={'type': 'save-new-obj', 'index': "add-seeds"}),
                ])
    ], id={'type': 'add-modal', 'index': 'add-seeds'})

@callback(
    Output({'type': 'add-modal', 'index': MATCH}, "is_open"),
    [Input({'type': 'add-obj', 'index': MATCH}, "n_clicks"),
    Input({'type': 'save-new-obj', 'index': MATCH}, "n_clicks")],
    [State({'type': 'add-modal', 'index': MATCH}, "is_open")],
)
def toggle_add_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

@callback(
    Output("add-obj-cultivar", "options"),
    Input("add-obj-cultivar", "search_value"),
    Input("add-obj-cultivar", "value"),
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
    Output('add-obj-cultivar', 'value'),
    Output('add-seeds-input', 'value'),
    Output('add-seeds-link', 'href'),
    Input({'type': 'save-new-obj', 'index': 'add-seeds'}, 'n_clicks'),
    State('add-seeds-input', 'value'),
    State('add-obj-cultivar', 'value'),
    prevent_initial_call=True,
)
def save_changes(n_clicks, pkt_id, cultivar):
    name, category = cultivar.split('|')
    with Session.begin() as session:
        obj = Seeds.add(session, name, category, pkt_id)
        pkt_id = obj.pkt_id
    with Session.begin() as session:
        obj = Seeds.query(session, name, category, pkt_id)
        if obj:
            return None, None, f"/traitsgarden/details?seedsid={obj.id}"
    return None, None, ''

from sqlalchemy import select
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.shared import dropdown_options_input

seeds_add_display = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add Seeds")),
        dbc.ModalBody([
            dbc.Row(dbc.Col(dbc.Input(id="add-seeds-input", placeholder='Seeds Name'))),
            dbc.Row(dbc.Col(dcc.Dropdown(id="add-seeds-cultivar", placeholder="Cultivar",)))
            ]),
        dbc.ModalFooter([
                dcc.Location(id='add-seeds-link', refresh=True),
                dbc.Button("Save", id="save-new-seeds"),
                ])
    ], id="add-seeds-modal")

@callback(
    Output("add-seeds-modal", "is_open"),
    [Input("add-seeds", "n_clicks"), Input("save-new-seeds", "n_clicks")],
    [State("add-seeds-modal", "is_open")],
)
def toggle_addseeds_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

# @callback(
#     Output("add-seeds-cultivar", "options"),
#     Input("add-seeds-cultivar", "search_value"),
#     Input("add-seeds-cultivar", "value"),
# )
# @dropdown_options_input
# def update_category_dropdown(search_value, input_value):
#     stmt = select(Seeds.category).where(
#         Seeds.category.ilike(f'%{search_value}%')
#     ).distinct()
#     with Session.begin() as session:
#         result = query_orm(session, stmt)
#     return result

# @callback(
#     Output('add-seeds-cultivar', 'value'),
#     Output('add-seeds-input', 'value'),
#     Output('add-seeds-link', 'href'),
#     Input('save-new-seeds', 'n_clicks'),
#     State('add-seeds-input', 'value'),
#     State('add-seeds-cultivar', 'value'),
#     prevent_initial_call=True,
# )
# def save_changes(n_clicks, seeds_name, category):
#     with Session.begin() as session:
#         obj = Seeds.add(session, seeds_name, category)
#     with Session.begin() as session:
#         obj = Seeds.query(session, seeds_name, category)
#         if obj:
#             return None, None, f"/traitsgarden/details?seedsid={obj.id}"
#     return None, None, ''

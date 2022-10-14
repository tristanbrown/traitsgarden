from sqlalchemy import select
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.shared import dropdown_options_input

cultivar_add_display = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Add Cultivar")),
        dbc.ModalBody([
            dbc.Row(dbc.Col(dbc.Input(id="add-cultivar-input", placeholder='Cultivar Name'))),
            dbc.Row(dbc.Col(dcc.Dropdown(id="add-category-dropdown", placeholder="Category",)))
            ]),
        dbc.ModalFooter([
                dcc.Location(id='add-cultivar-link', refresh=True),
                dbc.Button("Save", id="save-new-cultivar"),
                ])
    ], id="add-cultivar-modal")

@callback(
    Output("add-cultivar-modal", "is_open"),
    [Input("add-cultivar-open", "n_clicks"), Input("save-new-cultivar", "n_clicks")],
    [State("add-cultivar-modal", "is_open")],
)
def toggle_addcultivar_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

@callback(
    Output("add-category-dropdown", "options"),
    Input("add-category-dropdown", "search_value"),
    Input("add-category-dropdown", "value"),
)
@dropdown_options_input
def update_category_dropdown(search_value, input_value):
    stmt = select(Cultivar.category).where(
        Cultivar.category.ilike(f'%{search_value}%')
    ).distinct()
    with Session.begin() as session:
        result = query_orm(session, stmt)
    return result

@callback(
    Output('add-category-dropdown', 'value'),
    Output('add-cultivar-input', 'value'),
    Output('add-cultivar-link', 'href'),
    Input('save-new-cultivar', 'n_clicks'),
    State('add-cultivar-input', 'value'),
    State('add-category-dropdown', 'value'),
    prevent_initial_call=True,
)
def save_changes(n_clicks, cultivar_name, category):
    with Session.begin() as session:
        obj = Cultivar.add(session, cultivar_name, category)
    with Session.begin() as session:
        obj = Cultivar.query(session, cultivar_name, category)
        if obj:
            return None, None, f"/traitsgarden/details?cultivarid={obj.id}"
    return None, None, ''

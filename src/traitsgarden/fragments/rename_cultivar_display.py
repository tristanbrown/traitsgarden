from sqlalchemy import select
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.shared import dropdown_options_input

def cultivar_rename_display(obj_id):
    with Session.begin() as session:
        obj = Cultivar.get(session, obj_id)
        objname = obj.name
        category = obj.category
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Rename Cultivar")),
        dbc.ModalBody([
            dbc.Row(dbc.Col(dbc.Input(id="rename-cultivar-input", placeholder='Cultivar Name', value=objname))),
            dbc.Row(dbc.Col(dcc.Dropdown(id="rename-category-dropdown", placeholder="Category", value=category)))
            ]),
        dbc.ModalFooter([
                dcc.Location(id='rename-cultivar-link', refresh=True),
                dbc.Button("Save", id="save-renamed-cultivar"),
                ])
    ], id="rename-cultivar-modal")

@callback(
    Output("rename-cultivar-modal", "is_open"),
    [Input("rename-cultivar-open", "n_clicks"), Input("save-renamed-cultivar", "n_clicks")],
    [State("rename-cultivar-modal", "is_open")],
)
def toggle_renamecultivar_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

@callback(
    Output("rename-category-dropdown", "options"),
    Input("rename-category-dropdown", "search_value"),
    Input("rename-category-dropdown", "value"),
)
@dropdown_options_input
def update_category_dropdown(search_value, input_value):
    stmt = select(Cultivar.category).where(
        Cultivar.category.ilike(f'%{search_value}%')
    ).distinct().order_by(Cultivar.category)
    with Session.begin() as session:
        result = session.execute(stmt).scalars().all()
    return result

@callback(
    Output('rename-category-dropdown', 'value'),
    Output('rename-cultivar-input', 'value'),
    Output('rename-cultivar-link', 'href'),
    Input('save-renamed-cultivar', 'n_clicks'),
    State('ids', 'data'),
    State('rename-cultivar-input', 'value'),
    State('rename-category-dropdown', 'value'),
    prevent_initial_call=True,
)
def save_changes(n_clicks, ids, cultivar_name, category):
    with Session.begin() as session:
        obj_id = ids['cultivar']
        obj = Cultivar.get(session, obj_id)
        obj.name = cultivar_name
        obj.category = category
    with Session.begin() as session:
        for model in ('seeds', 'plant', 'cultivar'):
            if obj_id := ids[model]:
                return None, None, f"details?{model}id={obj_id}"
    return None, None, ''

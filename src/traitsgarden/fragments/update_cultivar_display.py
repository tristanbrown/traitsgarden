from sqlalchemy import select
from dash import dcc, html, callback, register_page
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.shared import dropdown_options_input

def cultivar_update_display(obj_id=None):
    if obj_id is None:
        index = 'add'
        objname = category = None
    else:
        index = 'rename'
        with Session.begin() as session:
            obj = Cultivar.get(session, obj_id)
            objname = obj.name
            category = obj.category
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(f"{index.capitalize()} Cultivar")),
        dbc.ModalBody([
            dbc.Row(dbc.Col(dbc.Input(
                id={'type': 'cultivar-input', 'index': index},
                placeholder='Cultivar Name', value=objname))),
            dbc.Row(dbc.Col(dcc.Dropdown(
                id={'type': 'category-dropdown', 'index': index},
                placeholder="Category", value=category)))
            ]),
        dbc.ModalFooter([
                dcc.Location(id={'type': 'cultivar-link', 'index': index}, refresh=True),
                dbc.Button("Save", id={'type': 'save-cultivar', 'index': index}),
                ])
    ], id={'type': 'update-cultivar-modal', 'index': index})

@callback(
    Output({'type': 'update-cultivar-modal', 'index': MATCH}, "is_open"),
    [Input({'type': 'update-cultivar-open', 'index': MATCH}, "n_clicks"),
    Input({'type': 'save-cultivar', 'index': MATCH}, "n_clicks")],
    [State({'type': 'update-cultivar-modal', 'index': MATCH}, "is_open")],
)
def toggle_updatecultivar_dialogue(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

@callback(
    Output({'type': 'category-dropdown', 'index': MATCH}, "options"),
    Input({'type': 'category-dropdown', 'index': MATCH}, "search_value"),
    Input({'type': 'category-dropdown', 'index': MATCH}, "value"),
)
@dropdown_options_input
def update_category_options(search_value, input_value):
    stmt = select(Cultivar.category).where(
        Cultivar.category.ilike(f'%{search_value}%')
    ).distinct().order_by(Cultivar.category)
    with Session.begin() as session:
        result = session.execute(stmt).scalars().all()
    return result

@callback(
    Output({'type': 'category-dropdown', 'index': 'add'}, 'value'),
    Output({'type': 'cultivar-input', 'index': 'add'}, 'value'),
    Output({'type': 'cultivar-link', 'index': 'add'}, 'href'),
    Input({'type': 'save-cultivar', 'index': 'add'}, 'n_clicks'),
    State({'type': 'cultivar-input', 'index': 'add'}, 'value'),
    State({'type': 'category-dropdown', 'index': 'add'}, 'value'),
    prevent_initial_call=True,
)
def save_add_cultivar(n_clicks, cultivar_name, category):
    with Session.begin() as session:
        obj = Cultivar.add(session, cultivar_name, category)
    with Session.begin() as session:
        obj = Cultivar.query(session, cultivar_name, category)
        if obj:
            return None, None, f"details?cultivarid={obj.id}"
    return None, None, ''

@callback(
    Output({'type': 'category-dropdown', 'index': 'rename'}, 'value'),
    Output({'type': 'cultivar-input', 'index': 'rename'}, 'value'),
    Output({'type': 'cultivar-link', 'index': 'rename'}, 'href'),
    Input({'type': 'save-cultivar', 'index': 'rename'}, 'n_clicks'),
    State('ids', 'data'),
    State({'type': 'cultivar-input', 'index': 'rename'}, 'value'),
    State({'type': 'category-dropdown', 'index': 'rename'}, 'value'),
    prevent_initial_call=True,
)
def save_rename_cultivar(n_clicks, ids, cultivar_name, category):
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

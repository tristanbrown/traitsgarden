from sqlalchemy import select
from dash import dcc, html, callback, ctx, register_page, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.search import update_search_ids

def display_dropdown_ids(category, name, model, current_id):
    cultivar = f"{category} | {name}"
    search_ids = update_search_ids(None, cultivar, model)
    return html.Div([
        dcc.Dropdown(id="ids-dropdown", value=current_id, options=search_ids,
            clearable=False, searchable=False),
        dcc.Location(id='ids-dropdown-link', refresh=True),
    ])

@callback(
    Output('ids-dropdown-link', 'href'),
    State('ids', 'data'),
    Input('ids-dropdown', 'value'),
    prevent_initial_call=True,
)
def new_id_go(all_ids, new_id):
    with Session.begin() as session:
        cultivar = Cultivar.get(session, all_ids['cultivar'])
        category, name = (cultivar.category, cultivar.name)
    for model in (Seeds, Plant):
        modelname = model.__name__.lower()
        if old_id := all_ids[modelname]:
            break
    with Session.begin() as session:
        obj = model.query(session, name, category, new_id)
        if int(old_id) != obj.id:
            return f"details?{modelname}id={obj.id}"
    raise PreventUpdate

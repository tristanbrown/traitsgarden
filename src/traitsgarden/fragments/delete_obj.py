from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar

models = {'cultivar': Cultivar, 'seeds': Seeds, 'plant': Plant}

del_display = dbc.Modal([
    dcc.Store(id='obj-to-delete', data={'model': None, 'id': None}),
    dbc.ModalHeader(dbc.ModalTitle(id="delete-title")),
    dbc.ModalBody("Are you sure you want to delete this object?"),
    dbc.ModalFooter([
            dcc.Location(id='delete-destination', refresh=True),
            dbc.Button("Delete", id="confirm-delete"),
            dbc.Button("Cancel", id="cancel-delete"),
            ])
], id="delete-obj-modal")

@callback(
    Output("delete-title", 'children'),
    Output('obj-to-delete', 'data'),
    Input("delete-cultivar-open", "n_clicks"),
    Input("delete-entity-open", "n_clicks"),
    State('ids', 'data'),
    prevent_initial_call=True,
)
def choose_obj_to_delete(cultivar_click, other_click, ids):
    if cultivar_click:
        model = 'cultivar'
    elif other_click:
        if ids['seeds']:
            model = 'seeds'
        elif ids['plant']:
            model = 'plant'
        else:
            model = 'cultivar'
    title = f"Delete {model.capitalize()}"
    del_ids = {'model': model, 'id': ids[model]}
    return title, del_ids

@callback(
    Output("delete-obj-modal", "is_open"),
    [Input("delete-cultivar-open", "n_clicks"),
    Input("delete-entity-open", "n_clicks"),
    Input("confirm-delete", "n_clicks"),
    Input("cancel-delete", "n_clicks")],
    [State("delete-obj-modal", "is_open")],
)
def toggle_delete_modal(n_open1, n_open2, n_confirm, n_cancel, is_open):
    if any([n_open1, n_open2, n_confirm, n_cancel]):
        return not is_open
    return is_open

@callback(
    Output('delete-destination', 'href'),
    Input('confirm-delete', 'n_clicks'),
    State('obj-to-delete', 'data'),
    prevent_initial_call=True,
)
def delete_obj(n_clicks, obj_data):
    with Session.begin() as session:
        obj = models[obj_data['model']].get(session, obj_data['id'])
        if obj:
            obj.delete(session)
            return f"/traitsgarden/table?name={obj_data['model']}"
    return ''

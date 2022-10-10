from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar

models = {'cultivar': Cultivar, 'seeds': Seeds, 'plant': Plant}

def del_display(model, id):
    return dbc.Modal([
        dcc.Store(id='obj-to-delete', data={'model': model, 'id': id}),
        dbc.ModalHeader(dbc.ModalTitle(f"Delete {model.capitalize()}")),
        dbc.ModalBody("Are you sure you want to delete this object?"),
        dbc.ModalFooter([
                dcc.Location(id='delete-destination', refresh=True),
                dbc.Button("Delete", id="confirm-delete"),
                dbc.Button("Cancel", id="cancel-delete"),
                ])
    ], id="delete-obj-modal")

@callback(
    Output("delete-obj-modal", "is_open"),
    [Input("delete-cultivar-open", "n_clicks"),
    Input("confirm-delete", "n_clicks"),
    Input("cancel-delete", "n_clicks")],
    [State("delete-obj-modal", "is_open")],
)
def toggle_delete_modal(n_open, n_confirm, n_cancel, is_open):
    if any([n_open, n_confirm, n_cancel]):
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

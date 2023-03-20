from dash import dcc, html, callback
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar

models = {'cultivar': Cultivar, 'seeds': Seeds, 'plant': Plant}

def del_display(objname):
    index = f"delete-{objname}"
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(f"Delete {objname.capitalize()}")),
        dbc.ModalBody("Are you sure you want to delete this object?"),
        dbc.ModalFooter([
                dcc.Location(id={'type': 'save-redirect', 'index': index}, refresh=True),
                dbc.Button("Confirm Delete", id={'type': 'save-dialogue', 'index': index}),
                ])
    ], id={'type': 'dialogue', 'index': index})

def get_delete_callback(objname):
    @callback(
        Output({'type': 'save-redirect', 'index': f'delete-{objname}'}, 'href'),
        Input({'type': 'save-dialogue', 'index': f'delete-{objname}'}, 'n_clicks'),
        State('ids', 'data'),
        prevent_initial_call=True,
    )
    def delete_obj(n_clicks, ids):
        obj_id = ids[objname]
        with Session.begin() as session:
            obj = models[objname].get(session, obj_id)
            if obj:
                obj.delete(session)
                return f"table?name={objname}"
        return ''
    return delete_obj

delete_cultivar = get_delete_callback('cultivar')
delete_seeds = get_delete_callback('seeds')
delete_plant = get_delete_callback('plant')

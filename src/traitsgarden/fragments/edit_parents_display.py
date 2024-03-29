from sqlalchemy import select
from dash import dcc, html, callback, ctx
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar


def edit_parents_modal(name, category, pkt_id):
    index = f"edit-parents"
    if name and category:
        cultivar = f"{name}|{category}"
    else:
        cultivar = None
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(f"Edit Seeds Parents")),
        dcc.Store(id='seedparent-store'),
        dbc.ModalBody(id={'type': 'dialogue-body', 'index': index}),
        dbc.ModalBody([
            dcc.Dropdown(id={'type': 'cultivar-select', 'index': index},
                placeholder="Cultivar", value=cultivar),
            dcc.Dropdown(id={'type': 'plantid-dropdown', 'index': index},
                placeholder="Plant ID"),
            ]),
        dbc.ModalFooter([
                dcc.Location(id={'type': 'save-redirect', 'index': index}, refresh=True),
                dbc.Button("Save", id={'type': 'save-dialogue', 'index': index}),
                ])
    ], id={'type': 'dialogue', 'index': index})


def init_parents_store(seeds_id):
    """Get the parents data from the database and Store it."""
    with Session.begin() as session:
        obj = Seeds.get(session, seeds_id)
        parent_objs = obj.get_parents(session)
        parent_names = {
            label: {
                parent.id: parent.__repr__() for parent in parent_group
            }
            for label, parent_group in parent_objs.items()
        }
    return parent_names


@callback(
    Output('seedparent-store', 'data'),
    Input({'type': 'open-dialogue', 'index': 'edit-parents'}, 'n_clicks'),
    Input({'type': 'delete-parent', 'index': ALL}, 'n_clicks'),
    Input({'type': 'add-parent', 'index': ALL}, 'n_clicks'),
    State({'type': 'cultivar-select', 'index': 'edit-parents'}, "value"),
    State({'type': 'plantid-dropdown', 'index': 'edit-parents'}, "value"),
    State('ids', 'data'),
    State('seedparent-store', 'data'),
    prevent_initial_call=True,
)
def update_seedparent_store(
        open_click,
        del_click,
        add_click,
        cultivar,
        plant_id,
        ids,
        parent_names
        ):
    """Updates the temporary Store of seed parents data."""

    button_id = ctx.triggered_id
    any_clicks = any(ctx.inputs.values())

    if button_id['type'] == 'open-dialogue':
        parent_names = init_parents_store(ids['seeds'])
    elif button_id['type'] == 'delete-parent' and any_clicks:
        parent_type, parent_id = button_id['index'].split('=')
        parent_names[parent_type].pop(parent_id, None)
    elif button_id['type'] == 'add-parent' and any_clicks:
        parent_type = button_id['index']
        name, category = cultivar.split("|")
        with Session.begin() as session:
            parent = Plant.query(session, name, category, plant_id)
            parent_names[parent_type][parent.id] = parent.__repr__()
    return parent_names


@callback(
    Output({'type': 'dialogue-body', 'index': "edit-parents"}, 'children'),
    Input({'type': 'open-dialogue', 'index': "edit-parents"}, 'n_clicks'),
    Input('seedparent-store', 'data'),
    prevent_initial_call=True,
)
def get_parent_boxes(open_clicks, parent_names):
    """"""
    parent_boxes = {}
    for label, parent_group in parent_names.items():
        parent_boxes[label] = [
            dbc.InputGroup([
                dbc.Button(
                    "X",
                    id={'type': 'delete-parent', 'index': f"{label}={id}"},
                    n_clicks=0),
                dbc.InputGroupText(name)
            ], size='sm')
            for id, name in parent_group.items()
        ] + [
            dbc.InputGroup(
                dbc.Button(
                    "+",
                    id={'type': 'add-parent', 'index': label},
                    n_clicks=0),
                size='sm')
            ]
    deletable_parents = [
        "Mothers:",
        html.Br(),
        *parent_boxes['mothers'],
        html.Br(),
        "Fathers:",
        html.Br(),
        *parent_boxes['fathers'],
    ]
    return deletable_parents

@callback(
    Output({'type': 'save-redirect', 'index': "edit-parents"}, 'href'),
    Input({'type': 'save-dialogue', 'index': "edit-parents"}, 'n_clicks'),
    State('ids', 'data'),
    State('seedparent-store', 'data'),
    prevent_initial_call=True,
)
def save_stored_parents(n_clicks, ids, parent_names):
    parent_ids = {
        label: [int(val) for val in vals.keys()]
        for label, vals in parent_names.items()
    }
    with Session.begin() as session:
        obj = Seeds.get(session, ids['seeds'])
        obj.update_parents(session, parent_ids)
    return f"details?seedsid={ids['seeds']}"

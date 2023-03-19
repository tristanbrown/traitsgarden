from sqlalchemy import select
from dash import dcc, html, callback, ctx
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar
from traitsgarden.db.query import query_orm
from traitsgarden.fragments.shared import dropdown_options_input

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
    State('ids', 'data'),
    State('seedparent-store', 'data'),
    prevent_initial_call=True,
)
def update_seedparent_store(open_click, del_click, ids, parent_names):
    button_id = ctx.triggered_id
    print(button_id)
    any_clicks = any(ctx.inputs.values())
    if button_id['type'] == 'open-dialogue':
        parent_names = init_parents_store(ids['seeds'])
    elif button_id['type'] == 'delete-parent' and any_clicks:
        del_parent_type, del_parent_id = button_id['index'].split('=')
        parent_names[del_parent_type].pop(del_parent_id, None)
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

# @callback(
#     Output({'type': 'dialogue', 'index': MATCH}, "is_open"),
#     [Input({'type': 'open-dialogue', 'index': MATCH}, "n_clicks"),
#     Input({'type': 'save-dialogue', 'index': MATCH}, "n_clicks")],
#     [State({'type': 'dialogue', 'index': MATCH}, "is_open")],
# )
# def toggle_dialogue(n_open, n_close, is_open):
#     if n_open or n_close:
#         return not is_open
#     return is_open

# @callback(
#     Output({'type': 'cultivar_select', 'index': MATCH}, "options"),
#     Input({'type': 'cultivar_select', 'index': MATCH}, "search_value"),
#     Input({'type': 'cultivar_select', 'index': MATCH}, "value"),
# )
# def update_cultivar_options(search_value, input_value):
#     if not search_value:
#         search_value = ''
#     stmt = select(Cultivar.name, Cultivar.category).where(
#         Cultivar.name.ilike(f'%{search_value}%')
#     ).distinct().order_by(Cultivar.name)
#     with Session.begin() as session:
#         result = session.execute(stmt)
#     return [{'label': f"{name} ({cat})", 'value': f"{name}|{cat}"} \
#         for name, cat in result]

# @callback(
#     Output({'type': 'cultivar_select', 'index': MATCH}, 'value'),
#     Output({'type': 'basic-input', 'index': MATCH}, 'value'),
#     Output({'type': 'save-redirect', 'index': MATCH}, 'href'),
#     Input({'type': 'save-dialogue', 'index': MATCH}, 'n_clicks'),
#     State({'type': 'save-dialogue', 'index': MATCH}, 'id'),
#     State({'type': 'basic-input', 'index': MATCH}, 'value'),
#     State({'type': 'cultivar_select', 'index': MATCH}, 'value'),
#     prevent_initial_call=True,
# )
# def save_changes(n_clicks, index, obj_id, cultivar):
#     objtype = index['index'].split('-')[-1]
#     models = {'seeds': Seeds, 'plant': Plant}
#     model = models[objtype]
#     name, category = cultivar.split('|')
#     with Session.begin() as session:
#         obj = model.add(session, name, category, obj_id)
#         if objtype == 'seeds':
#             obj_id = obj.pkt_id
#         elif objtype == 'plant':
#             obj_id = obj.plant_id
#     with Session.begin() as session:
#         obj = model.query(session, name, category, obj_id)
#         if obj:
#             return None, None, f"details?{objtype}id={obj.id}"
#     return None, None, ''

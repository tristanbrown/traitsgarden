"""Shared functions and wrappers between fragments."""

from sqlalchemy import select
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from traitsgarden.db.connect import Session
from traitsgarden.db.models import Plant, Seeds, Cultivar

## Dialogues

@callback(
    Output({'type': 'dialogue', 'index': MATCH}, "is_open"),
    [Input({'type': 'open-dialogue', 'index': MATCH}, "n_clicks"),
    Input({'type': 'save-dialogue', 'index': MATCH}, "n_clicks")],
    [State({'type': 'dialogue', 'index': MATCH}, "is_open")],
)
def toggle_dialogue(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

## Dropdown Options

def dropdown_options_input(get_options):
    """From an iterable, generate dropdown menu options,
    including custom input values.
    """
    def wrapper(search_value, input_value):
        if not search_value:
            search_value = ''
        result = get_options(search_value, input_value)
        options = list(result)
        if search_value:  ## Include the user input
            options = [search_value] + options
        if input_value:  ## Keep the input after selected
            options = [input_value] + options
        return options
    return wrapper

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
    Output({'type': 'cultivar-select', 'index': MATCH}, "options"),
    Input({'type': 'cultivar-select', 'index': MATCH}, "search_value"),
    Input({'type': 'cultivar-select', 'index': MATCH}, "value"),
)
def update_cultivar_options(search_value, input_value):
    if not search_value:
        search_value = ''
    stmt = select(Cultivar.name, Cultivar.category).where(
        Cultivar.name.ilike(f'%{search_value}%')
    ).distinct().order_by(Cultivar.name)
    with Session.begin() as session:
        result = session.execute(stmt)
    return [{'label': f"{name} ({cat})", 'value': f"{name}|{cat}"} \
        for name, cat in result]

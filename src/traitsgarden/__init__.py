"""Set up Flask app"""
import os
from dash import Dash, html, dcc, page_container, register_page, page_registry

from traitsgarden.settings import Config
from traitsgarden.db.connect import Session, connect_db
# from traitsgarden.pages import index


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)
server = app.server
server.config.from_object(Config())

register_page("another_home", layout=html.Div("We're home!"), path="/")
register_page(
    "very_important", layout=html.Div("Don't miss it!"), path="/important", order=0
)

## Initial layout
app.layout = html.Div(
    [
        html.H1("App Frame"),
        html.Div(
            [
                html.Div(
                    dcc.Link(f"{page['name']} - {page['path']}", href=page["path"])
                )
                for page in page_registry.values()
                if page["module"] != "pages.not_found_404"
            ]
        ),
        page_container,
    ]
)


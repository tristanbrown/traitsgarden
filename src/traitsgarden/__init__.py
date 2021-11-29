"""Set up Flask app"""
import dash

from .settings import Config

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
server.config.from_object(Config())
app.config.suppress_callback_exceptions = True
